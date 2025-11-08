"""
Security middleware for SkillBridge
Provides XSS protection, rate limiting, and security monitoring
"""

import re
import logging
from django.http import HttpResponseForbidden, HttpResponse
from django.core.cache import cache
from django.conf import settings
from .security import AuditLog

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """
    Enhanced security middleware for XSS protection and suspicious request detection
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Patterns for detecting suspicious requests
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'union\s+select',
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*update\s+.*\s+set',
            r'--\s*$',  # SQL comment
            r'/\*.*\*/',  # SQL comment block
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'eval\s*\(',
            r'document\.cookie',
            r'document\.location',
            r'window\.location',
        ]

    def __call__(self, request):
        # Check for suspicious content
        if self._contains_suspicious_content(request):
            ip = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            AuditLog.log_security_event(
                'SUSPICIOUS_REQUEST_BLOCKED',
                getattr(request, 'user', None),
                'Suspicious request pattern detected',
                ip_address=ip,
                user_agent=user_agent[:200],  # Limit length
                extra_data={'path': request.path, 'method': request.method}
            )

            return HttpResponseForbidden('Suspicious request detected')

        # Add security headers
        response = self.get_response(request)
        self._add_security_headers(response)

        return response

    def _contains_suspicious_content(self, request):
        """Check request for suspicious patterns"""
        # Check URL path
        if self._matches_patterns(request.path):
            return True

        # Check query parameters
        for key, values in request.GET.lists():
            for value in values:
                if self._matches_patterns(str(value)):
                    return True

        # Check POST data (avoid logging sensitive data)
        if request.method == 'POST' and hasattr(request, 'POST'):
            for key, values in request.POST.lists():
                # Skip sensitive fields
                if key.lower() in ['password', 'token', 'secret', 'key']:
                    continue
                for value in values:
                    if self._matches_patterns(str(value)):
                        return True

        # Check headers (avoid common legitimate headers)
        suspicious_headers = ['X-Forwarded-For', 'X-Real-IP']
        for header_name in suspicious_headers:
            header_value = request.META.get(f'HTTP_{header_name.upper().replace("-", "_")}')
            if header_value and self._matches_patterns(header_value):
                return True

        return False

    def _matches_patterns(self, text):
        """Check if text matches any suspicious patterns"""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
                return True
        return False

    def _add_security_headers(self, response):
        """Add security headers to response"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent abuse
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_client_ip(request)
        user = getattr(request, 'user', None)

        # Different limits for authenticated vs anonymous users
        if user and user.is_authenticated:
            limit = 1000  # requests per hour for authenticated users
            window = 3600  # 1 hour
        else:
            limit = 100   # requests per hour for anonymous users
            window = 3600  # 1 hour

        # Create cache key
        cache_key = f'rate_limit_{ip}_{user.id if user and user.is_authenticated else "anon"}'

        # Check current request count
        request_count = cache.get(cache_key, 0)

        if request_count >= limit:
            AuditLog.log_security_event(
                'RATE_LIMIT_EXCEEDED',
                user,
                f'Rate limit exceeded: {request_count}/{limit}',
                ip_address=ip,
                extra_data={'path': request.path, 'method': request.method}
            )

            return HttpResponse(
                'Rate limit exceeded. Please try again later.',
                status=429,
                content_type='text/plain'
            )

        # Increment counter
        cache.set(cache_key, request_count + 1, window)

        response = self.get_response(request)

        # Add rate limit headers
        remaining = limit - (request_count + 1)
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(max(0, remaining))
        response['X-RateLimit-Reset'] = str(window)

        return response

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditMiddleware:
    """
    Middleware for auditing sensitive operations
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Operations that should be audited
        self.audit_endpoints = [
            '/api/v1/auth/login/',
            '/api/v1/auth/register/',
            '/api/v1/users/profile/',
            '/api/v1/admin/',
        ]

    def __call__(self, request):
        # Log sensitive operations
        if self._should_audit(request):
            ip = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            AuditLog.log_security_event(
                'API_ACCESS',
                getattr(request, 'user', None),
                f'Accessed {request.method} {request.path}',
                ip_address=ip,
                user_agent=user_agent[:200],
                extra_data={
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                }
            )

        response = self.get_response(request)

        # Log failed authentication attempts
        if (request.path in ['/api/v1/auth/login/'] and
            response.status_code in [400, 401]):
            AuditLog.log_authentication_event(
                'login',
                getattr(request, 'user', None),
                success=False,
                ip_address=self._get_client_ip(request),
                details='Invalid credentials'
            )

        return response

    def _should_audit(self, request):
        """Determine if request should be audited"""
        path = request.path
        return any(audit_path in path for audit_path in self.audit_endpoints)

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
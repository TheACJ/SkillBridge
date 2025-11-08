"""
Security utilities for SkillBridge backend
Provides input sanitization, data encryption, and security helpers
"""

import os
import re
import html
import base64
import logging
from typing import Optional, Dict, Any
from bleach import clean
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Security utilities for input validation and sanitization"""

    @staticmethod
    def sanitize_html(content: str, allow_basic_tags: bool = True) -> str:
        """
        Sanitize HTML content to prevent XSS attacks

        Args:
            content: HTML content to sanitize
            allow_basic_tags: Whether to allow basic formatting tags

        Returns:
            Sanitized HTML content
        """
        if not content:
            return ""

        if allow_basic_tags:
            allowed_tags = ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'a', 'ul', 'ol', 'li', 'blockquote']
            allowed_attrs = {
                'a': ['href', 'title', 'target'],
                '*': ['class']
            }
        else:
            allowed_tags = []
            allowed_attrs = {}

        return clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize plain text input by escaping HTML entities

        Args:
            text: Plain text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return ""
        return html.escape(text.strip())

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format using regex

        Args:
            email: Email address to validate

        Returns:
            True if valid format, False otherwise
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    @staticmethod
    def contains_suspicious_patterns(text: str) -> bool:
        """
        Check for suspicious patterns that might indicate attacks

        Args:
            text: Text to check

        Returns:
            True if suspicious patterns found
        """
        suspicious_patterns = [
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
        ]

        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
                logger.warning(f"Suspicious pattern detected: {pattern}")
                return True
        return False

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength

        Args:
            password: Password to validate

        Returns:
            Dict with validation results and suggestions
        """
        result = {
            'is_valid': True,
            'score': 0,
            'issues': [],
            'suggestions': []
        }

        if len(password) < 8:
            result['issues'].append('Password must be at least 8 characters long')
            result['suggestions'].append('Use at least 8 characters')
            result['is_valid'] = False

        if not re.search(r'[A-Z]', password):
            result['issues'].append('Password must contain at least one uppercase letter')
            result['suggestions'].append('Include uppercase letters (A-Z)')

        if not re.search(r'[a-z]', password):
            result['issues'].append('Password must contain at least one lowercase letter')
            result['suggestions'].append('Include lowercase letters (a-z)')

        if not re.search(r'\d', password):
            result['issues'].append('Password must contain at least one number')
            result['suggestions'].append('Include numbers (0-9)')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['issues'].append('Password must contain at least one special character')
            result['suggestions'].append('Include special characters (!@#$%^&*)')

        # Calculate score
        checks = [
            len(password) >= 8,
            bool(re.search(r'[A-Z]', password)),
            bool(re.search(r'[a-z]', password)),
            bool(re.search(r'\d', password)),
            bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            len(password) >= 12,  # Bonus for longer passwords
        ]

        result['score'] = sum(checks)

        return result


class DataEncryption:
    """Data encryption utilities using Fernet (AES)"""

    def __init__(self):
        key = getattr(settings, 'ENCRYPTION_KEY', None) or os.getenv('ENCRYPTION_KEY')
        if not key:
            # Generate a key if none exists (for development)
            key = base64.urlsafe_b64encode(os.urandom(32)).decode()
            logger.warning("Using auto-generated encryption key. Set ENCRYPTION_KEY in production!")

        try:
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise

    def encrypt(self, data: str) -> str:
        """
        Encrypt string data

        Args:
            data: String to encrypt

        Returns:
            Encrypted data as base64 string
        """
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data

        Args:
            encrypted_data: Base64 encrypted string

        Returns:
            Decrypted string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except (InvalidToken, Exception) as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Invalid encrypted data")


class AuditLog:
    """Audit logging utilities"""

    @staticmethod
    def log_security_event(
        event_type: str,
        user=None,
        details: str = "",
        ip_address: str = None,
        user_agent: str = None,
        extra_data: Dict[str, Any] = None
    ) -> None:
        """
        Log security-related events

        Args:
            event_type: Type of security event
            user: User associated with the event
            details: Event details
            ip_address: IP address of the request
            user_agent: User agent string
            extra_data: Additional data to log
        """
        audit_logger = logging.getLogger('audit')

        log_data = {
            'event_type': event_type,
            'user_id': user.id if user else None,
            'user_email': user.email if user else 'Anonymous',
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': None,  # Will be added by logging formatter
        }

        if extra_data:
            log_data.update(extra_data)

        audit_logger.info(f"SECURITY_EVENT: {event_type}", extra=log_data)

    @staticmethod
    def log_authentication_event(
        event_type: str,
        user=None,
        success: bool = True,
        ip_address: str = None,
        details: str = ""
    ) -> None:
        """
        Log authentication events

        Args:
            event_type: Type of auth event (login, logout, failed_login, etc.)
            user: User attempting authentication
            success: Whether authentication was successful
            ip_address: IP address of the request
            details: Additional details
        """
        status = "SUCCESS" if success else "FAILED"
        AuditLog.log_security_event(
            f"AUTH_{event_type.upper()}_{status}",
            user=user,
            details=details,
            ip_address=ip_address
        )

    @staticmethod
    def log_data_access(
        operation: str,
        user,
        resource_type: str,
        resource_id: str = None,
        ip_address: str = None
    ) -> None:
        """
        Log data access events

        Args:
            operation: CRUD operation (create, read, update, delete)
            user: User performing the operation
            resource_type: Type of resource being accessed
            resource_id: ID of the resource
            ip_address: IP address of the request
        """
        details = f"{operation.upper()} {resource_type}"
        if resource_id:
            details += f" (ID: {resource_id})"

        AuditLog.log_security_event(
            f"DATA_ACCESS_{operation.upper()}",
            user=user,
            details=details,
            ip_address=ip_address
        )


# Global instances
security_utils = SecurityUtils()
data_encryption = DataEncryption()
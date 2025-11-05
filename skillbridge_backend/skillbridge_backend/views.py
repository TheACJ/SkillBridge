"""
Health check and monitoring views for the SkillBridge backend.
"""

import psutil
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.conf import settings
from django.db import connection
from django.core.cache import cache
import redis
import time


@require_GET
def health_check(request):
    """
    Comprehensive health check endpoint for monitoring system status.
    Returns JSON with health status of all critical components.
    """
    health_data = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('VERSION', '1.0.0'),
        'environment': getattr(settings, 'DJANGO_ENV', 'development'),
        'checks': {}
    }

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_data['checks']['database'] = {'status': 'healthy', 'message': 'Database connection OK'}
    except Exception as e:
        health_data['checks']['database'] = {'status': 'unhealthy', 'message': str(e)}
        health_data['status'] = 'unhealthy'

    # Redis/Cache check
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_data['checks']['cache'] = {'status': 'healthy', 'message': 'Cache connection OK'}
        else:
            health_data['checks']['cache'] = {'status': 'unhealthy', 'message': 'Cache write/read failed'}
            health_data['status'] = 'unhealthy'
    except Exception as e:
        health_data['checks']['cache'] = {'status': 'unhealthy', 'message': str(e)}
        health_data['status'] = 'unhealthy'

    # System resources check
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)

        health_data['checks']['system'] = {
            'status': 'healthy',
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'cpu_percent': cpu_percent,
            'message': f'Memory: {memory.percent}%, Disk: {disk.percent}%, CPU: {cpu_percent}%'
        }

        # Mark unhealthy if resources are critically low
        if memory.percent > 95 or disk.percent > 95 or cpu_percent > 95:
            health_data['checks']['system']['status'] = 'warning'
            if health_data['status'] == 'healthy':
                health_data['status'] = 'warning'

    except Exception as e:
        health_data['checks']['system'] = {'status': 'unhealthy', 'message': str(e)}
        health_data['status'] = 'unhealthy'

    # External services check (optional)
    external_checks = {}

    # OpenAI check (if configured)
    if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = settings.OPENAI_API_KEY
            # Simple test - just check if API key is valid format
            if openai.api_key and len(openai.api_key) > 20:
                external_checks['openai'] = {'status': 'healthy', 'message': 'API key configured'}
            else:
                external_checks['openai'] = {'status': 'unhealthy', 'message': 'Invalid API key'}
        except Exception as e:
            external_checks['openai'] = {'status': 'unhealthy', 'message': str(e)}

    # GitHub check (if configured)
    if hasattr(settings, 'GITHUB_ACCESS_TOKEN') and settings.GITHUB_ACCESS_TOKEN:
        try:
            from github import Github
            g = Github(settings.GITHUB_ACCESS_TOKEN)
            user = g.get_user()
            external_checks['github'] = {'status': 'healthy', 'message': f'Connected as {user.login}'}
        except Exception as e:
            external_checks['github'] = {'status': 'unhealthy', 'message': str(e)}

    if external_checks:
        health_data['checks']['external_services'] = external_checks

    # Set HTTP status code based on overall health
    status_code = 200
    if health_data['status'] == 'unhealthy':
        status_code = 503  # Service Unavailable
    elif health_data['status'] == 'warning':
        status_code = 200  # Still OK but with warnings

    return JsonResponse(health_data, status=status_code)


@require_GET
@cache_page(300)  # Cache for 5 minutes
def api_status(request):
    """
    Lightweight API status endpoint for load balancers and monitoring tools.
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'SkillBridge API',
        'version': getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('VERSION', '1.0.0'),
        'timestamp': time.time()
    })


@require_GET
def system_info(request):
    """
    Detailed system information for debugging and monitoring.
    Only available in DEBUG mode or with proper authentication.
    """
    if not settings.DEBUG:
        # In production, require authentication
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None

        info = {
            'system': {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': cpu_percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'disk_percent': disk.percent,
                'load_average': load_avg,
            },
            'django': {
                'debug': settings.DEBUG,
                'environment': getattr(settings, 'DJANGO_ENV', 'unknown'),
                'database_engine': settings.DATABASES['default']['ENGINE'],
                'cache_backend': settings.CACHES['default']['BACKEND'],
                'installed_apps_count': len(settings.INSTALLED_APPS),
            },
            'python': {
                'version': f"{psutil.python_version_tuple()[0]}.{psutil.python_version_tuple()[1]}.{psutil.python_version_tuple()[2]}",
                'implementation': psutil.python_implementation(),
            }
        }

        return JsonResponse(info)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
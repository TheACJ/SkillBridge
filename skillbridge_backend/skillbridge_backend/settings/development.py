"""
Development settings for skillbridge_backend project.
"""

from .base import *

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'django', 'testserver']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging - more verbose in development
if 'LOGGING' in globals():
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    LOGGING['loggers']['skillbridge_backend']['level'] = 'DEBUG'

# CORS - allow all in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable throttling in development for easier testing
if 'REST_FRAMEWORK' in globals():
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'anon': '1000/hour',
        'user': '10000/hour',
    }

# Disable authentication in development for easier testing
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = []

# Add debug toolbar if installed
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass
import os
from utils.logging import SafeFileHandler

# Get environment setting
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')

# Base logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    }
}

# Add file logging only in development environment
if ENVIRONMENT == 'development':
    LOGGING['handlers']['file'] = {
        '()': 'utils.logging.SafeFileHandler',
        'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        'formatter': 'verbose',
        'mode': 'a',
    }
    LOGGING['root']['handlers'].append('file')
    LOGGING['loggers']['django']['handlers'].append('file') 
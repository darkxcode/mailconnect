from utils.logging import SafeFileHandler

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            '()': 'utils.logging.SafeFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        // other handlers...
    },
    // rest of logging config...
} 
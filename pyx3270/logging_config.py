LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'emulator_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'x3270_emulator.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'default',
        },
        'server_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'x3270_server.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'default',
        },
        'offline_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'x3270_offline.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'default',
        },
    },
    'loggers': {
        'pyx3270.emulator': {
            'level': 'DEBUG',
            'handlers': ['emulator_file'],
            'propagate': False,
        },
        'pyx3270.server': {
            'level': 'DEBUG',
            'handlers': ['server_file'],
            'propagate': False,
        },
        'pyx3270.offline': {
            'level': 'DEBUG',
            'handlers': ['offline_file'],
            'propagate': False,
        },
    },
}

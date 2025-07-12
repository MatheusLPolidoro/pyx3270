import logging.config

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
    },
    'loggers': {
        'x3270_emulator': {
            'level': 'DEBUG',
            'handlers': ['emulator_file'],
            'propagate': False,
        },
        'x3270_server': {
            'level': 'DEBUG',
            'handlers': ['server_file'],
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
emulator_logger = logging.getLogger('x3270_emulator')
server_logger = logging.getLogger('x3270_server')

import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv('TTT_API_TOKEN')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': LOG_LEVEL,
            'propagate': True
        },
    }
}
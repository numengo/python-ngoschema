
SIMPLE_SETTINGS = {
    'OVERRIDE_BY_ENV': True,
    'CONFIGURE_LOGGING': True,
    'DYNAMIC_SETTINGS': {
        'backend': 'redis',
        'pattern': 'DYNAMIC_*',
        'auto_casting': True,
        'prefix': 'NGOSCHEMA_'
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(levelname)s %(asctime)s.%(msecs)03d %(name)s %(funcName)s: %(message)s',
            'datefmt': '%I:%M:%S'
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'verbose': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(levelname) -10s %(asctime)s %(name) -35s %(funcName) -30s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'stream': 'ext://sys.stdout',  # Default is stderr
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': 'INFO'
        },
    }
}

# resolver
URI_ID = '$id'
CURRENT_DRAFT = 'draft-05'
MS_DOMAIN = 'http://numengo.org'
MS_URI = f'{MS_DOMAIN}/ngoschema/{CURRENT_DRAFT}'

# utils.str_utils
PPRINT_MAX_EL = 10
PPRINT_MAX_STRL = 80

DEFAULT_CDATA_KEY = '#text'

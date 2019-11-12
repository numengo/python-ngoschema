
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
MS_DOMAIN = 'http://numengo.org/'
MS_URI = f'{MS_DOMAIN}ngoschema/{CURRENT_DRAFT}'

# utils.str_utils
PPRINT_MAX_EL = 10
PPRINT_MAX_STRL = 80

DEFAULT_CDATA_KEY = '#text'

# additional types
import decimal
import datetime
import pathlib
import arrow
from past.builtins import basestring

string_types = (basestring, str)
datetime_types = (datetime.datetime, arrow.Arrow)

LITERALS_TYPE_CLASS_MAPPING = (
    ("integer", int),
    ("number", decimal.Decimal),
    ("boolean", bool),
    ("string", str),
    ("importable", str),
    ("path", pathlib.Path),
    ("datetime", datetime.datetime),
    ("date", datetime.date),
    ("time", datetime.time),
    ("null", None),
)

EXTRA_SCHEMA_TYPE_MAPPING = (
    ("importable", string_types),
    ("path", string_types + (pathlib.Path, )),
    ("date", string_types + datetime_types + (datetime.date, )),
    ("time", string_types + datetime_types + (datetime.time, )),
    ("datetime", string_types + datetime_types),
)

# format options
DATE_FORMATS = [
    "YYYY-MM-DD", "YYYY/MM/DD", "YYYY.MM.DD", "YYYY-MM", "YYYY/MM", "YYYY.MM"
]

ALT_DATE_FORMATS = [
    "DD-MM-YYYY",
    "DD/MM/YYYY",
    "DD.MM.YYYY",
    "MM-YYYY",
    "MM/YYYY",
    "MM.YYYY",
]

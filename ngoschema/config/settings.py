
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
            'format': u'%(levelname)s %(asctime)s.%(msecs)03d %(name)s %(funcName)s: %(message)s',
            'datefmt': '%I:%M:%S'
        },
        'standard': {
            'format': u'%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'verbose': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': u'%(levelname) -10s %(asctime)s %(name) -35s %(funcName) -30s: %(message)s'
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

DEFAULT_CONTEXT = {
    'True': True,
    'False': False,
    'None': None,
}

# resolver
URI_ID = '$id'
CURRENT_DRAFT = 'draft-06'
MS_DOMAIN = 'https://numengo.org/'
MS_URI = f'{MS_DOMAIN}ngoschema/{CURRENT_DRAFT}'
JSCH_URI = "https://json-schema.org/draft/2019-09/schema#"

DEFAULT_MS_URI = MS_URI


# utils.str_utils
PPRINT_MAX_EL = 10
PPRINT_MAX_STRL = 40

DEFAULT_CDATA_KEY = '#text'
DEFAULT_PRIMITIVE_VALIDATE = True
DEFAULT_COLLECTION_VALIDATE = False
DEFAULT_COLLECTION_LAZY_LOADING = False
DEFAULT_COLLECTION_ATTRIBUTE_BY_NAME = False
ATTRIBUTE_NAME_FIELD = 'name'
DEFAULT_LOGGER_LEVEL = 'INFO'
DEFAULT_ADD_LOGGING = False
DEFAULT_ASSERT_ARGS = True

# additional types
import decimal
import datetime
import pathlib
import urllib.parse
import arrow
import six
import collections
from past.builtins import basestring


SCHEMA_REF_TYPE_MAPPING = (
    ('integer', int),
    ('number', decimal.Decimal),
    ('boolean', bool),
    ('string', str),
    ('importable', str),
    ('uri', urllib.parse.ParseResult),
    ('path', pathlib.Path),
    ('datetime', datetime.datetime),
    ('date', datetime.date),
    ('time', datetime.time),
    ('null', None),
)

SCHEMA_DEF_KEYS = ('type', 'extends', 'dependencies', 'aliases', 'negatedAliases', 'notSerialized', 'notValidated',
                   'default', 'required', 'readOnly', 'properties', 'patternProperties', 'additionalProperties',
                   'primaryKeys', '$defs', 'items', 'convert', 'validate', 'serialize')

string_types = (basestring, str)
datetime_types = string_types + (arrow.Arrow, datetime.datetime)

BOOLEAN_TRUE_STR_LIST = ['true']
BOOLEAN_FALSE_STR_LIST = ['false']

# reference type is last
EXTRA_SCHEMA_TYPE_MAPPING = (
    ('object', (dict, collections.OrderedDict, )),
    ('importable', string_types),
    ('number', six.integer_types + (float, decimal.Decimal)),
    ('uri',  string_types + (pathlib.Path, urllib.parse.ParseResult)),
    ('path', string_types + (urllib.parse.ParseResult, pathlib.Path)),
    ('date', datetime_types + (datetime.date, )),
    ('time', datetime_types + (datetime.time, )),
    ('datetime', datetime_types),
)

DATETIME_NOW_STRINGS = ['now']
DATE_TODAY_STRINGS = ['today']

# format options
DATE_FORMATS = [
    'YYYY-MM-DD', 'YYYY/MM/DD', 'YYYY.MM.DD', 'YYYY-MM', 'YYYY/MM', 'YYYY.MM'
]

ALT_DATE_FORMATS = [
    'DD-MM-YYYY',
    'DD/MM/YYYY',
    'DD.MM.YYYY',
    'MM-YYYY',
    'MM/YYYY',
    'MM.YYYY',
]

ALT_TIME_FORMATS = [
    'HH:mm:ss.SSSSSS ZZ',
    'HH:mm:ss.SSSSSS',
    'HH:mm:ss.SSS ZZ',
    'HH:mm:ss.SSS',
    'HH:mm:ssZZ',
    'HH:mm:ss ZZ',
    'HH:mm:ss',
    'HH:mm',
    'HH:mm:ss A',
    'HH:mm A',
]

DATETIME_FORMATS = {
    'ATOM': 'YYYY-MM-DD HH:mm:ssZZ',
    'COOKIE': 'dddd, DD-MMM-YYYY HH:mm:ss ZZZ',
    'RFC822': 'ddd, DD MMM YY HH:mm:ss Z',
    'RFC850': 'dddd, DD-MMM-YY HH:mm:ss ZZZ',
    'RFC1036': 'ddd, DD MMM YY HH:mm:ss Z',
    'RFC1123': 'ddd, DD MMM YYYY HH:mm:ss Z',
    'RFC2822': 'ddd, DD MMM YYYY HH:mm:ss Z',
    'RFC3339': 'YYYY-MM-DD HH:mm:ssZZ',
    'RSS': 'ddd, DD MMM YYYY HH:mm:ss Z',
    'W3C': 'YYYY-MM-DD HH:mm:ssZZ',
}

GETTER_PREFIX = 'get_'
SETTER_PREFIX = 'set_'
DELETER_PREFIX = 'del_'

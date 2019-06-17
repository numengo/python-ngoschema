# -*- coding: utf-8 -*-
from .jinja2 import templates_module_loader

from ngoschema.protocol_base import ProtocolBase
from .classbuilder import get_builder
from .resolver import DEFAULT_MS_URI
from .resolver import get_resolver
from .schema_metaclass import SchemaMetaclass
from .schemas_loader import load_module_schemas
from . import pjo_validators
from python_jsonschema_objects import ValidationError

load_module_schemas('ngoschema')
templates_module_loader.register('ngoschema')

from .metadata import Metadata

__all__ = [
    'DEFAULT_MS_URI',
    'get_resolver',
    'get_builder',
    'SchemaMetaclass',
    'ValidationError'
]

__author__ = "Cédric ROMAN"
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.2.2'"

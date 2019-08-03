# -*- coding: utf-8 -*-

__author__ = """Cedric ROMAN"""
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.2.2'"

from .resolver import DEFAULT_MS_URI, CURRENT_DRAFT
from .resolver import get_resolver
from .classbuilder import get_builder
from .schema_metaclass import SchemaMetaclass
from .protocol_base import ProtocolBase
from .jinja2 import load_module_templates
from .schemas_loader import load_module_schemas
from . import pjo_validators as validators
from python_jsonschema_objects import ValidationError

load_module_schemas('ngoschema')
load_module_templates('ngoschema')

# need schemas loaded first
from .object_transform import load_module_transforms
from .metadata import Metadata

__all__ = [
    'DEFAULT_MS_URI',
    'CURRENT_DRAFT',
    'get_resolver',
    'get_builder',
    'SchemaMetaclass',
    'ProtocolBase',
    'Metadata',
    'validators',
    'ValidationError',
    'load_module_schemas',
    'load_module_templates',
    'load_module_transforms'
]

# -*- coding: utf-8 -*-

__author__ = """Cedric ROMAN"""
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.2.2'"

from .schemas_loader import load_module_schemas, load_schema, load_schema_file
load_module_schemas('ngoschema')

from .utils import load_module_templates, templates_module_loader
from .utils import load_module_transforms, transforms_module_loader
from .utils import load_module_objects, objects_module_loader
load_module_templates('ngoschema')

from .resolver import DEFAULT_MS_URI, CURRENT_DRAFT
from .resolver import get_resolver
from .classbuilder import get_builder
from .schema_metaclass import SchemaMetaclass
from .protocol_base import ProtocolBase
from .protocol_base import DEFAULT_CDATA_KEY
from .query import Query
from python_jsonschema_objects import ValidationError


__all__ = [
    # schemas_loader
    'templates_module_loader',
    'load_module_templates',
    'transforms_module_loader',
    'load_module_transforms',
    'objects_module_loader',
    'load_module_objects',
    'load_schema',
    'load_schema_file',
    'load_module_schemas',
    'DEFAULT_MS_URI',
    'CURRENT_DRAFT',
    'DEFAULT_CDATA_KEY',
    'get_resolver',
    'get_builder',
    'SchemaMetaclass',
    'ProtocolBase',
    'validators',
    'ValidationError',
    'load_module_schemas',
    'Query'
]

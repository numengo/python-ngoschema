# -*- coding: utf-8 -*-

__author__ = """Cedric ROMAN"""
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.2.2'"

from .schemas_loader import load_module_schemas, load_schema, load_schema_file
load_module_schemas('ngoschema')

from .exceptions import InvalidOperationException, SchemaError, ValidationError

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
from .handlers import *
from .query import Query, Filter


__all__ = [
    # exceptions
    'SchemaError',
    'ValidationError',
    'InvalidOperationException',
    # loaders
    'templates_module_loader',
    'load_module_templates',
    'transforms_module_loader',
    'load_module_transforms',
    'objects_module_loader',
    'load_module_objects',
    'load_schema',
    'load_schema_file',
    'load_module_schemas',
    # infos
    'DEFAULT_MS_URI',
    'CURRENT_DRAFT',
    'DEFAULT_CDATA_KEY',
    # builder and protocol
    'get_resolver',
    'get_builder',
    'SchemaMetaclass',
    'ProtocolBase',
    # query
    'Query',
    'Filter',
    # handlers
    'MemoryObjectHandler',
    'FileObjectHandler',
    'JsonFileObjectHandler',
    'YamlFileObjectHandler',
    'XmlFileObjectHandler',
    'Jinja2FileObjectHandler',
    'Jinja2MacroFileObjectHandler',
    'Jinja2MacroTemplatedPathFileObjectHandler',
    'load_object_from_file',
    'serialize_object_to_file'
]

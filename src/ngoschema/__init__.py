# -*- coding: utf-8 -*-

__author__ = """Cedric ROMAN"""
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.2.2'"

from simple_settings import LazySettings

from .schemas_loader import load_module_schemas, load_schema, load_schema_file, get_schema_store_list
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
from ngoschema.utils import DEFAULT_CDATA_KEY
from .handlers import *
from .query import Query, Filter

settings = LazySettings('ngoschema.project_settings', 'NGOSCHEMA_.environ')

__all__ = [
    'settings',
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
    'get_schema_store_list',
    # infos
    'DEFAULT_MS_URI',
    'CURRENT_DRAFT',
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
    'load_json_from_file',
    'load_yaml_from_file',
    'load_xml_from_file',
    'serialize_object_to_file'
]

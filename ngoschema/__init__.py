# -*- coding: utf-8 -*-

__author__ = """Cedric ROMAN"""
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.3.0'"

# load settings
from simple_settings import LazySettings
settings = LazySettings('ngoschema.config.settings', 'NGOSCHEMA_.environ')

from .utils import Context

DEFAULT_CONTEXT = Context(**{
    'True': True,
    'False': False,
    'None': None,
})

APP_CONTEXT = DEFAULT_CONTEXT.create_child(settings)

from .utils import register_module
register_module('ngoschema')

from .exceptions import InvalidOperation, SchemaError, ValidationError
from .types import *
from .repositories import *
from .query import Query, Filter

__all__ = [
    'settings',
    # exceptions
    'SchemaError',
    'ValidationError',
    'InvalidOperation',
    # loaders
    'register_module',
    # builder and protocol
    'NamespaceManager',
    'TypeBuilder',
    'Type',
    'with_metaclass',
    'ObjectMetaclass',
    # literals
    # query
    'Query',
    'Filter',
    # repository
    'repository_registry',
    'MemoryRepository',
    'FileRepository',
    'JsonFileRepository',
    'YamlFileRepository',
    'XmlFileRepository',
    'load_object_from_file',
    'load_json_from_file',
    'load_yaml_from_file',
    'load_xml_from_file',
    'serialize_object_to_file',
]

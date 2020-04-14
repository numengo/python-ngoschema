# -*- coding: utf-8 -*-

__author__ = """Cedric ROMAN"""
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.3.0'"

# load settings
from simple_settings import LazySettings
settings = LazySettings('ngoschema.config.settings', 'NGOSCHEMA_.environ')

# add additional types
import itertools
from python_jsonschema_objects import validators
validators.SCHEMA_TYPE_MAPPING = tuple(itertools.chain(validators.SCHEMA_TYPE_MAPPING, settings.EXTRA_SCHEMA_TYPE_MAPPING))

from .utils import register_module
register_module('ngoschema')

from .exceptions import InvalidOperationException, SchemaError, ValidationError
from .resolver import get_resolver
from .classbuilder import get_builder
from .schema_metaclass import SchemaMetaclass
from .protocol_base import ProtocolBase
from .repositories import *
from .query import Query, Filter
from .literals import LiteralValue, TextField, ImportableField, IntegerField
from .wrapper_types import ArrayWrapper

__all__ = [
    'settings',
    # exceptions
    'SchemaError',
    'ValidationError',
    'InvalidOperationException',
    # loaders
    'register_module',
    # builder and protocol
    'get_resolver',
    'get_builder',
    'with_metaclass',
    'SchemaMetaclass',
    'ProtocolBase',
    # literals
    'LiteralValue',
    'TextField',
    'ImportableField',
    'IntegerField',
    # arrays
    'ArrayWrapper',
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

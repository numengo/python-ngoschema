# -*- coding: utf-8 -*-

__author__ = """Cedric ROMAN"""
__email__ = "roman@numengo.com"
__version__ = "__version__ = '1.0.5'"

# load settings
from simple_settings import LazySettings
settings = LazySettings('ngoschema.config.settings')

# register module and load schemas
from .loaders import register_module
register_module('ngoschema')

# create a default context
#from .contexts import Context

#DEFAULT_CONTEXT = Context(**settings.DEFAULT_CONTEXT)
#APP_CONTEXT = DEFAULT_CONTEXT.create_child(settings)

from .exceptions import InvalidOperation, SchemaError, ValidationError
from .managers import *
from .protocols import *
from .repositories import *
from .query import Query, Filter
from .registries import serializers_registry, transformers_registry, repositories_registry


__all__ = [
    'settings',
    # exceptions
    'SchemaError',
    'ValidationError',
    'InvalidOperation',
    # loaders
    'register_module',
    # builder and protocol
    'TypeBuilder',
    'type_builder',
    'NamespaceManager',
    'with_metaclass',
    'SchemaMetaclass',
    # literals
    # query
    'Query',
    'Filter',
    # repository
    'repositories_registry',
]

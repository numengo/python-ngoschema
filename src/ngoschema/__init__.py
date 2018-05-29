# -*- coding: utf-8 -*-
from .exceptions import (SchemaError, InvalidValue)
from ._classbuilder import ProtocolBase
from ._schemas import SchemaMetaclass

from .resolver import DEFAULT_MS_URI, DEFAULT_DEFS_URI, get_resolver
from .schemas_loader import load_module_schemas
from pyrsistent import pmap
MS_STORE = pmap(load_module_schemas())

__all__ = ['MS_STORE', 'DEFAULT_MS_URI', 'DEFAULT_DEFS_URI', 'get_resolver', 'ProtocolBase', 'SchemaMetaclass']

__author__ = 'Cédric ROMAN'
__email__ = 'roman@numengo.com'
__version__ = '0.1.0'


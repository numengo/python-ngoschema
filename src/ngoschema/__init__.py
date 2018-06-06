# -*- coding: utf-8 -*-
from pyrsistent import pmap

from .classbuilder import ProtocolBase
from .resolver import DEFAULT_DEFS_URI
from .resolver import DEFAULT_MS_URI
from .resolver import get_resolver
from .schema_metaclass import SchemaMetaclass
from .schemas_loader import load_module_schemas

MS_STORE = pmap(load_module_schemas())

__all__ = [
    "MS_STORE",
    "DEFAULT_MS_URI",
    "DEFAULT_DEFS_URI",
    "get_resolver",
    "ProtocolBase",
    "SchemaMetaclass",
]

__author__ = "Cédric ROMAN"
__email__ = "roman@numengo.com"
__version__ = "0.1.0"

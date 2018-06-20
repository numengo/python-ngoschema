# -*- coding: utf-8 -*-
from .schemas_loader import load_module_schemas
load_module_schemas('ngoschema')

from .classbuilder import ProtocolBase
from .resolver import DEFAULT_MS_URI
from .resolver import get_resolver
from .schema_metaclass import SchemaMetaclass

__all__ = [
    "DEFAULT_MS_URI",
    "get_resolver",
    "ProtocolBase",
    "SchemaMetaclass",
]

__author__ = "Cédric ROMAN"
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.2.0'"

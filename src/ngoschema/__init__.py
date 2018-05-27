# -*- coding: utf-8 -*-
#from . import _apipkg
#from ._schemas_old import *
from .exceptions import (SchemaError, InvalidValue)
#from .schemas_loader import (load_schema, load_schema_file, load_module_schemas)
#from ngoschema.doc_rest_parser import parse_docstring

#from ngoschema.exceptions import (SchemaError, InvalidValue)
#from ngoschema.schemas_loader import load_module_schemas
#from ngoschema.doc_rest_parser import parse_docstring

#from ngoschema.resolver import ExpandingResolver, get_resolver


from .resolver import DEFAULT_MS_URI, DEFAULT_DEFS_URI, get_resolver
from .schemas_loader import load_module_schemas
from pyrsistent import pmap
MS_STORE = pmap(load_module_schemas())

__all__ = ['MS_STORE', 'DEFAULT_MS_URI', 'DEFAULT_DEFS_URI', 'get_resolver']

__author__ = 'Cédric ROMAN'
__email__ = 'roman@numengo.com'
__version__ = '0.5.0'


# *- coding: utf-8 -*-
"""
Base class for metadata (inherited by all components normally)

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import weakref

from future.utils import with_metaclass

from . import utils
from .mixins import HasParent, HasCanonicalName
from .protocol_base import ProtocolBase
from .wrapper_types import ArrayWrapper
from .schema_metaclass import SchemaMetaclass
from .foreign_key import ForeignKey
from .canonical_name import CN_KEY


class NamedObject(with_metaclass(SchemaMetaclass, HasCanonicalName, ProtocolBase)):
    """
    Class to deal with metadata and parents/children relationships
    """
    __schema__ = "http://numengo.org/draft-05/schema#/definitions/NamedObject"

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, *args, **kwargs)

    def set_name(self, value):
        HasCanonicalName.set_name(self, value)

    def set_canonicalName(self, value):
        HasCanonicalName.set_canonicalName(self, value)

    def get_canonicalName(self):
        return self._cname


class Metadata(with_metaclass(SchemaMetaclass, NamedObject)):
    """
    Class to deal with metadata and parents/children relationships
    """
    __schema__ = "http://numengo.org/draft-05/schema#/definitions/Metadata"

    def __init__(self, *args, **kwargs):
        NamedObject.__init__(self, *args, **kwargs)

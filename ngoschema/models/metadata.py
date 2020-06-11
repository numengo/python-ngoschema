# *- coding: utf-8 -*-
"""
Foreign key component

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 28/01/2019
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from future.utils import with_metaclass
import sys
import weakref

from .. import settings
from ..decorators import classproperty, depend_on_prop
from ..resolver import UriResolver, resolve_uri
from ..types import ObjectMetaclass, ObjectProtocol
from ..types.foreign_key import Ref, ForeignKey
from ..types.type_builder import TypeBuilder, scope

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class NamedObject(with_metaclass(ObjectMetaclass)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _schema_id = "https://numengo.org/ngoschema/draft-06#/$defs/NamedObject"

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.canonicalName}>'

    @property
    def _parent_named(self):
        return next((m for m in self._context.maps_flattened if isinstance(m, NamedObject) and m is not self), None)

    @depend_on_prop('name')
    def get_canonicalName(self):
        p = self._parent_named
        return f'{p.canonicalName}.{self.name}' if p is not None else self.name


class ObjectMetadata(with_metaclass(ObjectMetaclass)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _schema_id = "https://numengo.org/ngoschema/draft-06#/$defs/ObjectMetadata"

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
from ..types import ObjectMetaclass, ObjectProtocol

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class NamedObject(with_metaclass(ObjectMetaclass)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _schema_id = "https://numengo.org/ngoschema#/$defs/NamedObject"

    def __str__(self):
        if self._str is None:
            cn = self.canonicalName
            a = ([cn] if cn else [])+ [f'{k}={str(self._validated_data[k] or self._data[k])}' for k in self._required]
            self._str = '<%s %s>' % (self.qualname(), ' '.join(a))
        return self._str

    def _make_context(self, context=None, *extra_contexts):
        ObjectProtocol._make_context(self, context, *extra_contexts)
        self._set_validated_data('_parent_named', next((m for m in self._context.maps_flattened if isinstance(m, NamedObject) and m is not self), None))

    @depend_on_prop('name')
    def get_canonicalName(self):
        p = self._parent_named
        return f'{p.canonicalName}.{self.name}' if p is not None and p.canonicalName else self.name


class ObjectMetadata(with_metaclass(ObjectMetaclass)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _schema_id = "https://numengo.org/ngoschema#/$defs/ObjectMetadata"

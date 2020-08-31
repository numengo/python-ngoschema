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
from ..protocols import ObjectMetaclass, ObjectProtocol

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class NamedObject(with_metaclass(ObjectMetaclass)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _id = "https://numengo.org/ngoschema#/$defs/NamedObject"
    _id = "https://numengo.org/ngoschema2#/$defs/metadata/$defs/NamedObject"
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/NamedObject"

    def __str__(self):
        if self._str is None:
            cn = self.canonicalName
            a = ([cn] if cn else []) + [f'{k}={str(self._data_validated[k] or self._data[k])}' for k in self._required]
            self._str = '<%s %s>' % (self.qualname(), ' '.join(a))
        return self._str

    def _make_context(self, context=None, *extra_contexts):
        ObjectProtocol._make_context(self, context, *extra_contexts)
        self._set_data_validated('_parentNamed', next((m for m in self._context.maps if isinstance(m, NamedObject) and m is not self), None))

    @depend_on_prop('name')
    def get_canonicalName(self):
        p = self._parentNamed
        pcn = p.canonicalName if p else None
        n = self.name
        return f'{pcn}.{n}' if pcn else n


class Metadata(with_metaclass(ObjectMetaclass)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _id = "https://numengo.org/ngoschema#/$defs/ObjectMetadata"
    _id = "https://numengo.org/ngoschema2#/$defs/metadata/$defs/Metadata"
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/Metadata"

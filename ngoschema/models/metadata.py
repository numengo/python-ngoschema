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
from ..protocols import SchemaMetaclass, ObjectProtocol

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class Annotation(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/Annotation"


class IdentifiedObject(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/IdentifiedObject"


class Metadata(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/Metadata"


class NamedObject(with_metaclass(SchemaMetaclass)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/NamedObject"

    def __str__(self):
        if self._str is None:
            cn = self._canonicalName
            a = ([cn] if cn else []) + [f'{k}={str(self._data_validated[k] or self._data[k])}' for k in self._required]
            self._str = '<%s %s>' % (self.qualname(), ' '.join(a))
        return self._str

    def set_context(self, context=None, *extra_contexts):
        ObjectProtocol.set_context(self, context, *extra_contexts)
        ctx = self._context
        self._set_data_validated('_parentNamed', next((m for m in ctx.maps if isinstance(m, NamedObject) and m is not self), None))

    @property
    def _canonicalName(self):
        # one that does not trigger lazyloading
        pn = self._data_validated.get('_parentNamed')
        pn = pn if pn is not self else None
        n = self._data_validated.get('name') or self._data.get('name')
        return f'{pn._canonicalName}.{n}' if pn else n

    @depend_on_prop('name', '_parentNamed')
    def get_canonicalName(self):
        return self._canonicalName
    #    p = self._parentNamed
    #    pcn = p.canonicalName if p else None
    #    n = self._data_validated.get('name') or self._data.get('name')
    #    n = self.name
    #    return f'{pcn}.{n}' if pcn else n


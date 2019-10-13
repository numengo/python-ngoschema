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

from ngoschema import SchemaMetaclass, ProtocolBase
from ngoschema.mixins import HasCanonicalName

from .protocol_base import ProtocolBase
from .schema_metaclass import SchemaMetaclass

from .decorators import classproperty


class KeyedObject(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    __schema__ = "http://numengo.org/draft-05/schema#/definitions/KeyedObject"

    @classproperty
    def _primaryKeys(cls):
        return cls.propinfo('primaryKeys')

    _keys = None
    @property
    def fkeys(self):
        if self._keys is None:
            self._keys = (self.get(k) for k in self._primaryKeys)
        return self._keys

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, *args, **kwargs)


class NamedObject(with_metaclass(SchemaMetaclass, HasCanonicalName, KeyedObject)):
    """
    Class to deal with metadata and parents/children relationships
    """
    __schema__ = "http://numengo.org/draft-05/schema#/definitions/NamedObject"

    def __init__(self, *args, **kwargs):
        HasCanonicalName.__init__(self)
        KeyedObject.__init__(self, *args, **kwargs)

    @classproperty
    def _primaryKeys(cls):
        return cls.propinfo('primaryKeys') or ['canonicalName']

    def set_name(self, value):
        HasCanonicalName.set_name(self, value)

    def get_canonicalName(self):
        return self._get_prop_value('canonicalName') or self._cname

    #def set_canonicalName(self, value):
    #    value = value.replace('-', '_')
    #    cn = str(value) if value else None
    #    self._cname = cn
    #    self._set_prop_value('canonicalName', cn)

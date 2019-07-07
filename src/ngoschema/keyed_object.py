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

from .protocol_base import ProtocolBase
from .schema_metaclass import SchemaMetaclass

from .decorators import classproperty


class KeyedObject(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    __schema__ = "http://numengo.org/draft-05/schema#/definitions/KeyedObject"

    @classproperty
    def primaryKeys(cls):
        return cls.propinfo('primaryKeys') or ['canonicalName']

    __registry = None
    @classproperty
    def _registry(cls):
        if cls.__registry is None:
            cls.__registry = weakref.WeakValueDictionary()
        return cls.__registry

    def register(self):
        self._registry[tuple(self[k].for_json() for k in self.primaryKeys)] = self

    @classmethod
    def resolve_by_keys(self, keys):
        try:
            return self._registry.get(keys)
        except Exception as er:
            raise ValueError("Impossible to resolve foreign instance '%s' with keys %s.\n%s" % (self.__class__, keys, sys.exc_info()[2]))

    _keys = None
    @property
    def keys(self):
        if self._keys is None:
            self._keys = (self.get(k) for k in self.primaryKeys)
        return self._keys

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, *args, **kwargs)

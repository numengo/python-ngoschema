# *- coding: utf-8 -*-
"""
Base class for loading objects from files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import Mapping
import six
import weakref

from ngoschema.utils import Registry, is_sequence
from ngoschema import ProtocolBase

class ObjectRegistry(Registry):
    _class = ProtocolBase
    _keys = None

    def __init__(self, object_class = None, keys=None):
        Registry.__init__(self)
        self._keys = tuple(keys) if is_sequence(keys) else None
        if object_class is not None:
            self._class = object_class
        # use alternate naming
        self._identity_map = self._registry

    def identity_key(self, instance_key):
        if instance_key in self._identity_map:
            return instance_key
        return self._identity_key(instance_key)

    def _identity_key(self, instance):
        if not isinstance(instance, self._class):
            raise Exception("%r is not an instance of %r" % (instance, self._class))
        return tuple([instance.get_prop_value(k) for k in self._keys]) if self._keys else id(instance)

    def register(self, key, instance):
        if not isinstance(instance, self._class):
            raise Exception("%r is not an instance of %r" % (instance, self._class))
        self._identity_map[key] = instance
        return instance

    def add(self, instance):
        self._identity_map[self.identity_key(instance)] = instance
        return instance

    def remove(self, instance):
        del self._identity_map[self.identity_key(instance)]

    def unregister(self, key):
        del self._identity_map[key]


class ObjectWeakRegistry(ObjectRegistry):

    def __init__(self, object_class = None, keys=None):
        ObjectRegistry.__init__(self, object_class, keys)
        self._identity_map = self._registry = weakref.WeakValueDictionary()

    def __getitem__(self, key):
        # callv weak reference
        return self._identity_map[key]()

    def add(self, instance):
        key = self.identity_key(instance)
        def _remove_key(registry, key):
            if key in registry._identity_map:
                del registry._identity_map[key]
        weakref.finalize(instance, _remove_key, self, key)
        self._identity_map[key] = instance


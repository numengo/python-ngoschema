# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import defaultdict
from operator import neg

from ..utils import ReadOnlyChainMap as ChainMap
from ..protocols import Deserializer, Serializer
from .type import Type
from .constants import _True


class CollectionDeserializer(Deserializer):
    _collType = None
    _many = True
    _dependencies = {}

    def __init__(self, collType=None, dependencies=None, **opts):
        Deserializer.__init__(self, **opts)
        self._collType = collType or self._collType
        self._dependencies = defaultdict(list, dependencies or {})

    @staticmethod
    def _call_order(self, value, **opts):
        pass

    @classmethod
    def call_order(cls, value, **opts):
        return cls._call_order(cls, value, **opts)


class CollectionSerializer(Serializer, CollectionDeserializer):
    _many = True
    _deserializer = CollectionDeserializer

    def __init__(self, **opts):
        #CollectionDeserializer.__init__(self, **opts)
        Serializer.__init__(self, **opts)

    @staticmethod
    def _print_order(self, value, **opts):
        pass

    @classmethod
    def print_order(cls, value, **opts):
        return cls._print_order(cls, value, **opts)


class Collection(Type, CollectionSerializer):
    _items = _True
    _notValidated = set()
    _notSerialized = set()
    _serializer = CollectionSerializer

    _items_type_cache = None

    def __init__(self, items=None, notValidated=None, notSerialized=None, **opts):
        self._notValidated.update(notValidated or [])
        self._notSerialized.update(notSerialized or [])
        #CollectionSerializer.__init__(self, **opts)
        Type.__init__(self, **opts)
        self._items = items or self._items

    @staticmethod
    def _check(self, value, items=True, **opts):
        #value = value if isinstance(value, self._collType) else Type._check(self, value, **opts)
        value = self._deserializer._check(self, value, **opts)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    v = value[k]
                    if v is not None:
                        value[k] = t._check(t, value[k], **opts)
        return value

    @staticmethod
    def _deserialize(self, value, evaluate=True, items=False, **opts):
        value = self._collType(value or self._default)
        ret = self._deserializer._deserialize(self, value, items=items, evaluate=False, **opts)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    ret[k] = t._deserialize(t, value[k], evaluate=evaluate, **opts)
        return self._evaluate(self, ret, items=False, **opts) if evaluate else ret

    #@staticmethod
    #def _call_order(self, value, items=False, **opts):
    #    value = set(value).difference(self._notValidated)
    #    return self._deserializer._call_order(self, value, **opts)

    #@staticmethod
    #def _print_order(self, value, excludes=[], **opts):
    #    """Generate a print order according to schema and inherited schemas properties order
    #    and additonal properties detected in values. """
    #    excludes = list(self._notSerialized.union(excludes))
    #    return self._deserializer._call_order(self, value, excludes=excludes, **opts)

    @staticmethod
    def _convert(self, value, items=True, **opts):
        value = self._collType(value)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    value[k] = t._convert(t, value[k], **opts)
        value = self._deserializer._convert(self, value, **opts)
        return value

    @staticmethod
    def _validate(self, value, items=True, **opts):
        value = self._deserializer._validate(self, value, **opts)
        if items:
            value = self._collType(value)  # make a copy to avoid modifying original object
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    value[k] = t._validate(t, value[k], **opts)
        return value

    @staticmethod
    def _evaluate(self, value, convert=True, validate=True, items=True, **opts):
        value = Type._evaluate(self, value, convert=convert, validate=False, **opts)
        if items:
            for k in self._call_order(self, value, **opts):
                if self._is_included(k, value, **opts):
                    t = self._items_type(self, k)
                    value[k] = t._evaluate(t, value[k], convert=False, validate=validate, **opts)
        return Type._evaluate(self, value, convert=False, validate=validate, **opts)

    @staticmethod
    def _serialize(self, value, items=True, **opts):
        ret = self._serializer._serialize(self, value, **opts)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    v = value[k]
                    ret[k] = t._serialize(t, v, **opts)
            #ret = self.default(value, items=False, **opts)
            #for k in self.print_order(value, **opts):
            #    t = self._items_type(self, k)
            #    ret[k] = t._serialize(t, value[k], deserialize=deserialize, **opts) if items else value[k]
        return ret
        #return self._collType(Type._serialize(self, ret, deserialize=False, **opts))

    @classmethod
    def items_types(cls, value, **opts):
        # _items_types is defined in the collection implementation class
        return cls._items_types(cls, value, **opts)

    @classmethod
    def items_type(cls, item):
        # _items_types is defined in the collection implementation class
        return cls._items_type(cls, item)

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import defaultdict
from operator import neg

from ..exceptions import InvalidValue, ValidationError
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
        self._dependencies = defaultdict(list, dependencies or self._dependencies)

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
        Type.__init__(self, **opts)
        self._items = items or self._items

    @staticmethod
    def _check(self, value, items=False, **opts):
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
        ret = self._deserializer._deserialize(self, value or self._default, items=items, evaluate=False, **opts)
        #ret = self._collType(ret)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    ret[k] = t._deserialize(t, value[k], evaluate=evaluate, **opts)
        return self._evaluate(self, ret, items=False, **opts) if evaluate else ret

    @staticmethod
    def _convert(self, value, items=True, no_defaults=True, **opts):
        value = self._collType(value)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, no_defaults=no_defaults, **opts):
                    value[k] = t._convert(t, value[k], **opts)
        value = CollectionSerializer._convert(self, value, **opts)
        return value

    @staticmethod
    def _validate(self, value, items=True, no_defaults=True, **opts):
        value = CollectionSerializer._validate(self, value, **opts)
        if items:
            ret = self.null(value, **opts)
            for k in self._call_order(self, value, **opts):
                if self._is_included(k, value, no_defaults=no_defaults, **opts):
                    t = self._items_type(self, k)
                    try:
                        ret[k] = t._validate(t, value[k], items=True, no_defaults=no_defaults, **opts)
                    except Exception as er:
                        msg = f"Errpr while validating item '{k}' of type {t} in {self.__class__}: {str(er)}"
                        raise ValidationError(msg)
            #for k, t in self._items_types(self, value):
            #    if self._is_included(k, value, no_defaults=no_defaults, **opts):
            #        ret[k] = t._validate(t, value[k], items=True, no_defaults=no_defaults, **opts)
            value = ret  # make a copy to avoid modifying original object
        return value

    @staticmethod
    def _evaluate(self, value, convert=True, validate=True, items=True, **opts):
        value = Type._evaluate(self, value, convert=convert, validate=False, **opts)
        if items:
            for k in self._call_order(self, value, **opts):
                if self._is_included(k, value, **opts):
                    t = self._items_type(self, k)
                    try:
                        value[k] = t._evaluate(t, value[k], convert=False, validate=validate, **opts)
                    except Exception as er:
                        msg = f"Errpr while evaluating item '{k}' of type {t} in {self.__class__}: {str(er)}"
                        raise InvalidValue(msg)
        return Type._evaluate(self, value, convert=False, validate=validate, **opts)

    @staticmethod
    def _serialize(self, value, items=True, only=[], excludes=[], **opts):
        opts.setdefault('no_defaults', True)
        value = CollectionSerializer._serialize(self, value, only=only, excludes=excludes, **opts)
        if items:
            #ret = self.null(value, only=only, excludes=excludes) # not opts because it sometimes triggers no_defaults
            ret = self.null(value, only=only, excludes=excludes, **opts)
            for k, t in self._items_types(self, ret):
                if self._is_included(k, value, only=only, excludes=excludes, **opts):
                    v = value[k]
                    t_excludes = set(getattr(t, '_notSerialized', [])).union(excludes)
                    ret[k] = t._serialize(t, v, excludes=t_excludes, **opts)
                    #ret[k] = v.do_serialize(**opts) if hasattr(v, 'do_serialize') else t._serialize(t, v, **opts)
        else:
            ret = self._collType(value)
        return ret

    @classmethod
    def items_types(cls, value, **opts):
        # _items_types is defined in the collection implementation class
        return cls._items_types(cls, value, **opts)

    @classmethod
    def items_type(cls, item):
        # _items_types is defined in the collection implementation class
        return cls._items_type(cls, item)

    @classmethod
    def null(cls, value, **opts):
        # _null is defined in the collection implementation class
        return cls._null(cls, value, **opts)

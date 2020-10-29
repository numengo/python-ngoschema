# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from abc import abstractmethod
from operator import neg

from ..exceptions import InvalidValue, InvalidOperation
from ..decorators import assert_arg
from ..managers.type_builder import DefaultValidator
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from .. import settings
from ..types.strings import Pattern, Expr
from ..types.collection import Collection
from ..types.uri import PathFile, PathFileExists
from ..types.object import Object
from ..contexts import InstanceContext
from .type_protocol import TypeProtocol

#COLLECTION_VALIDATE = settings.DEFAULT_COLLECTION_VALIDATE
LAZY_LOADING = settings.DEFAULT_COLLECTION_LAZY_LOADING


class CollectionProtocol(Collection):
    _lazyLoading = LAZY_LOADING
    _collection = None
    #_validate = COLLECTION_VALIDATE

    _data = None
    _data_validated = None
    _items_inputs = None
    _items_type_cache = None
    _repr = None
    _str = None

    def __init__(self, value=None, lazyLoading=None, items=None, validate=True, **opts):
        self._lazyLoading = lazyLoading if lazyLoading is not None else self._lazyLoading
        lz = self._lazyLoading if items is None else not items
        #Collection.__init__(self, **opts)
        value = opts if value is None else value  # to allow initialization by keywords
        self._data = self._deserialize(self, value, items=False, evaluate=False, convert=False, **opts)
        # touch allocates storage for data, need to call _create_context again
        self._touch()
        self.set_context(opts)
        if not lz:
            self._collType(self)
        if validate:
            self._validate(self, self, items=False)

    @staticmethod
    def _create_context(self, *extra_contexts, **local):
        return Collection._create_context(self, {'this': self}, *extra_contexts, **local)

    #@staticmethod
    #def _call_order(self, value, excludes=[], **opts):
    #    #excludes = list(self._notValidated.union(excludes))
    #    return Collection._call_order(self, value, excludes=excludes, **opts)

    @staticmethod
    def _convert(self, value, excludes=[], **opts):
        excludes = list(self._notValidated.union(excludes))
        if self._lazyLoading:
            opts.setdefault('items', False)
        return self._collection._convert(self, value, excludes=excludes, **opts)

    @staticmethod
    def _deserialize(self, value, items=False, **opts):
        return self._collection._deserialize(self, value, items=items, **opts)

    @staticmethod
    def _validate(self, value, items=False, excludes=[], **opts):
        excludes = list(self._notValidated.union(excludes))
        return self._collection._validate(self, value, items=items, excludes=excludes, **opts)

    @staticmethod
    def _evaluate(self, value, excludes=[], **opts):
        excludes = list(self._notValidated.union(excludes))
        if self._lazyLoading:
            opts.setdefault('items', False)
        return self._collection._evaluate(self, value, excludes=excludes, **opts)

    #def print_order(self, **opts):
    #    return self._print_order(self, self._data, **opts)

    #@staticmethod
    #def _print_order(self, value, excludes=[], **opts):
    #    excludes = list(self._notSerialized.union(excludes))
    #    return self._serializer._print_order(self, value, excludes=excludes, **opts)

    @staticmethod
    def _serialize(self, value, excludes=[], **opts):
        excludes = list(self._notSerialized.union(excludes))
        return self._collection._serialize(self, value, excludes=excludes, **opts)

    def _touch(self):
        self._repr = None
        self._str = None

    def _items_touch(self, item):
        CollectionProtocol._touch(self)
        self._data_validated[item] = None
        self._items_inputs[item] = {}
        for d, s in self._dependencies.items():
            if item in s:
                self._items_touch(d)

    def _items_inputs_evaluate(self, item):
        ret = {}
        t = self._items_type(self, item)
        for k in t._inputs(t, self._data[item]):
            try:
                ret[k] = self[k]
            except Exception as er:
                self._logger.error(er, exc_info=True)
                pass
        return ret

    def _items_evaluate(self, item, **opts):
        v = self._data[item]
        t = self._items_type(self, item)
        opts.setdefault('context', self._context)
        if hasattr(t, '_lazyLoading'):
            if t._lazyLoading:
                opts.setdefault('validate', False)
        if t.is_primitive():
            opts['serialize'] = False
        try:
            ret = t(v, **opts)
            return ret
        except Exception as er:
            raise er
        return t._evaluate(t, v, **opts)

    @classmethod
    def items_serialize(cls, value, item, **opts):
        v = value[item]
        t = cls._items_type(cls, item)
        ctx = getattr(value, '_context', cls._context)
        opts.setdefault('context', ctx)
        return t._serialize(t, v, **opts)

    def __setitem__(self, item, value):
        self._data[item] = value
        if not self._lazyLoading:
            self._items_inputs[item] = self._items_inputs_evaluate(item)
            self._set_data_validated(item, self._items_evaluate(item))

    def __getitem__(self, item):
        if self._data_validated[item] is None:
            self._items_inputs[item] = self._items_inputs_evaluate(item)
            self._set_data_validated(item, self._items_evaluate(item))
        return self._data_validated[item]

    def __delitem__(self, index):
        del self._data[index]
        del self._data_validated[index]
        del self._items_inputs[index]
        self._validate(items=False)

    def _set_data(self, item, value):
        t = self._items_type(self, item)
        orig = self._data[item]
        # to avoid comparison of objects (often equality which is the longest to validate), only touch for changed primitives
        if t.is_primitive():
            if value != orig:
                self._items_touch(item)
        else:
            self._items_touch(item)
        self._data[item] = value

    def _set_data_validated(self, item, value):
        t = self._items_type(self, item)
        if t.is_primitive():
            orig = self._data[item]
            if not Pattern.check(orig) and not Expr.check(orig):
                self._data[item] = value
        else:
            self._data[item] = value
        self._data_validated[item] = value

    def _is_outdated(self, item):
        return (self._data_validated[item] is None and self._data[item] is not None
                ) or (self._items_inputs.get(item, []) != self._items_inputs_evaluate(item))

    @classmethod
    def create(cls, value=None, **opts):
        return cls(value, **opts)

    def do_validate(self, **opts):
        return self._validate(self, self, **opts)

    def do_serialize(self, **opts):
        return self._serialize(self, self, deserialize=False, **opts)

    def copy(self):
        return self.create(self._data, context=self._context)

    def __eq__(self, other):
        if other is None:
            return False
        if other is self:
            return True
        if not self.check(other):
            return False
        if len(self) != len(other):
            return False
        for i, v in enumerate(other):
            if self[i] != v:
                return False
        return True

    def __hash__(self):
        return hash(tuple(self._id, tuple((k, hash(v)) for k, v in enumerate(self._data_validated))))


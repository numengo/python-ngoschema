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

LAZY_LOADING = settings.DEFAULT_COLLECTION_LAZY_LOADING


class CollectionProtocol(Collection):
    _lazyLoading = LAZY_LOADING
    _collection = None
    #_validate = COLLECTION_VALIDATE

    _data = None
    _dataValidated = None
    _itemsInputs = None
    _items_type_cache = None
    _repr = None
    _str = None
    #_session = None

    def __init__(self, value=None, lazyLoading=None, items=None, validate=True, context=None, session=None, **opts):
        self._lazyLoading = lazyLoading if lazyLoading is not None else self._lazyLoading
        lz = self._lazyLoading if items is None else not items
        #Collection.__init__(self, **opts)
        if value is None:
            # to allow initialization by keywords
            value = opts
            opts = {}
        self._data = self._deserialize(self, value, items=False, evaluate=False, **opts)  #, convert=False, **opts)
        # touch allocates storage for data, need to call _create_context again
        self._touch()
        ctx = self._create_context(self, context=context)
        self.set_context(ctx, session=session, **opts)
        if not lz:
            self._collType(self)
        if validate:
            self._validate(self, self, items=False, context=ctx)

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
        opts.setdefault('context', self._context)
        return self._collection._validate(self, value, items=items, excludes=excludes, **opts)

    @staticmethod
    def _evaluate(self, value, excludes=[], **opts):
        excludes = list(self._notValidated.union(excludes))
        if self._lazyLoading:
            opts.setdefault('items', False)
        if isinstance(value, self._pyType):
            if opts.get('validate'):
                self._validate(self, value, excludes=excludes, **opts)
            return value
        return self._collection._evaluate(self, value, excludes=excludes, **opts)

    @staticmethod
    def _serialize(self, value, excludes=[], **opts):
        excludes = list(self._notSerialized.union(excludes))
        return self._collection._serialize(self, value, excludes=excludes, **opts)

    def _touch(self):
        self._repr = None
        self._str = None

    def _items_touch(self, item):
        CollectionProtocol._touch(self)
        self._dataValidated[item] = None
        self._itemsInputs[item] = {}
        for d, s in self._dependencies.items():
            if item in s:
                self._items_touch(d)

    def _items_inputs_evaluate(self, item):
        ret = {}
        t = self._items_type(self, item)
        # treat dependencies
        for k in self._dependencies.get(item, []):
            try:
                ret[k] = self[k]
            except Exception as er:
                self._logger.error(er, exc_info=True)
        # treat data
        if t.is_primitive() and not t._rawLiterals:
            for k in t._inputs(t, self._data[item]):
                try:
                    ret[k] = self[k]
                except Exception as er:
                    self._logger.error(er, exc_info=True)
        return ret

    def _items_evaluate(self, item, **opts):
        from ..types.constants import _True
        v = self._data[item]
        t = self._items_type(self, item)
        opts.setdefault('context', self._context)
        if hasattr(t, '_lazyLoading'):
            if t._lazyLoading:
                opts.setdefault('validate', False)
        try:
            if t.is_primitive():
                opts['serialize'] = False
                return t(v, **opts)
            elif isinstance(t, _True):
                return v
            else:
                return v if isinstance(t, type) and isinstance(v, t) else t(v, **opts)
        except Exception as er:
            self._logger.error(er, exc_info=True)
            raise er

    def items_serialize(self, item, **opts):
        v = self[item]
        t = self._items_type(self, item)
        opts['context'] = getattr(v, '_context', self._context)
        return t._serialize(t, v, **opts)

    def __setitem__(self, item, value):
        self._data[item] = value
        if not self._lazyLoading:
            self._itemsInputs[item] = self._items_inputs_evaluate(item)
            self._set_dataValidated(item, self._items_evaluate(item))

    def __getitem__(self, item):
        if self._dataValidated[item] is None:
            self._itemsInputs[item] = self._items_inputs_evaluate(item)
            self._set_dataValidated(item, self._items_evaluate(item))
        return self._dataValidated[item]

    def __delitem__(self, index):
        del self._data[index]
        del self._dataValidated[index]
        del self._itemsInputs[index]
        CollectionProtocol._validate(self, self, items=False)

    def get(self, key, default=None):
        try:
            v = self[key]
            return default if v is None else v
        except KeyError:
            return default

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

    def _set_dataValidated(self, item, value):
        t = self._items_type(self, item)
        if t.is_primitive():
            orig = self._data[item]
            if not Pattern.check(orig) and not Expr.check(orig):
                self._data[item] = value
        else:
            self._data[item] = value
        self._dataValidated[item] = value

    def _is_outdated(self, item):
        return (self._dataValidated[item] is None and self._data[item] is not None
                ) or (self._itemsInputs.get(item, {}) != self._items_inputs_evaluate(item))

    @classmethod
    def create(cls, value=None, **opts):
        return cls(value, **opts)

    def do_validate(self, **opts):
        return self._validate(self, self, **opts)

    def do_serialize(self, deserialize=False, **opts):
        opts['context'] = self._context
        return self._serialize(self, self, deserialize=deserialize, **opts)
        return self._serializer._serialize(self, self, deserialize=deserialize, **opts)

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
        return hash(tuple(self._id, tuple((k, hash(v)) for k, v in enumerate(self._dataValidated))))


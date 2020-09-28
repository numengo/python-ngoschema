# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from abc import abstractmethod

from ..exceptions import InvalidValue
from ..managers.type_builder import DefaultValidator
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from .. import settings
from .type_protocol import TypeProtocol, value_opts
from ..types.strings import Pattern, Expr
from ..types.object import Object

COLLECTION_VALIDATE = settings.DEFAULT_COLLECTION_VALIDATE
LAZY_LOADING = settings.DEFAULT_COLLECTION_LAZY_LOADING


class CollectionProtocol(TypeProtocol):
    _session = None
    _lazy_loading = LAZY_LOADING
    _is_validated = False
    _data = None
    _data_validated = None
    _dependencies = {}
    _items_inputs = None
    _parent = None
    _root = None
    _item_type_cache = None
    _validate = COLLECTION_VALIDATE

    def __init__(self, value=None, items=None, context=None, session=None, **kwargs):
        self._lazy_loading = lz = self._lazy_loading if items is None else not items
        self._session = session = session or self._session
        # prepare data
        value, opts = value_opts(value, **kwargs)
        #if value and '$schema' in value:
        #    value.pop('$schema')
        validate = opts.pop('validate', self._validate)
        TypeProtocol.__init__(self, value, items=False, validate=False, context=context, **opts)
        # touch allocates storage for data, need to call create_context again
        self._touch()
        self.set_context(context, opts)
        if validate:
            # not lz all elements have been evaluated and validated. does not need to check items
            self.do_validate(items=not lz)
        elif not lz:
            self._coll_type(self)

    def set_context(self, context=None, *extra_contexts):
        from .object_protocol import ObjectProtocol
        TypeProtocol.set_context(self, context, *extra_contexts)
        ctx = self._context
        # _parent and _root are declared readonly in inspect.mm and it raises an error
        self._parent = next((m for m in ctx.maps if isinstance(m, ObjectProtocol) and m is not self), None)
        self._root = next((m for m in reversed(ctx.maps) if isinstance(m, ObjectProtocol) and m is not self), None)

    @classmethod
    def __ring_key__(cls):
        return cls._id

    @classmethod
    def check(cls, value, **opts):
        return isinstance(value, cls) or cls._check(cls, value)

    @classmethod
    def has_default(cls):
        return cls._has_default(cls)

    @classmethod
    def default(cls, **opts):
        return cls._default(cls, **opts)

    @classmethod
    def convert(cls, value, **opts):
        if cls._lazy_loading:
            opts.setdefault('items', False)
        return value if isinstance(value, cls) else cls(value, **opts)
        #return value if isinstance(value, cls) else cls(cls._convert(cls, value, **opts), **opts)

    @classmethod
    def inputs(cls, value, **opts):
        return cls._inputs(cls, value, **opts)

    @classmethod
    def validate(cls, value, **opts):
        return cls._do_validate(cls, value, **opts)

    @classmethod
    def evaluate(cls, value, convert=True, context=None, **opts):
        validate = opts.get('validate', cls._validate)
        if value is None:
            if not cls.has_default():
                return None
            value = cls.default()
            value = value.copy() if hasattr(value, 'copy') else value
        if not cls.check(value, convert=convert, context=context):
            cls.validate(value, with_type=True, **opts)
        typed = value
        if isinstance(value, cls):
            typed.set_context(context, opts)
        else:
            typed = cls.convert(value, context=context, **opts)
        if validate:
            cls.validate(typed, with_type=False, **opts)
        return typed

    def call_order(self, **opts):
        return self._call_order(self, self._data, **opts)

    def print_order(self, **opts):
        return self._print_order(self._data, **opts)

    def _touch(self):
        self._is_validated = False
        self._repr = None
        self._str = None

    def _item_touch(self, item):
        CollectionProtocol._touch(self)
        self._data_validated[item] = None
        self._items_inputs[item] = {}

    def _item_inputs_evaluate(self, item):
        ret = {}
        for k in self.inputs(self._data, item=item, with_inner=False):
            try:
                ret[k] = self[k]
            except Exception as er:
                self._logger.error(er, exc_info=True)
                pass
        return ret

    def _item_evaluate(self, item, **opts):
        v = self._data[item]
        t = self.item_type(item)
        opts.setdefault('context', self._context)
        if hasattr(t, '_lazy_loading'):
            if t._lazy_loading:
                opts.setdefault('validate', False)
        return t.evaluate(v, **opts)

    @classmethod
    def item_serialize(cls, value, item, **opts):
        v = value[item]
        t = cls.item_type(item)
        ctx = getattr(value, '_context', cls._context)
        opts.setdefault('context', ctx)
        return t.serialize(v, **opts)

    def __setitem__(self, item, value):
        self._data[item] = value
        if not self._lazy_loading:
            self._items_inputs[item] = self._item_inputs_evaluate(item)
            self._set_data_validated(item, self._item_evaluate(item))

    def __getitem__(self, item):
        if self._data_validated[item] is None:
            self._items_inputs[item] = self._item_inputs_evaluate(item)
            self._set_data_validated(item, self._item_evaluate(item))
        return self._data_validated[item]

    def __delitem__(self, index):
        del self._data[index]
        del self._data_validated[index]
        del self._items_inputs[index]
        self.do_validate(items=False)

    def _set_data(self, item, value):
        t = self.item_type(item)
        orig = self._data[item]
        # to avoid comparison of objects (often equality which is the longest to validate), only touch for changed primitives
        if t.is_primitive():
            if value != orig:
                self._item_touch(item)
        else:
            self._item_touch(item)
        self._data[item] = value

    def _set_data_validated(self, item, value):
        t = self.item_type(item)
        if t.is_primitive():
            orig = self._data[item]
            if not Pattern.check(orig) and not Expr.check(orig):
                self._data[item] = value
        else:
            self._data[item] = value
        self._data_validated[item] = value

    def _is_outdated(self, item):
        return (self._data_validated[item] is None and self._data[item] is not None
                ) or (self._items_inputs.get(item, []) != self._item_inputs_evaluate(item))

    @classmethod
    def validate(cls, value, as_dict=False, **opts):
        # check instances and set their validated flag if all items are validated
        if not cls.check(value):
            errors = {'type': '%s is not of type %s' % (value, cls._py_type)}
        else:
            items = opts.pop('items', not cls._lazy_loading)
            if isinstance(value, cls) and value._is_validated:
                return {}
            errors = cls._do_validate(cls, value, items=items, as_dict=as_dict, **opts)
            if items and isinstance(value, cls) and not opts.get('excludes') and not opts.get('only'):
                value._is_validated = True
        return errors if as_dict else cls._format_error(value, errors)

    def do_validate(self, items=True, **opts):
        return self.validate(self, items=items, **opts)

    @classmethod
    def serialize(cls, value, **opts):
        return cls._serialize(cls, value, **opts)

    def do_serialize(self, **opts):
        return self.serialize(self, **opts)

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


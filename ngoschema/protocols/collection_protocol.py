# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from abc import abstractmethod

from ..exceptions import InvalidValue
from ..managers.type_builder import DefaultValidator
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from .. import settings
from .type_protocol import TypeProtocol
from ..types.strings import Pattern, Expr
from ..types.object import Object

LAZY_LOADING = settings.DEFAULT_LAZY_LOADING


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
    _items_type_cache = None

    def __init__(self, *args, validate=False, lazy_loading=None, context=None, session=None, **kwargs):
        self._lazy_loading = lz = self._lazy_loading if lazy_loading is None else lazy_loading
        self._session = session = session or self._session
        # prepare data
        kwargs.pop('$schema', None)
        value = args[0] if args else kwargs or None
        opts = kwargs if args else {}
        TypeProtocol.__init__(self, value, items=False, validate=False, **opts)
        self._touch()
        self._make_context(context)
        if validate:
            # not lz all elements have been evaluated and validated. does not need to check items
            self.do_validate(items=not lz)
        elif not lz:
            self._coll_type(self)

    def _make_context(self, context=None, *extra_contexts):
        from .object_protocol import ObjectProtocol
        TypeProtocol._make_context(self, context, *extra_contexts)
        # _parent and _root are declared readonly in inspect.mm and it raises an error
        self._parent = next((m for m in self._context.maps if isinstance(m, ObjectProtocol) and m is not self), None)
        self._root = next((m for m in reversed(self._context.maps) if isinstance(m, ObjectProtocol) and m is not self), None)

    @classmethod
    def check(cls, value, **opts):
        return isinstance(value, cls) or cls._check(cls, value)

    @classmethod
    def convert(cls, value, **opts):
        return value if isinstance(value, cls) else cls._convert(cls, value, **opts)

    def call_order(self, **opts):
        return self._call_order(self, self._data, **opts)

    #@abstractmethod
    #def _call_order(self, value, with_inputs=True, **opts):
    #    pass

    def print_order(self, **opts):
        return self._print_order(self._data, **opts)

   # @abstractmethod
    #def _print_order(self, value, with_inputs=True, **opts):
    #    pass

    @abstractmethod
    def items_type(self, name):
        pass

    def _touch(self):
        self._is_validated = False
        self._repr = None
        self._str = None

    def _items_touch(self, item):
        CollectionProtocol._touch(self)
        self._data_validated[item] = None
        self._items_inputs[item] = {}

    def _items_inputs_evaluate(self, item):
        inputs = self.inputs(self._data, item=item, with_inner=False)
        return {k: self[k] for k in inputs}
        return {k: self[k] for k in self.inputs(self._data, item, with_inner=False)}

    def _items_evaluate(self, item, **opts):
        v = self._data[item]
        t = self.items_type(item)
        return t(self._data[item], context=self._context, **opts)

    def __setitem__(self, item, value):
        self._data[item] = value
        if not self._lazy_loading:
            self._items_inputs[item] = self._items_inputs_evaluate(item)
            self._set_data_validated(item, self._items_evaluate(item, validate=True))

    def __getitem__(self, item):
        if self._data_validated[item] is None:
            self._items_inputs[item] = self._items_inputs_evaluate(item)
            self._set_data_validated(item, self._items_evaluate(item, validate=True))
        return self._data_validated[item]

    def __delitem__(self, index):
        del self._data[index]
        del self._data_validated[index]
        del self._items_inputs[index]
        self.validate(items=False)

    def _set_data(self, item, value):
        t = self.items_type(item)
        if t.is_primitive() and value != self._data[item]:
            self._items_touch(item)
        self._data[item] = value

    def _set_data_validated(self, item, value):
        t = self.items_type(item)
        if t.is_primitive():
            #if value != self._data_validated[item]:
            #    self._items_touch(item)
            orig = self._data[item]
            if not Pattern.check(orig) and not Expr.check(orig):
                self._data[item] = value
        else:
            self._data[item] = value
        self._data_validated[item] = value

    def _is_outdated(self, item):
        return (self._data_validated[item] is None and self._data[item] is not None
                ) or (self._items_inputs[item] != self._items_inputs_evaluate(item))

    @classmethod
    def validate(cls, value, as_dict=True, **opts):
        if not cls.check(value):
            errors = {'type': '%s is not of type %s' % (value, cls._py_type)}
        else:
            items = opts.pop('items', not cls._lazy_loading)
            if isinstance(value, cls) and value._is_validated:
                return {}
            errors = cls._validate(cls, value, items=items, as_dict=as_dict, **opts)
            if items and isinstance(value, cls) and not opts.get('excludes') and not opts.get('only'):
                value._is_validated = True
        return errors if as_dict else cls._format_error(value, errors)

    def do_validate(self, **opts):
        return self.validate(self, items=True, **opts)

    def do_serialize(self, **opts):
        return self.serialize(self, **opts)

    def __eq__(self, other):
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


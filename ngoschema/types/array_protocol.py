# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import MutableSequence
import logging

from ..types import Array, Object, Literal, Type, Expr, Pattern
from ..decorators import classproperty
from ..utils import class_casted_as
from ..types.namespace import default_ns_manager
from .. import settings, DEFAULT_CONTEXT
from .. import settings

LAZY_LOADING = settings.DEFAULT_LAZY_LOADING


class ArrayProtocol(Array, MutableSequence):
    """
    ArrayProtocol is class defined by a json-schema and built by TypeBuilder.build_array_protocol.

    The class is built with a list or a unique item type (which can be a Literal or a subclass of
    ObjectProtocol or ArrayProtocol.

    If lazy loading is enabled, data is only constructed and validated on first read access. If not, validation is done
    when setting the item.
    """
    _lazy_loading = LAZY_LOADING
    _data = []
    _validated_data = []

    def __init__(self, data, validate=False, context=None, **opts):
        self._context = Array._make_context(self, context)
        self._lazy_loading = lz = not validate or self._lazy_loading
        if data is None:
            self._data = self.default().copy()
        else:
            self._data = Array._convert(self, data, convert=False, context=self._context, **opts)
        self._touch()
        if not lz:
            list(self)
        if validate:
            self.validate(self, excludes=['items'] if lz else [])

    def _touch(self, index=None):
        if index:
            self._validated_data[index] = None
            self._input_data[index] = {}
        else:
            self._input_data = [{}] * len(self._data)
            self._validated_data = [None] * len(self._data)

    def _set_data(self, index, value):
        if Literal.check(value) and value != self._data.get(index):
            self._touch(index)
        self._data[index] = value

    def _set_validated_data(self, index, value):
        if Literal.check(value) and value != self._validated_data[index]:
            self._touch(index)
        self._validated_data[index] = value

    def _item_evaluate(self, index, value, **opts):
        from .object_protocol import ObjectProtocol
        ptype = Array._item_type(self, index)
        if isinstance(value, ptype) and not Expr.check(value) and not Pattern.check(value):
            lz_excludes = ['items', 'properties'] if getattr(ptype, '_lazy_loading', False) else []
            ptype.validate(value, excludes=opts.pop('excludes', []) + lz_excludes, **opts)
        else:
            value = ptype(value, **opts)
        if isinstance(value, (ObjectProtocol, ArrayProtocol)):
            value._make_context(self._context)
        return value

    def __len__(self):
        return len(self._data)

    def insert(self, index, value):
        itype = self._item_type(index)
        self._input_data.insert(index, {})
        self._validated_data.insert(index, None)
        self._data.insert(index, value)
        if not self._lazy_loading:
            self._set_validated_data(index, self._item_evaluate(index, self._data[index]))
        self.validate(self, excludes=['items'])

    def __setitem__(self, index, value):
        itype = self._item_type(index)
        self._data[index] = value
        if not self._lazy_loading:
            self._set_validated_data(index, self._item_evaluate(index, self._data[index]))

    def __getitem__(self, index):
        if self._validated_data[index] is None:
            self._set_validated_data(index, self._item_evaluate(index, self._data[index]))
        return self._validated_data[index]

    def __delitem__(self, index):
        del self._data[index]
        del self._validated_data[index]
        self.validate(self, excludes=['items'])

    def __eq__(self, other):
        if not Array.check(other):
            return False
        if len(self) != len(other):
            return False
        for i, v in enumerate(other):
            if self[i] != v:
                return False
        return True

    def __hash__(self):
        return hash(tuple(self._id, self._validated_data))

    @classmethod
    def validate(cls, value, **opts):
        return Array.validate(cls, value, **opts)

    def do_validate(self, **opts):
        from .object_protocol import ObjectProtocol
        for i, (d, v) in enumerate(zip(self._data, self._validated_data)):
            if v is None and d is not None:
                v = self[i]
            if isinstance(v, (ObjectProtocol, ArrayProtocol)):
                v.do_validate(**opts)
            elif v is not None:
                Array._item_type(self, i).validate(v, **opts)
        return self._validated_data

    @classmethod
    def serialize(cls, value, **opts):
        return Array.serialize(cls, value, **opts)

    def do_serialize(self, **opts):
        from .object_protocol import ObjectProtocol
        ret = [None] * len(self._data)
        for i, (d, v) in enumerate(zip(self._data, self._validated_data)):
            if v is None and d is not None:
                v = self[i]
                #v = d
            if isinstance(v, (ObjectProtocol, ArrayProtocol)):
                ret[i] = v.do_serialize(**opts)
            elif v is not None:
                ret[i] = Array._item_type(self, i).serialize(v, **opts)
        return ret

    def __repr__(self):
        def format_str(t, item):
            if Object.check(item):
                return '{%i}' % (len([k for k, v in item.items() if v is not None]))
            if Array.check(item, with_string=False):
                return '[%i]' % (len(item))
            return t.serialize(item)

        def trim(s):
            return (s[:settings.PPRINT_MAX_STRL] + '...') if len(s) >= settings.PPRINT_MAX_STRL else s

        return '<%s item=%s [%s]>' % (self.__class__.__name__, self._items._id,
                              ', '.join([trim(format_str(t, v)) for i, (t, v) in enumerate(zip(self._items_types(self), self))
                                        if i < settings.PPRINT_MAX_EL] + (
                                  ['...'] if len(self) >= settings.PPRINT_MAX_EL else [])))

    @classmethod
    def convert(cls, value, **opts):
        return Array._convert(cls, value, **opts)

    _default = None
    @classmethod
    def default(cls):
        if cls._default is None:
            cls._default = Array.default(cls)
        return cls._default

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from .type_builder import TypeBuilder
        attrs = attrs or {}
        cname = default_ns_manager.get_id_cname(id)
        clsname = cname.split('.')[-1]
        logger = logging.getLogger(cname)
        items = schema.get('items')
        items_list = False
        if items:
            if Array.check(items):
                items_list = True
                items = [TypeBuilder.build(f'{id}/items/{i}', item) for i, item in enumerate(items)]
            else:
                items = TypeBuilder.build(f'{id}/items', items)
        attrs.setdefault('_lazy_loading', LAZY_LOADING)
        if not any([issubclass(b, ArrayProtocol) for b in bases]):
            bases = list(bases) + [ArrayProtocol]
        attrs['_lazy_loading'] = getattr(items, '_lazy_loading', LAZY_LOADING)
        attrs['_items'] = items
        attrs['_items_list'] = items_list
        attrs['_schema'] = schema
        attrs['_logger'] = logger
        cls = type(clsname, tuple(bases), attrs)
        return cls

    @classmethod
    def extend_type(cls, *bases, **schema):
        if bases or schema:
            return ArrayProtocol.build(cls.__name__, schema, cls, *bases)
        return cls

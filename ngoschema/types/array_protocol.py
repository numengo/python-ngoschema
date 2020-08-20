# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import MutableSequence
import six
import logging

from ..exceptions import InvalidValue
from ..types import Array, Object, Literal, Type, Expr, Pattern
from ..decorators import classproperty
from ..utils import shorten
from ..types.namespace_manager import default_ns_manager
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

    def __init__(self, data, validate=False, check=False, context=None, session=None, **opts):
        self._make_context(context)
        self._session = session
        self._lazy_loading = lz = not validate or self._lazy_loading
        if check and not self.check(data):
            raise InvalidValue('%s is not compatible with %s' % data, self)
        if data is None:
            self._data = self.default().copy()
        else:
            self._data = Array._convert(self, data, convert=False, context=self._context, **opts)
        if self._has_pk:
            for i, (t, v) in enumerate(zip(self._items_types(self._data), self._data)):
                self._set_data(i, v)
        self._touch()
        if not lz:
            list(self)
        if validate:
            self.validate(self, excludes=['items'] if lz else [])

    def _touch(self, index=None):
        self._srepr = None
        if index:
            self._validated_data[index] = None
            self._input_data[index] = {}
        else:
            self._input_data = [{}] * len(self._data)
            self._validated_data = [None] * len(self._data)

    def _set_data(self, index, value):
        from ..models import Entity
        itype = Array._item_type(self, index)
        if issubclass(itype, Entity) and value is not None and not Object.check(value):
            obj = self.session.resolve_fkey(value, itype)
            assert obj
            value = obj
        if Literal.check(value) and value != self._data.get(index):
            self._touch(index)
        self._data[index] = value

    def _set_validated_data(self, index, value):
        if Literal.check(value) and value != self._validated_data[index]:
            self._touch(index)
        self._validated_data[index] = value

    def _make_context(self, context=None, *extra_contexts):
        self._context = Array._make_context(self, context, *extra_contexts)
        from .object_protocol import ObjectProtocol
        self._parent = next((m for m in self._context.maps_flattened if isinstance(m, ObjectProtocol) and m is not self), None)
        self._root = next((m for m in reversed(self._context.maps_flattened) if isinstance(m, ObjectProtocol) and m is not self), None)

    def _item_evaluate(self, index, value, **opts):
        from .object_protocol import ObjectProtocol
        ptype = Array._item_type(self, index)
        if isinstance(value, ptype) and not Expr.check(value) and not Pattern.check(value):
            if isinstance(value, (ObjectProtocol, ArrayProtocol)):
                lz_excludes = ['items', 'properties'] if getattr(ptype, '_lazy_loading', False) else []
                value.validate(value, excludes=opts.pop('excludes', []) + lz_excludes, **opts)
            else:
                ptype.validate(value, **opts)
        else:
            value = ptype(value, session=self.session, **opts, context=self._context)
        if isinstance(value, (ObjectProtocol, ArrayProtocol)):
            value._make_context(self._context)
        return value

    def __len__(self):
        return len(self._data)

    def insert(self, index, value):
        self._input_data.insert(index, {})
        self._validated_data.insert(index, None)
        self._data.insert(index, value)
        if not self._lazy_loading:
            self._set_validated_data(index, self._item_evaluate(index, self._data[index]))
        else:
            value._make_context(self._context)
        self.validate(self, excludes=['items'])

    def __setitem__(self, index, value):
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
            if isinstance(v, (ObjectProtocol, ArrayProtocol)):
                ret[i] = v.do_serialize(**opts)
            elif v is not None:
                ret[i] = Array._item_type(self, i).serialize(v, **opts)
        return ret

    _srepr = None
    def _repr_list(self):
        if self._srepr is None:
            hidden = max(0, len(self) - settings.PPRINT_MAX_EL)
            a = [shorten(self._validated_data[i] or self._data[i]) for i, t in enumerate(self._items_types(self))
                 if i < settings.PPRINT_MAX_EL] + (['+%i...' % hidden] if hidden else [])
            self._srepr = '[%s]' % (', '.join(a))
        return self._srepr

    def __repr__(self):
        return '%s([%s])' % (self.qualname(), self._repr_list())

    def __str__(self):
        return self._repr_list()

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
        attrs['_has_pk'] = bool(any(len(getattr(t, '_primary_keys', [])) for t in items)\
                                    if items_list else len(getattr(items, '_primary_keys', [])))
        attrs['_items_list'] = items_list
        attrs['_schema'] = schema
        attrs['_logger'] = logger
        attrs['_schema_id'] = id
        attrs['_id'] = id
        cls = type(clsname, tuple(bases), attrs)
        return cls

    @classmethod
    def extend_type(cls, *bases, **schema):
        if bases or schema:
            return ArrayProtocol.build(cls.__name__, schema, cls, *bases)
        return cls

    @property
    def session(self):
        if not self._session and self._root and getattr(self._root, '_repo', None):
            self._session = self._root._repo.session
        return self._session

    def get(self, *pks, default=None, **kwargs):
        from ..query import Query
        if pks:
            kwargs.update({k: v for k, v in zip(self._items._primary_keys, pks)})
        try:
            return Query(self).next(**kwargs)
        except StopIteration as er:
            return default

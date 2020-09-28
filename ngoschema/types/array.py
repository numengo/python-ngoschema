# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import Mapping, Sequence, deque, OrderedDict

from ..exceptions import ValidationError, ConversionError
from ..decorators import log_exceptions
from ..managers.type_builder import register_type
from .type import TypeProtocol, Type
from .constants import _True
from .strings import String


@register_type('array')
class Array(Type):
    """
    json-schema 'array' type
    """
    _py_type = list
    _coll_type = list
    _items = _True()
    _items_list = False
    _str_delimiter = ','
    _min_items = 0
    _max_items = None
    _unique_items = False

    def __init__(self, **schema):
        # split the schema to isolate items schema and object schema
        from ..managers.type_builder import TypeBuilder
        Type.__init__(self, **schema)
        schema = self._schema
        items = schema.get('items', True)
        cls_name = f'{self.__class__.__name__}_{id(self)}'
        if isinstance(items, Mapping):
            self._items = TypeBuilder.build(f'{cls_name}/items', items)
        if isinstance(items, Sequence):
            self._items_list = True
            self._items = [TypeBuilder.build(f'{cls_name}/items/{i}', item)
                               for i, item in enumerate(items)]
        self._min_items = schema.get('minItems', self._min_items)
        self._max_items = schema.get('maxItems', self._max_items)
        self._unique_items = schema.get('uniqueItems', self._unique_items)
        self._str_delimiter = schema.get('strDelimiter') or self._str_delimiter

    @classmethod
    def is_array(cls):
        return True

    @classmethod
    def is_array_primitive(cls):
        if cls._items_list:
            return all([it.is_primitive() for it in cls._items])
        else:
            return cls._items.is_primitive()

    def _check(self, value, with_string=True, **opts):
        if String.check(value):
            if not with_string:
                return False
            value = Array._convert(self, value)
        if not isinstance(value, (Sequence, deque)):
            return False
        l = len(value)
        if self._max_items and l > self._max_items:
            return False
        if l < self._min_items:
            return False
        return True

    def _print_order(self, value, **opts):
        # better later including dependencies
        return range(len(value))

    def _call_order(self, value, **opts):
        # better later including dependencies
        return range(len(value))

    def _convert(self, value, convert=False, **opts):
        if String.check(value, **opts):
            value = [s.strip() for s in value.split(self._str_delimiter)]
        value = value if isinstance(value, (Sequence, deque)) else [value]
        lv = len(value)
        items = [None] * max(len(value), self._min_items)
        for i, t in enumerate(Array._item_types(self, items)):
            v = value[i] if i < lv else t.default(**opts)
            items[i] = v if not convert else t(v, **opts)
        return self._py_type(items) if convert else items

    def _convert(self, value, items=True, **opts):
        if String.check(value):
            value = [s.strip() for s in value.split(self._str_delimiter)]
        value = value if isinstance(value, (Sequence, deque)) else [value]
        lv = len(value)
        ret = list(value)
        ret += [None] * max(0, self._min_items - len(ret))
        for i, (t, v) in enumerate(zip(Array._item_types(self, ret), ret)):
            if not items and v is None and t.has_default():
                v = t.default(raw_literals=True, **opts)
            ret[i] = v if not items else t.evaluate(v, **opts)
        return self._coll_type(ret)

    def _item_types(self, value):
        return self._items if self._items_list else [self._items] * len(value)

    def item_type(self, index):
        return self._items[index] if self._items_list else self._items

    def _inputs(self, value, item=None, with_inner=False, **opts):
        if String.check(value):
            value = Array.convert(value or [], convert=False)
        if item is not None:
            try:
                #t = Array._item_type(self, item)
                t = Array.item_type(self, item)
                return t.inputs(value[item], **opts)
            except Exception as er:
                self._logger.error('%i %s' % (item, value))
                raise er
        if with_inner:
            return set().union(*[Array.inputs(self, value, i, with_inner=False, **opts) for i, v in enumerate(value)])
        return set()

    def _do_validate(self, value, items=True, as_dict=False, **opts):
        errors = {}
        # to evaluate items, enumerating will call __getitem__ and validate each item
        try:
            if items:
                for i, t in enumerate(Array._item_types(self, value)):
                    errors.update(t.validate(value[i], as_dict=True, **opts))
            errors.update(TypeProtocol._do_validate(self, value, excludes=['items'], as_dict=True, **opts))
        except Exception as er:
            raise er
        return errors if as_dict else self._format_error(value, errors)

    def _has_default(self):
        return True  # default is empty list

    def _default(self, items=True, **opts):
        return Array._convert(self, self._schema.get('default', []), items=items, **opts)

    def _serialize(self, value, as_string=False, **opts):
        if as_string:
            return self._str_delimiter.join([String.serialize(v, **opts) for v in value])
        else:
            return [t.serialize(v, **opts) for t, v in zip(Array._item_types(self, value), value)]


ArrayString = Array.extend_type('ArrayString', items=String)


@register_type('tuple')
class Tuple(Array):
    _py_type = tuple
    _coll_type = tuple


@register_type('set')
class Set(Array):
    _py_type = set
    _coll_type = set

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import Mapping, Sequence, deque, OrderedDict

from ..exceptions import ValidationError, ConversionError
from ..utils import ReadOnlyChainMap as ChainMap
from ..decorators import log_exceptions
from ..managers.type_builder import register_type
from ..protocols.serializer import Serializer
from .type import Type
from .constants import _True
from .collection import CollectionDeserializer, CollectionSerializer, Collection
from .strings import String


class ArrayDeserializer(CollectionDeserializer):
    _collType = list
    _minItems = 0
    _maxItems = None
    _uniqueItems = False
    _splitString = False
    _strDelimiter = ','

    def __init__(self, minItems=None, maxItems=None, uniqueItems=None, splitString=None, strDelimiter=None, **opts):
        self._minItems = minItems or self._minItems
        self._maxItems = maxItems or self._maxItems
        self._uniqueItems = uniqueItems or self._uniqueItems
        self._splitString = splitString or self._splitString
        self._strDelimiter = strDelimiter or self._strDelimiter
        CollectionDeserializer.__init__(self, **opts)

    @staticmethod
    def _convert(self, value, **opts):
        value = self._collType([value[k] for k in self._call_order(self, value, **opts)])
        return CollectionDeserializer._convert(self, value, **opts)

    @staticmethod
    def _deserialize(self, value, **opts):
        value = CollectionDeserializer._deserialize(self, value, **opts)
        #split_string = self._splitString if split_string is None else split_string
        #str_del = self._strDelimiter if str_del is None else str_del
        if String.check(value):
            split_string = opts.get('split_string', self._splitString)
            str_del = opts.get('strDelimiter', self._strDelimiter)
            value = [s.strip() for s in value.split(str_del)] if split_string else [value]
        else:
            value = list(value) if isinstance(value, (Sequence, deque)) else [value]
        many = opts.get('many', self._many)
        lv = len(value)
        if lv > 1 and not many:
            raise ConversionError("Only one value is expected (%i): %s" % (lv, value))
        value += [None] * max(0, self._minItems - lv)
        return self._collType(value)

    @staticmethod
    def _validate(self, value, **opts):
        value = CollectionDeserializer._validate(self, value, **opts)
        if self._uniqueItems:
            hashes = set([hash(v) for v in value])
            if len(hashes) != len(value):
                ValidationError('Duplicate items in %s.' % value)
        return value

    @staticmethod
    def _call_order(self, value, **opts):
        # better later including dependencies
        return range(len(value))


class ArraySerializer(CollectionSerializer, ArrayDeserializer):
    _deserializer = ArrayDeserializer

    def __init__(self, **opts):
        CollectionSerializer.__init__(self, **opts)

    @staticmethod
    def _print_order(self, value, **opts):
        # better later including dependencies
        return range(len(value))

    @staticmethod
    def _serialize(self, value, as_string=False, **opts):
        value = CollectionSerializer._serialize(self, value, **opts)
        value = self._collType([value[k] for k in self._print_order(self, value, **opts)])
        if as_string:
            value = self._strDelimiter.join([String.serialize(v, **opts) for v in value])
        return value


@register_type('array')
class Array(Collection, ArraySerializer):
    _many = True
    _serializer = ArraySerializer
    _deserializer = ArrayDeserializer
    _pyType = list
    _itemsIsList = False
    _default = []

    @classmethod
    def is_array(cls):
        return True

    def __init__(self, items=None, **opts):
        # split the schema to isolate items schema and object schema
        from ..managers.type_builder import type_builder
        cls_name = f'{self.__class__.__name__}_{id(self)}'
        if isinstance(items, Mapping):
            self._items = type_builder.build(f'{cls_name}/items', items)
        elif isinstance(items, Sequence):
            self._itemsIsList = True
            self._items = [type_builder.build(f'{cls_name}/items/{i}', item)
                               for i, item in enumerate(items)]
        else:
            self._items = items or _True()
        Collection.__init__(self, **opts)

    def __call__(self, value=None, *values, **opts):
        value = value or list(values)  # to allow initialization by varargs
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        return Type.__call__(self, value, **opts)

    @staticmethod
    def _items_types(self, value, **opts):
        value = self._items[:len(value)] if self._itemsIsList else [self._items] * len(value)
        return [(i, v) for i, v in enumerate(value)]

    @staticmethod
    def _items_type(self, item):
        from ..protocols.type_proxy import TypeProxy
        t = self._items[item] if self._itemsIsList else self._items
        return t.proxy_type() if getattr(t, '_proxyUri', None) else t

    @staticmethod
    def _repr_schema(self):
        rs = Type._repr_schema(self)
        if self._items:
            if self._itemsIsList:
                rsi = [i._repr_schema(i) if isinstance(i, Type) else i for i in self._items]
            else:
                i = self._items
                rsi = self._items._repr_schema(i) if isinstance(i, Type) else i
            rs['items'] = rsi
        if self._minItems:
            rs['minItems'] = self._minItems
        if self._maxItems:
            rs['maxItems'] = self._maxItems
        if self._uniqueItems:
            rs['uniqueItems'] = self._uniqueItems
        if self._splitString:
            rs['splitString'] = self._splitString
            rs['strDelimiter'] = self._strDelimiter
        return rs

    @staticmethod
    def _has_default(self, value=None, **opts):
        return True

    def default(self, value=None, **opts):
        value = value or self._default
        ret = [None] * len(value)
        for k, t in self._items_types(self, value):
            ret[k] = t.default(value[k], **opts) if t.has_default(value[k]) else None
        return self._serialize(self, ret, items=False, **opts)

    @staticmethod
    def _null(self, value, **opts):
        return self._collType([None for k in self.call_order(value, **opts)])

    @staticmethod
    def _check(self, value, split_string=True, **opts):
        if String.check(value):
            if not split_string:
                raise TypeError('%s is a string and is not allowed in this array. Use split_string.')
            value = Array._convert(self, value)
        if not isinstance(value, Sequence):
            raise TypeError('%s is not a sequence or array.')
        return Collection._check(self, value, **opts)

    @staticmethod
    def _validate(self, value, items=True, excludes=[], **opts):
        excludes = list(excludes) + ['minItems', 'maxItems', 'uniqueItems', 'items']
        # TODO add validate size, uniqueness as separate validation methods
        #value = self._deserializer._validate(self, value, excludes=excludes, **opts)
        value = Collection._validate(self, value, items=items, excludes=excludes, **opts)
        return value

    @staticmethod
    def _inputs(self, value, items=False, **opts):
        inputs = set()
        if String.check(value):
            value = Array._convert(self, value or [], convert=False)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    inputs.update(ChainMap(*[set([f'{k}.{i}' for i in t._inputs(t, value[k], **opts)])]))
            #return inputs.union(*[Array._inputs(self, value, i, items=False, **opts) for i, v in enumerate(value)])
        return inputs

    @classmethod
    def is_array_primitive(cls):
        if cls._itemsIsList:
            return all([it.is_primitive() for it in cls._items])
        else:
            return cls._items.is_primitive()


ArrayString = Array.extend_type('ArrayString', items=String)


@register_type('tuple')
class Tuple(Array):
    _pyType = tuple
    #_collType = list


@register_type('set')
class Set(Array):
    _pyType = set
    #_collType = list

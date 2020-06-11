# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import Mapping, Sequence, deque

from ..exceptions import ValidationError, ConversionError
from ..utils import ReadOnlyChainMap as ChainMap
from ..decorators import classproperty, memoized_method
from .type import Type, TypeChecker
from .literals import String


@TypeChecker.register('array')
class Array(Type):
    """
    json-schema 'array' type
    """
    _schema = {'type': 'array'}
    _py_type = list
    _items = Type()
    _items_list = False
    _str_delimiter = ','

    def __init__(self, **schema):
        # split the schema to isolate items schema and object schema
        from .type_builder import TypeBuilder
        Type.__init__(self, **schema)
        items = self._schema.get('items', {})
        if isinstance(items, Mapping):
            self._items = Type.build(f'{self.__class__.__name__}/items', items)()
        if isinstance(items, Sequence):
            self._items_list = True
            self._items = [Type.build(f'{self.__class__.__name__}/items/{i}', item)()
                               for i, item in enumerate(items)]
        self._str_delimiter = self._schema.get('str_delimiter') or self._str_delimiter

    @classmethod
    def check(cls, value, with_string=True, **opts):
        if with_string and String.check(value):
            return True
        return isinstance(value, (Sequence, deque)) and not isinstance(value, str)

    def convert(self, value, **opts):
        return Array._convert(self, value, **opts)

    @staticmethod
    def _convert(self, value, convert=True, **opts):
        if String.check(value, **opts):
            value = [s.strip() for s in value.split(self._str_delimiter)]
        value = value if isinstance(value, (Sequence, deque)) else [value]
        return self._py_type(v if not convert else t(v, **opts)
                for t, v in zip(Array._items_types(self, value), value))

    def _items_types(self, value):
        return self._items if self._items_list else [self._items] * len(value)

    def _item_type(self, index):
        return self._items[index] if self._items_list else self._items

    @classmethod
    def inputs(cls, value, **opts):
        return Array._inputs(cls, value, **opts)

    def _inputs(self, value, index=None, with_inner=False, **opts):
        value = Array.convert(self, value or [], convert=False)
        if index is not None:
            try:
                itypes = Array._items_types(self, value)
                return itypes[index].inputs(value[index], **opts)
            except Exception as er:
                self._logger.error('%i %s' % (index, value))
                raise er
        if with_inner:
            return set().union(*[Array._inputs(self, value, i, with_inner=False, **opts) for i, v in enumerate(value)])
        return set()

    def validate(self, value, excludes=[], as_dict=False, **opts):
        errors = {}
        # to evaluate items, enumerating will call __getitem__ and validate each item
        try:
            if 'items' not in excludes:
                for i, t in enumerate(Array._items_types(self, value)):
                    if i not in excludes:
                        errors.update(t.validate(value[i], as_dict=True, **opts))
            errors.update(Type.validate(self, value, excludes=excludes + ['items'], as_dict=True, **opts))
        except Exception as er:
            raise er
        return errors if as_dict else self._format_error(value, errors)

    @classmethod
    def has_default(cls):
        return True

    def default(self):
        ret = Type._default(self)
        size = self._schema.get('minItems', len(ret or []))
        return self.convert(ret) if ret else [self._items.default() if self._items and size else None] * size

    def serialize(self, value, **opts):
        return self._py_type(t.serialize(v, **opts) for t, v in zip(Array._items_types(self, value), value))


ArrayString = Array.extend_type(items=String)


@TypeChecker.register('tuple')
class Tuple(Array):
    _py_type = tuple

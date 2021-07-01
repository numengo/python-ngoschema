# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import MutableSequence
import six
import logging

from ..types.array import Array, ArraySerializer, ArrayDeserializer
from .collection_protocol import CollectionProtocol, TypeProtocol
from ..types.constants import _True
from ..utils import shorten
from ..managers.namespace_manager import default_ns_manager
from .. import settings


LAZY_LOADING = settings.DEFAULT_COLLECTION_LAZY_LOADING
TRUE = _True()


class ArrayProtocol(CollectionProtocol, Array, MutableSequence):
    """
    ArrayProtocol is class defined by a json-schema and built by TypeBuilder.build_array_protocol.

    The class is built with a list or a unique item type (which can be a Literal or a subclass of
    ObjectProtocol or ArrayProtocol.

    If lazy loading is enabled, data is only constructed and validated on first read access. If not, validation is done
    when setting the item.
    """
    _serializer = ArraySerializer
    _deserializer = ArrayDeserializer
    _collection = Array
    _data = []
    _dataValidated = []
    _itemsInputs = []

    @classmethod
    def default(cls, value=None, evaluate=False, **opts):
        dft = Array.default(cls, value, evaluate=evaluate, **opts)
        return cls(dft, **opts) if evaluate else dft

    def _touch(self):
        CollectionProtocol._touch(self)
        self._dataValidated = [None] * len(self._data)
        self._itemsInputs = [{}] * len(self._data)

    #@staticmethod
    #def _items_type(self, item):
    #    #from .type_proxy import TypeProxy
    #    #if self._items_type_cache is None:
    #    #    if not self._itemsIsList:
    #    #        if hasattr(self._items, 'proxy_type'):
    #    #            if self._items.proxy_type:
    #    #                self._items = self._items.proxy_type
    #    #                self._items_type_cache = self._items
    #    #        else:
    #    #            self._items_type_cache = self._items
    #    #    else:
    #    #        ok = True
    #    #        for i, t in enumerate(self._items):
    #    #            if hasattr(t, 'proxy_type'):
    #    #                if t.proxy_type:
    #    #                    self._items[i] = t.proxy_type
    #    #                else:
    #    #                    ok = False
    #    #        if ok:
    #    #            self._items_type_cache = self._items
    #    #return self._items_type_cache[item] if self._itemsIsList else self._items_type_cache
    #    return Array._items_type(self, item)

    def __len__(self):
        return len(self._data)

    def insert(self, item, value):
        self._itemsInputs.insert(item, {})
        self._dataValidated.insert(item, None)
        self._data.insert(item, value)
        if not self._lazyLoading:
            self._itemsInputs[item] = self._items_inputs_evaluate(item)
            self._set_dataValidated(item, self._items_evaluate(item))
        elif isinstance(value, TypeProtocol):
            value.set_context(self._context)
        self._validate(self, value, items=False)

    def _str_list(self):
        if self._str is None:
            hidden = max(0, len(self) - settings.PPRINT_MAX_EL)
            a = [shorten(self._dataValidated[i] or self._data[i], str_fun=repr)
                 for i, t in enumerate(self._items_types(self, self._data))
                 if i < settings.PPRINT_MAX_EL] + (['+%i...' % hidden] if hidden else [])
            self._str = '[%s]' % (', '.join(a))
        return self._str

    def __repr__(self):
        return '%s(%s)' % (self.qualname(), ArrayProtocol._str_list(self))

    def __str__(self):
        return ArrayProtocol._str_list(self)

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from ..managers.type_builder import type_builder
        attrs = attrs or {}
        cname = default_ns_manager.get_id_cname(id)
        clsname = cname.split('.')[-1]
        logger = logging.getLogger(cname)
        items = schema.get('items')
        items_list = False
        lz = schema.get('lazyLoading', None)
        if items:
            if Array.check(items):
                items_list = True
                items = [type_builder.build(f'{id}/items/{i}', item) for i, item in enumerate(items)]
            else:
                items = type_builder.build(f'{id}/items', items)
                lz = lz or getattr(items, '_lazyLoading', None)
        else:
            items = TRUE
        if not any([issubclass(b, ArrayProtocol) for b in bases]):
            bases = list(bases) + [ArrayProtocol]
        #if 'validate' in schema:
        #    attrs['_validate'] = schema['validate']
        if 'default' in schema:
            attrs['_default'] = schema['default']
        if lz is not None:
            attrs.setdefault('_lazyLoading', lz)
        attrs['_items'] = items
        attrs['_minItems'] = schema.get('minItems', Array._minItems)
        attrs['_maxItems'] = schema.get('maxItems', Array._maxItems)
        attrs['_uniqueItems'] = schema.get('uniqueItems', Array._uniqueItems)
        attrs['_splitString'] = schema.get('splitString', Array._splitString)
        attrs['_strDelimiter'] = schema.get('strDelimiter', Array._strDelimiter)
        attrs['_hasPk'] = bool(any(len(getattr(t, '_primaryKeys', [])) for t in items)\
                                    if items_list else len(getattr(items, '_primaryKeys', [])))
        attrs['_itemsIsList'] = items_list
        attrs['_schema'] = schema
        attrs['_logger'] = logger
        attrs['_id'] = id
        cls = type(clsname, tuple(bases), attrs)
        cls._pyType = cls
        return cls

    @property
    def identityKeys(self):
        return [i.identityKeys for i in self] if self._hasPk else None

    @property
    def attrs(self, attr):
        return [i[attr] for i in self]

    def get(self, *pks, default=None, **kwargs):
        from ..query import Query
        if pks:
            kwargs.update({k: v for k, v in zip(self._items._primaryKeys, pks)})
        try:
            return Query(self).next(**kwargs)
        except StopIteration as er:
            return default

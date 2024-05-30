# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections.abc import MutableSequence, Sequence
import six
import logging
import gettext

from ..datatypes.array import Array, ArraySerializer, ArrayDeserializer
from .collection_protocol import CollectionProtocol, TypeProtocol
from ..datatypes.constants import _True
from ..utils import shorten, to_list
from ..managers.namespace_manager import default_ns_manager
from .. import settings

_ = gettext.gettext
LAZY_LOADING = settings.DEFAULT_COLLECTION_LAZY_LOADING
TRUE = _True()


class ArrayProtocol(CollectionProtocol, Array, MutableSequence):
    _("""
    ArrayProtocol is class defined by a json-schema and built by TypeBuilder.build_array_protocol.

    The class is built with a list or a unique item type (which can be a Literal or a subclass of
    ObjectProtocol or ArrayProtocol.

    If lazy loading is enabled, data is only constructed and validated on first read access. If not, validation is done
    when setting the item.
    """)
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

    def __eq__(self, other):
        return CollectionProtocol.__eq__(self, other) if isinstance(other, Sequence) else False

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
            a = [shorten(self._dataValidated[i] or self._data[i], str_fun=str)
                 for i, t in enumerate(self._items_types(self, self._data))
                 if i < settings.PPRINT_MAX_EL] + (['+%i...' % hidden] if hidden else [])
            self._str = '[%s]' % (', '.join(a))
        return self._str

    def __repr__(self):
        return '%s(%s)' % (self.qualname(), ArrayProtocol._str_list(self))

    def __str__(self):
        if self._asString:
            return ArraySerializer._serialize(self, self)
        return ArrayProtocol._str_list(self)

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from ..managers.type_builder import type_builder
        attrs = attrs or {}
        cname = default_ns_manager.get_id_cname(id)
        clsname = cname.split('.')[-1]
        logger = logging.getLogger(cname)
        description = schema.get('description')
        comment = schema.get('$comment')
        title = schema.get('title', clsname)
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
        attrs['_title'] = title
        attrs['__doc__'] = description
        attrs['_description'] = description
        attrs['_comment'] = comment
        attrs['_minItems'] = schema.get('minItems', Array._minItems)
        attrs['_maxItems'] = schema.get('maxItems', Array._maxItems)
        attrs['_uniqueItems'] = schema.get('uniqueItems', Array._uniqueItems)
        attrs['_asString'] = schema.get('asString', Array._asString)
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

    def sort(self, key=None, reverse=False):
        list(self)
        # sort 2 lists by one
        self._dataValidated, self._data = zip(*sorted(zip(self._dataValidated, self._data), key=key, reverse=reverse))

    def get(self, *iks, default=None, **kwargs):
        from ..query import Query
        items = self._items
        if iks:
            from ..models.instances import Entity, Instance
            if items and not self._itemsIsList and issubclass(items, Instance):
                pks = items._primaryKeys if issubclass(items, Entity) else ('name', )
                kwargs.update({k: v for k, v in zip(pks, iks)})
            else:
                raise Exception('can only access this way an array of a given unique Instance or Entity')
        if items is not None and not self._itemsIsList:
            for alias, raw in self._items._aliases.items():
                if alias in kwargs:
                    kwargs[raw] = kwargs.pop(alias)
            for alias, raw in self._items._aliasesNegated.items():
                if alias in kwargs:
                    kwargs[raw] = - kwargs.pop(alias)
        try:
            return Query(self).next(**kwargs)
        except StopIteration as er:
            return default

    def query(self, *attrs, distinct=False, order_by=False, reverse=False, **attrs_value):
        from ..query import Query
        items = self._items
        if items is not None and items is not TRUE and not self._itemsIsList:
            for alias, raw in self._items._aliases.items():
                if alias in attrs_value:
                    attrs_value[raw] = attrs_value.pop(alias)
            for alias, raw in self._items._aliasesNegated.items():
                if alias in attrs_value:
                    attrs_value[raw] = - attrs_value.pop(alias)
        return Query(self, distinct=distinct, order_by=order_by, reverse=reverse).get(*attrs, **attrs_value)

    def __setitem__(self, item, value):
        if isinstance(item, int):
            return CollectionProtocol.__setitem__(self, item, value)
        from ..models.instances import Entity, Instance
        iks = to_list(item)
        items = self._items
        if items and not self._itemsIsList and issubclass(items, Instance):
            pks = items._primaryKeys if issubclass(items, Entity) else ('name', )
            if len(iks) != len(pks):
                raise NotImplemented('access error with key %s where expecting %s' % (iks, pks))
            for i, v in enumerate(self):
                if iks == [v[pk] for pk in pks]:
                    return CollectionProtocol.__setitem__(self, i, value)
            if not isinstance(value, Instance):
                value = items(**value)
            for pk, ik in zip(pks, iks):
                vik = value[pk]
                if vik is not None and vik != ik:
                    self.logger('changing primary key!!!')
                value[pk] = ik
            self.append(value)
        else:
            raise NotImplemented('access error with key %s' % item)

    def __getitem__(self, item):
        if isinstance(item, int):
            return CollectionProtocol.__getitem__(self, item)
        from ..models.instances import Entity, Instance
        iks = to_list(item)
        items = self._items
        if items and not self._itemsIsList and isinstance(items, type) and issubclass(items, Instance):
            pks = items._primaryKeys if issubclass(items, Entity) else ('name', )
            if len(iks) != len(pks):
                raise ValueError('access error with key %s where expecting %s' % (iks, pks))
            return self.get(*iks)
        else:
            raise ValueError('access error with key %s' % item)

    def __contains__(self, value):
        for v in self:
            if v is value or v == value:
                return True
        from ..models.instances import Entity, Instance
        items = self._items
        if items and not self._itemsIsList and issubclass(items, Instance):
            pks = items._primaryKeys if issubclass(items, Entity) else ('name', )
            iks = to_list(value)
            if len(pks) != len(iks):
                return False
            for i, v in enumerate(self):
                if iks == [v[pk] for pk in pks]:
                    return True
            return False
        return False

    def __eq__(self, other, parents=tuple()):
        if other is None:
            return False
        if other is self:
            return True
        if self in parents:
            return True
        if not isinstance(other, Sequence):
            return False
        if len(self) != len(other):
            return False
        for i, v in enumerate(other):
            v2 = self[i]
            if isinstance(v2, CollectionProtocol):
                if not v2.__class__.__eq__(v2, v, parents=parents+(self, )):
                    return False
            elif v2 != v:
                return False
        return True

    def diff(self, other, parents=tuple()):
        if not isinstance(other, Sequence):
            return other
        if self in parents:
            return
        l1 = len(self)
        l2 = len(other)
        ret = {i: self[i].diff(other[i], parents=parents+(self,)) if isinstance(self[i], CollectionProtocol) else other[i] for i in range(min(l1, l2)) if self[i] != other[i]}
        if l2 > l1:
            ret.update({i: other[i] for i in range(l1, l2)})
        if l2 < l1:
            ret.update({i: self[i] for i in range(l2, l1)})
        return ret

    def copy(self, _parents=tuple()):
        for orig, copy in _parents:
            if self is orig:
                return copy
        self.do_validate()
        copy = self.create(self._dataValidated, context=self._context, validate=False, lazy_loading=True)
        for i, v in enumerate(copy):
            if isinstance(v, CollectionProtocol):
                copy[i] = v.copy(_parents=_parents + ((self, copy), ))
        copy.do_validate()
        return copy

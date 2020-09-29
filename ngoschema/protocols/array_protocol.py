# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import MutableSequence
import six
import logging

from ..exceptions import InvalidValue
from ..types import Array
from .collection_protocol import CollectionProtocol, TypeProtocol, value_opts
from ..types.constants import _True
from ..decorators import classproperty
from ..utils import shorten
from ..managers.namespace_manager import default_ns_manager
from .. import settings, DEFAULT_CONTEXT
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
    _data = []
    _data_validated = []
    _items_inputs = []

    def __init__(self, value=None, items=None, context=None, session=None, **kwargs):
        value, opts = value_opts(value, **kwargs)
        CollectionProtocol.__init__(self, value, items=items, context=context, session=session, **opts)
        if self._has_pk:
            for v in self:
                v.identity_keys

    def _item_touch(self, item):
        CollectionProtocol._item_touch(item)
        for d, s in self._dependencies.items():
            if item in s:
                self._item_touch(d)

    def _touch(self):
        CollectionProtocol._touch(self)
        self._data_validated = [None] * len(self._data)
        self._items_inputs = [{}] * len(self._data)

    @classmethod
    def item_type(cls, item):
        from .type_proxy import TypeProxy
        if cls._item_type_cache is None:
            if not cls._items_list:
                if isinstance(cls._items, TypeProxy):
                    if cls._items.proxy_type:
                        cls._items = cls._items.proxy_type
                        cls._item_type_cache = cls._items
                else:
                    cls._item_type_cache = cls._items
            else:
                ok = True
                for i, t in enumerate(cls._items):
                    if isinstance(t, TypeProxy):
                        if t.proxy_type:
                            cls._items[i] = t.proxy_type
                        else:
                            ok = False
                if ok:
                    cls._item_type_cache = cls._items
        return Array.item_type(cls, item)

    @classmethod
    def check(cls, value, **opts):
        if isinstance(value, cls) or cls._check(cls, value):
            return True
        if cls._items is not None and cls._items.check(value):
            # this is for arrays not properly initialized by loading xml for ex
            return True
        return False

    #def _set_data(self, index, value):
    #    from ..models import Entity
    #    itype = Array.item_type(self, index)
    #    if issubclass(itype, Entity) and value is not None and not Object.check(value):
    #        obj = self.session.resolve_fkey(value, itype)
    #        assert obj
    #        value = obj
    #    if Literal.check(value) and value != self._data.get(index):
    #        self.touch(index)
    #    self._data[index] = value

    def __len__(self):
        return len(self._data)

    def insert(self, item, value):
        self._items_inputs.insert(item, {})
        self._data_validated.insert(item, None)
        self._data.insert(item, value)
        if not self._lazy_loading:
            self._items_inputs[item] = self._item_inputs_evaluate(item)
            self._set_data_validated(item, self._item_evaluate(item))
        elif isinstance(value, TypeProtocol):
            value.set_context(self._context)
        self.do_validate(items=False)

    def _str_list(self):
        if self._str is None:
            hidden = max(0, len(self) - settings.PPRINT_MAX_EL)
            a = [shorten(self._data_validated[i] or self._data[i], str_fun=repr) for i, t in enumerate(self._item_types(self))
                 if i < settings.PPRINT_MAX_EL] + (['+%i...' % hidden] if hidden else [])
            self._str = '[%s]' % (', '.join(a))
        return self._str

    def __repr__(self):
        return '%s(%s)' % (self.qualname(), ArrayProtocol._str_list(self))

    def __str__(self):
        return ArrayProtocol._str_list(self)

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from ..contexts import object_contexts
        from ..managers.type_builder import TypeBuilder
        attrs = attrs or {}
        cname = default_ns_manager.get_id_cname(id)
        clsname = cname.split('.')[-1]
        logger = logging.getLogger(cname)
        items = schema.get('items')
        items_list = False
        lz = schema.get('lazyLoading', False)
        if items:
            if Array.check(items):
                items_list = True
                items = [TypeBuilder.build(f'{id}/items/{i}', item) for i, item in enumerate(items)]
            else:
                items = TypeBuilder.build(f'{id}/items', items)
                lz = lz or getattr(items, '_lazy_loading', False)
        else:
            items = TRUE
        if not any([issubclass(b, ArrayProtocol) for b in bases]):
            bases = list(bases) + [ArrayProtocol]
        if 'validate' in schema:
            attrs['_validate'] = schema['validate']
        attrs.setdefault('_lazy_loading', lz)
        attrs['_items'] = items
        attrs['_min_items'] = schema.get('minItems', 0)
        attrs['_max_items'] = schema.get('maxItems')
        attrs['_unique_items'] = schema.get('uniqueItems', False)
        attrs['_default_cache'] = None
        attrs['_has_pk'] = bool(any(len(getattr(t, '_primary_keys', [])) for t in items)\
                                    if items_list else len(getattr(items, '_primary_keys', [])))
        attrs['_items_list'] = items_list
        attrs['_schema'] = schema
        attrs['_logger'] = logger
        attrs['_id'] = id
        cls = type(clsname, tuple(bases), attrs)
        cls._py_type = cls
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

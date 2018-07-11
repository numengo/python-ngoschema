# *- coding: utf-8 -*-
"""
Base class for loading objects from files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import itertools
import operator

from . import utils
from .classbuilder import get_descendant


class Query(object):
    _result_cache = None

    def __init__(self, iterable, distinct=False, order_by=False):
        self._iterable = iterable
        self._distinct = distinct
        self._order_by = order_by
        self._seen = set()

    @staticmethod
    def _comparable(obj):
        return obj.for_json() if hasattr(obj, "for_json") else obj

    def _select_or_reject(self,
                          load_lazy=False,
                          select=True,
                          *attrs,
                          **attrs_value):
        """
        Make a generator for an iterable. The flag `select` allow to return 
        the selected or rejected objects corresponding to the criteria

        Criteria on descendant attributes are done with the syntax `child__childOfChild`.
        The last elements of a criteria can be an operator as [lt, le, eq, ne, ge, gt, in] (
        default is `eq`)
        ex: `child__numElements__ge = 5` will select objects with an attribute named `child`
        with an attribute `numElements` greater or equal to 5

        :param iterable: iterable to process
        :param attrs: select/reject objects with given attributes defined
        :param load_lazy: in case of lazy loaded object, force loading
        :param select: returns the selected/rejected objects corresponding to the query
        :param distinct: flag to only returns distinct objects
        :param attrs_value: select/objects objects with given attribute/value pairs
        """
        for obj in self._iterable:
            for k, v2 in attrs_value.items():
                op = 'eq'
                if '__' in k:
                    ks = k.split('__')
                    if ks[-1] in ['lt', 'le', 'eq', 'ne', 'ge', 'gt', 'in']:
                        op = ks[-1]
                        ks.pop()
                else:
                    ks = [k]
                o = get_descendant(obj, ks, load_lazy)
                if o is None:
                    break
                v = self._comparable(o)
                if op not in ['in'] and not getattr(operator, op)(v, v2):
                    if select:
                        break
                elif op == 'in' and not v in v2:
                    if select:
                        break
            else:
                for k in attrs:
                    ks = k.split('__')
                    if get_descendant(obj, ks, load_lazy):
                        if select:
                            break
                else:
                    if self._distinct:
                        comparable = self._comparable(obj)
                        if comparable not in self._seen:
                            self._seen.add(comparable)
                        else:
                            continue
                    yield obj

    def select(self,
               load_lazy=False,
               order_by=False,
               distinct=False,
               *attrs,
               **attrs_value):
        return Query(
            self._select_or_reject(
                load_lazy=load_lazy, select=True, *attrs, **attrs_value),
            order_by=order_by or self._order_by,
            distinct=distinct or self._distinct)

    def reject(self,
               load_lazy=False,
               order_by=False,
               distinct=False,
               *attrs,
               **attrs_value):
        return Query(
            self._select_or_reject(
                load_lazy=load_lazy, select=False, *attrs, **attrs_value),
            order_by=order_by or self._order_by,
            distinct=distinct or self._distinct)

    def __iter__(self):
        return self._iterable

    def _cache_result(self):
        self._result_cache = list(self._iterable)

        if self._order_by:
            ks = self._order_by.split('__')
            self._result_cache = sorted(self._result_cache,
                                        lambda x: get_descendant(x, ks))

    def __getitem__(self, k):
        """Retrieve an item or slice from the set of results."""
        if not isinstance(k, (int, slice)):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        if self._result_cache is None:
            self._cache_result()

        return self._result_cache[k]

    def __len__(self):
        return len(self.all())

    def __contains__(self, obj):
        v = self._comparable(obj)
        for o in self:
            if self._comparable(o) == v:
                return True
        return False

    def all(self):
        """
        Return all results of query set
        """
        if self._result_cache is None:
            self._cache_result()
        return self._result_cache

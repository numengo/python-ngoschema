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
import re

from . import utils
from .classbuilder import get_descendant

_operators = [
# operator library
'lt', 'le', 'eq', 'ne', 'ge', 'gt', 'contains',
# redefined
'in', 'size', 'intersects',
# string and regex
'ieq', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex'
]

def _comparable(obj):
    return obj.for_json() if hasattr(obj, "for_json") else obj

def _sort_criteria(criteria):
    elts = criteria.split('__')
    ops = []
    for e in reversed(elts):
        if e not in _operators and not e.startswith('@'):
            break
        ops.insert(0, e)
        elts.pop()
    return elts, ops

def _apply_ops_test(ops, a, b):
    def _apply_op(op, a, b):
        if hasattr(operator, op):
            return getattr(operator, op)(a, b)
        if op == 'size':
            return len(a)
        if op.startswith('@'):
            return a[int(op[1:])]
        if op == 'in':
            return a in b
        if op == 'intersects':
            return set(a).intersection(set(b))
        if op == 'startswith':
            return a.startswith(b)
        if op == 'endswith':
            return a.endswith(b)
        if op == 'ieq':
            return re.match('^%s$'%b, a, re.IGNORECASE)
        if op == 'istartswith':
            return re.match('^%s'%b, a, re.IGNORECASE)
        if op == 'iendswith':
            return re.match('%s$'%b, a, re.IGNORECASE)
        if op == 'icontains':
            return re.match('%s'%b, a, re.IGNORECASE)
        if op == 'regex':
            return re.match(b, a)
    try:
        for op in ops:
            a = _apply_op(op, a, b)
        return a
    except:
        return False

class Query(object):
    _result_cache = None

    def __init__(self, iterable, distinct=False, order_by=False):
        self._iterable = iterable
        self._distinct = distinct
        self._order_by = order_by
        self._seen = set()

    def _chain(self):
        return Query(self._iterable, self._distinct, self._order_by)

    def _filter_or_exclude(self,
                          load_lazy=False,
                          negate=False,
                          *attrs,
                          **attrs_value):
        """
        Make a generator for an iterable. The flag `negate` allow to return 
        the excluded objects corresponding to the criteria

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
                ks, ops = _sort_criteria(k)
                o = get_descendant(obj, ks, load_lazy)
                if o is None:
                    break
                elif ops and utils.is_mapping(o):
                    # check if it s not a child
                    ops2 = ops
                    for op in ops2:
                        o2 = get_descendant(o, op, load_lazy)
                        if o2:
                            o = o2
                            ks.append(ops.pop(0))
                        else:
                            break
                ops = ops or ['eq']
                v = _comparable(o)
                if not _apply_ops_test(ops, v, v2) and not negate:
                    break
            else:
                for k in attrs:
                    ks = k.split('__')
                    if get_descendant(obj, ks, load_lazy):
                        if not negate:
                            break
                else:
                    if self._distinct:
                        comparable = _comparable(obj)
                        if comparable not in self._seen:
                            self._seen.add(comparable)
                        else:
                            continue
                    yield obj

    def filter(self,
               load_lazy=False,
               order_by=False,
               distinct=False,
               *attrs,
               **attrs_value):
        return Query(
            self._filter_or_exclude(
                load_lazy=load_lazy, *attrs, **attrs_value),
            order_by=order_by or self._order_by,
            distinct=distinct or self._distinct)

    def exclude(self,
               load_lazy=False,
               order_by=False,
               distinct=False,
               *attrs,
               **attrs_value):
        return Query(
            self._filter_or_exclude(
                load_lazy=load_lazy, negate=True, *attrs, **attrs_value),
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
        return self._result_cache

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
        v = _comparable(obj)
        for o in self:
            if _comparable(o) == v:
                return True
        return False

    def union(self, *others):
        res = self._cache_result()
        for o in others:
            res += o._cache_result()
        return Query(res, self._distinct, self._order_by)

    def intersection(self, *others):
        res = self._cache_result()
        for o in others:
            ores = o._cache_result()
            res = [r for r in res if r in ores]
        return Query(res, self._distinct, self._order_by)

    def difference(self, *others):
        res = self._cache_result()
        for o in others:
            ores = o._cache_result()
            res = [r for r in res if r not in ores]
        return Query(res, self._distinct, self._order_by)

    def get(self, load_lazy=False, *attrs, **attrs_value):
        ret = list(self._filter_or_exclude( load_lazy=load_lazy, *attrs, **attrs_value))
        if len(ret)==0:
            raise Exception('Entry does not exist')
        elif len(ret)>1:
            raise Exception('Multiple objects returned')
        return ret[0]
            

    def first(self):
        try:
            return self[0]
        except IndexError:
            return None

    def last(self):
        try:
            return self[-1]
        except IndexError:
            return None

    def reverse(self):
        ret = self._chain()
        ret._iterable = reversed(self._cache_result())
        return ret
    
    def count(self):
        return len(self)

    def order_by(self, order_by):
        return Query(self._iterable, self._distinct, order_by)

    def all(self):
        """
        Return all results of query set
        """
        if self._result_cache is None:
            self._cache_result()
        return self._result_cache

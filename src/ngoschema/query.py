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

from python_jsonschema_objects.literals import LiteralValue

from . import utils
from .protocol_base import get_descendant, ProtocolBase
from .canonical_name import CN_KEY

_operators = [
    # operator library
    'lt',
    'le',
    'eq',
    'ne',
    'neq',
    'ge',
    'gt',
    'not',
    'contains',
    # redefined
    'in',
    'size',
    'intersects',
    # string and regex
    'ieq',
    'icontains',
    'startswith',
    'istartswith',
    'endswith',
    'iendswith',
    'regex'
]


def _comparable(obj):
    if isinstance(obj, ProtocolBase):
        #obj = obj[CN_KEY]
        obj = str(obj.canonicalName)
    if isinstance(obj, LiteralValue):
        return obj.for_json()
    return obj


def _sort_criteria(criteria):
    elts = criteria.split('__')
    ops = []
    for e in reversed(elts):
        if e not in _operators and not e.startswith('@'):
            break
        ops.insert(0, e)
        elts.pop()
    return elts, ops


def _apply_ops_test(ops, negate, a, b):
    def _apply_op(op, a, b):
        if op in ('startswith', 'endswith', 'ieq', 'istartswith', 'iendswith', 'icontains', 'regex'):
            if not utils.is_string(a):
                raise TypeError("%s requires a string (%s not a string)" % (op, a))
            if not utils.is_string(b):
                raise TypeError("%s requires a string (%s not a string)" % (op, b))
        if hasattr(operator, op):
            return getattr(operator, op)(a, b)
        if op == 'neq':
            return a != b
        if op == 'size':
            return len(a)
        if op.startswith('@'):
            return a[int(op[1:])]
        if op == 'in':
            return a in b
        if op == 'intersects':
            if not utils.is_sequence(a):
                raise TypeError("%s requires a sequence (%s not a sequence)" % (op, a))
            if not utils.is_sequence(b):
                raise TypeError("%s requires a sequence (%s not a sequence)" % (op, b))
            return set(a).intersection(set(b))
        if op == 'startswith':
            return a.startswith(b)
        if op == 'endswith':
            return a.endswith(b)
        if op == 'ieq':
            return re.match('^%s$' % b, a, re.IGNORECASE)
        if op == 'istartswith':
            return re.match('^%s' % b, a, re.IGNORECASE)
        if op == 'iendswith':
            return re.match('%s$' % b, a, re.IGNORECASE)
        if op == 'icontains':
            return re.search('%s' % b, a, re.IGNORECASE)
        if op == 'regex':
            return re.match(b, a)

    for op in ops:
        a = _apply_op(op, a, b)
    return not a if negate else a


class Query(object):

    def __init__(self, iterable, distinct=False, order_by=False, reverse=False):
        """
        :param iterable: iterator on which to perform the query
        :param distinct: flag to only return distinct objects
        :type distinct: boolean
        :param order_by: column to use for order
        :type order_by: string
        :param reverse: boolean to reverse order
        :type reverse: boolean
        """
        self._iterable = iterable
        self._distinct = distinct
        self._order_by = order_by
        self._reverse = reverse

    def _chain(self):
        return Query(self._iterable, self._distinct, self._order_by, self._reverse)

    @staticmethod
    def _filter_or_exclude(iterable,
                           *attrs,
                           load_lazy=False,
                           negate=False,
                           any_of=False,
                           distinct=False,
                           **attrs_value):
        """
        Make a filter/exclude generator for an iterable. The flag `negate` allow to return 
        the excluded objects corresponding to the criteria. This generator filters/excludes
        objects respecting ANY of the criteria (OR).

        Criteria on descendant attributes are done with the syntax `child__childOfChild`.
        The last elements of a criteria can be an operator as [lt, le, eq, ne, ge, gt, in] (
        default is `eq`)
        ex: `child__numElements__ge = 5` will select objects with an attribute named `child`
        with an attribute `numElements` greater or equal to 5

        :param iterable: iterable to process
        :param load_lazy: in case of lazy loaded object, force loading
        :param attrs: select/reject objects with given attributes defined
        :param attrs_value: select/objects objects with given attribute/value pairs
        """
        seen = set()
        attrs_ops = {}
        for k, v2 in attrs_value.items():
            ks, ops = _sort_criteria(k)
            ops_negate = 'not' in ops
            if ops_negate:
                ops.remove('not')
            attrs_ops[k] = (ks, ops, ops_negate)

        for obj in iterable:
            if not obj:
                continue
            test = not any_of
            for k, v2 in attrs_value.items():
                ks, ops, ops_negate = attrs_ops[k]
                o = get_descendant(obj, ks, load_lazy)
                if o is None:
                    # breaking the look we never go in the for/ELSE statement where 
                    # an object is potentially yielded
                    test = False
                    break
                elif ops and utils.is_mapping(o):
                    # check if it s not a child
                    for op in ops:
                        o2 = get_descendant(o, op, load_lazy)
                        if o2:
                            o = o2
                            ks.append(ops.pop(0))
                        else:
                            test = False
                            break
                ops = ops or ['eq']
                v = _comparable(o)
                test2 = bool(_apply_ops_test(ops, ops_negate, v, v2))
                test = (test or test2) if any_of else (test and test2)
                if any_of:
                    if test2:
                        break
                elif not test:
                    break            

            for k in attrs:
                ks = k.split('__') 
                test2 = get_descendant(obj, ks, load_lazy) is not None
                test = (test or test2) if any_of else (test and test2)
                if any_of:
                    if test2:
                        break
                elif not test:
                    break
            if test is not negate:
                if distinct:
                    comparable = _comparable(obj)
                    if comparable not in seen:
                        seen.add(comparable)
                    else:
                        continue
                yield obj

    def filter(self,
               *attrs,
               load_lazy=None,
               order_by=None,
               reverse=None,
               distinct=None,
               **attrs_value):
        return Query(
                (x for x in Query._filter_or_exclude(self._iterable, *attrs, 
                                                    load_lazy=load_lazy, 
                                                    distinct=distinct or self._distinct,
                                                    **attrs_value)),
                order_by=order_by or self._order_by,
                reverse=reverse or self._reverse,
                distinct=distinct or self._distinct)

    def exclude(self,
               *attrs,
                load_lazy=None,
                order_by=None,
                reverse=None,
                distinct=None,
                **attrs_value):
        return Query(
                (x for x in Query._filter_or_exclude(self._iterable, *attrs, 
                                                    load_lazy=load_lazy, 
                                                    negate=True, 
                                                    distinct=distinct or self._distinct,
                                                    **attrs_value)),
                order_by=order_by or self._order_by,
                reverse=reverse or self._reverse,
                distinct=distinct or self._distinct)

    def filter_any_of(self,
               *attrs,
               load_lazy=None,
               order_by=None,
               reverse=None,
               distinct=None,
               **attrs_value):
        return Query(
                (x for x in Query._filter_or_exclude(self._iterable, *attrs, 
                                                    load_lazy=load_lazy, 
                                                    any_of=True,
                                                    distinct=distinct or self._distinct,
                                                    **attrs_value)),
                order_by=order_by or self._order_by,
                reverse=reverse or self._reverse,
                distinct=distinct or self._distinct)

    def exclude_any_of(self,
                *attrs,
                load_lazy=None,
                order_by=None,
                reverse=None,
                distinct=None,
                **attrs_value):
        return Query(
                (x for x in Query._filter_or_exclude(self._iterable, *attrs, 
                                                    load_lazy=load_lazy, 
                                                    any_of=True, 
                                                    negate=True, 
                                                    distinct=distinct or self._distinct,
                                                    **attrs_value)),
                order_by=order_by or self._order_by,
                reverse=reverse or self._reverse,
                distinct=distinct or self._distinct)

    def __iter__(self):
        return (x for x in self.result_cache)

    _result_cache = None
    @property
    def result_cache(self):
        if self._result_cache is None:
            self._result_cache = list(self._iterable)

            if self._order_by:
                ks = self._order_by.split('__')
                self._result_cache = sorted(self._result_cache,
                                            lambda x: get_descendant(x, ks))
            if self._reverse:
                self._result_cache = reversed(self._result_cache)
        return self._result_cache

    def __getitem__(self, k):
        """Retrieve an item or slice from the set of results."""
        if not isinstance(k, (int, slice)):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        return self.result_cache[k]

    def __len__(self):
        return len(self.result_cache)

    def __contains__(self, obj):
        v = _comparable(obj)
        for o in self:
            if _comparable(o) == v:
                return True
        return False

    def union(self, *others):
        res = self.result_cache
        for o in others:
            res += o.result_cache
        return Query(res, self._distinct, self._order_by)

    def intersection(self, *others):
        res = self.result_cache
        for o in others:
            ores = o.result_cache
            res = [r for r in res if r in ores]
        return Query(res, self._distinct, self._order_by)

    def difference(self, *others):
        res = self.result_cache
        for o in others:
            ores = o.result_cache
            res = [r for r in res if r not in ores]
        return Query(res, self._distinct, self._order_by)

    def get(self, *attrs, load_lazy=False, **attrs_value):
        ret = list(Query._filter_or_exclude(self._iterable,
                                        *attrs, 
                                        load_lazy=load_lazy,
                                        distinct=self._distinct,
                                        **attrs_value))
        if len(ret) == 0:
            raise Exception('Entry %s does not exist' % attrs_value)
        elif len(ret) > 1:
            import logging
            logging.error(ret)
            raise Exception('Multiple objects returned')
        return ret[0]

    def next(self, *attrs, load_lazy=False, **attrs_value):
        return next(
                Query._filter_or_exclude(self._iterable,
                                         *attrs, 
                                         distinct=self._distinct,
                                         load_lazy=load_lazy, 
                                         **attrs_value))

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
        ret._iterable = reversed(self.result_cache)
        return ret

    def count(self):
        return len(self)

    def order_by(self, order_by, reverse=False):
        return Query(self._iterable, self._distinct, order_by, reverse=reverse)

    def all(self):
        """
        Return all results of query set
        """
        return self.result_cache

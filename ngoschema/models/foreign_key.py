# *- coding: utf-8 -*-
"""
Foreign key component

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 28/01/2019
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import weakref
import sys

from python_jsonschema_objects.wrapper_types import ArrayWrapper
from .relationship import  Relationship
from ..decorators import classproperty
from ..mixins import HasCache, HasLogger
from ..literals import LiteralValue


class ForeignKey(LiteralValue, Relationship, HasLogger):
    _keys = None
    _foreignClass = None
    _ref = None
    _value = None
    #_validated = False

    @classmethod
    def _propinfo(cls, name, default=None):
        return cls.__propinfo__.get('foreignKey', {}).get(name, default)

    @classproperty
    def backPopulates(cls):
        return cls._propinfo('backPopulates', False)

    @classproperty
    def onDelete(cls):
        return cls._propinfo('onDelete')

    @classproperty
    def key(cls):
        return cls._propinfo('key', 'canonicalName')

    @classproperty
    def fkeys(cls):
        return [cls.key]

    def __init__(self, value, _parent=None):
        # todo: handle relative cnames/refs
        deps = self.propinfo('dependencies') or set()
        deps.add(self.key)
        HasCache.__init__(self, context=_parent, inputs=deps)
        self._value = None
        self._ref = None
        self._dirty = False
        if value is None:
            return
        if isinstance(value, self.foreignClass):
            self._set_ref(value)
            self._value = value._get_prop_value(self.key)
        elif isinstance(value, ForeignKey):
            self._set_ref(value._ref() if value._ref else None)
            self._value = value._value
            self._dirty = value._dirty
        else:
            self._value = value.for_json() if hasattr(value, 'for_json') else value

    def resolve(self):
        if self._ref:
            return self._ref()
        if self._value is None:
            return
        key, val = self.key, self._value
        for i in self.foreignClass._instances:
            ival = str(i.get(key))
            if not ival:
                continue
            if ival == val:
                self._set_ref(i)
                return i
        else:
            # not instanciated yet (lazy loading?)
            # look for a common ancestor
            ancs = self._value.split('.')
            from ngoschema.models.entity import NamedEntity
            for i in NamedEntity._instances:
                ival = str(i.get(key))
                iancs = ival.split('.')
                comm = []
                for a, ia in zip(ancs, iancs):
                    if a!=ia: break
                    comm.append(a)
                if comm:
                    ancestor = '.'.join(comm)
                    cur = i
                    while cur:
                        if cur.get(key) == ancestor:
                            break
                        cur = cur._parent
                    assert cur, ancestor
                    path2 = cur.resolve_cname(self._value)
                    for p in path2:
                        cur = cur[p]
                    self._set_ref(cur)
                    return cur
        raise ValueError("Impossible to resolve reference '%s'" % self._value)

    def _set_ref(self, instance):
        if instance is not None:
            self._ref = weakref.ref(instance)
            bp = self.backPopulates
            if bp:
                key = bp['fkeys'][0] if 'fkeys' in bp else bp.get('fkey', 'canonicalName')
                backref = instance[key]
                if self.isOne2Many:
                    if self._value not in backref:
                        instance[key] = list(backref) + [self._value]
                else:
                    instance[key] = [self._value] if isinstance(backref, ArrayWrapper) else self._value

    ref = property(resolve, _set_ref)


class CnameForeignKey(ForeignKey):

    @classproperty
    def key(cls):
        return 'canonicalName'

    def __init__(self, value, _parent=None):
        # todo: handle relative cnames/refs
        ForeignKey.__init__(self, value, _parent=_parent)

    def validate(self):
        if self._value:
            LiteralValue.validate(self)
        # literal value is validated, now let s see if it corresponds to reference
        if self._ref and self._ref():
            ref = self._ref()
            self._value = ref._cname
        assert self._value or self._ref is None

    def resolve(self):
        if self._ref:
            return self._ref()
        if self._value is None:
            return
        try:
            ref = self._context.resolve_cname(self._value)
            self._set_ref(ref)
            return ref
        except Exception as er:
            raise ValueError("Impossible to resolve canonical name '%s'.\n%s" % (self._value, sys.exc_info()[2]))

    ref = property(resolve, ForeignKey._set_ref)

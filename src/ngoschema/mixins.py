# *- coding: utf-8 -*-
"""
Project definition and main actions

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import weakref
from python_jsonschema_objects.classbuilder import LiteralValue
from .decorators import classproperty

class HasName:

    _name = None
    def set_name(self, value):
        self._name = str(value) if value else None

class HasParent:

    _parent_ref = None
    _children_dict = None

    def _set_parent(self, value):
        if value is None:
            if self._parent_ref and self._parent_ref():
                self._parent_ref()._unregister_child(self)
                self._parent_ref = None
        from .foreign_key import ForeignKey
        if isinstance(value, ForeignKey):
            self._parent_ref = value._ref
        if isinstance(value, HasParent):
            self._parent_ref = weakref.ref(value)
        self._parent_ref()._register_child(self)

    def _get_parent(self):
        return self._parent_ref() if self._parent_ref else None

    _parent = property(_get_parent, _set_parent)

    def _get_parents(self):
        cur = self._parent
        ret = []
        while cur:
            ret.append(cur)
            cur = cur._parent
        return ret

    _parents = property(_get_parents)

    def _register_child(self, child):
        # not using set because we need to remove an instance without deleting it
        # WeakSet.remove does not allow
        if self._children_dict is None:
            self._children_dict = weakref.WeakValueDictionary()
        self._children_dict[id(child)] = child

    def _unregister_child(self, child):
        self._children_dict.pop(id(child))

    def _get_children(self):
        return [wr() for wr in self._children_dict.valuerefs()] if self._children_dict else []

    def _touch_children(self):
        for c in self._children:
            c._touch_children()

    _children = property(_get_children)


class HasCanonicalName(HasName, HasParent):
    _cn_instances = weakref.WeakValueDictionary()

    def set_name(self, value):
        value = value.replace('-', '_')
        n = str(value) if value else None
        if self._name != n:
            self._unregister_cnamed()
            HasName.set_name(self, n)
            self._register_cnamed()

    def _set_parent(self, value):
        if self._parent is not value:
            self._unregister_cnamed()
            HasParent._set_parent(self, value)
            self._register_cnamed()

    _canonicalName = None
    def set_canonicalName(self, value):
        value = value.replace('-', '_')
        cn = str(value) if value else None
        if self._cname != cn:
            self._unregister_cnamed()
            self._canonicalName = cn
            self._register_cnamed()

    _cnam = None
    @property
    def _cname(self):
        if self._cnam is None:
            par = self._parent
            par_cn = None
            while par and not self._canonicalName:
                if isinstance(par, HasCanonicalName):
                    par_cn = par._cname
                    break
                par = par._parent
            self._cnam = self._canonicalName or \
                 '%s.%s' % (par_cn, self._name or '') if par_cn else self._name
        return self._cnam

    def _touch_children(self):
        self._cnam = None # reset canonical name cache
        HasParent._touch_children(self)

    def _register_child(self, child):
        HasParent._register_child(self, child)
        child._touch_children()

    def _unregister_child(self, child):
        HasParent._unregister_child(self, child)
        child._touch_children()

    def _register_cnamed(self):
        self._cn_instances[self._cname] = self

    def _unregister_cnamed(self):
        self._cn_instances.pop(self._cname, None)
        self._touch_children()

    @classmethod
    def resolve_cname(cls, cname):
        from .wrapper_types import ArrayWrapper
        cn = str(cname)
        ret = cls._cn_instances.get(cn)
        if ret:
            return ret()
        best_ancestor = None
        pstack = []
        while best_ancestor is None and '.' in cn:
            cn, _ = cn.rsplit('.', 1)
            pstack.append(_)
            best_ancestor = cls._cn_instances.get(cn)
        if best_ancestor is None:
            raise Exception('Unresolvable canonical name %s' % (cname))
        cur = best_ancestor
        while pstack:
            n = pstack.pop(-1)
            try:
                ch = next(c for c in cur._children if getattr(c, '_name', None) == n)
                if not pstack:
                    return ch
            except Exception as er:
                pstack.append(n)
                ch = None
            cur = ch or cur
            if ch is None:
                from . import canonical_name
                pstack.append(cur._name)
                pstack.reverse()
                _, path = canonical_name.resolve_cname_path(pstack, cur._lazy_data)
                for p in path:
                    cur = cur[p]
                return cur
        raise Exception('Unresolvable canonical name %s in %s' % (cname, best_ancestor._cname))


class RootRelativeCname:

    def resolve_relative_cname(self, value):
        val =  str(value)
        return '%s.%s' % (self._cname, val[1:]) if val[0]=='#' else val

    def get_relative_cname(self, child):
        base = '%s.' % self._cname
        return child._cname.replace(base, '#')


class HandleRelativeCname:

    _root = None
    @property
    def _root_parent(self):
        if not self._root:
            par = self._parent
            while par:
                if isinstance(par, RootRelativeCname):
                    self._root = weakref.ref(par)
                    return par
                par = par._parent
            self._root = weakref.ref(self)
        return self._root() if self._root else self

    @property
    def relativeCanonicalName(self):
        pcn = self._root_parent._cname
        return self._cname.replace('%s.' % pcn, '#')

    def _clean_cname(self, value):
        val = str(value)
        if val.startswith('#'):
            return self._root_parent.resolve_relative_cname(val)
        return val


class HasCache:
    _context = None
    _cache = None
    _inputs = set()
    _outputs = set()

    def __init__(self, *args, **kwargs):
        self._dirty = True
        self._inputs = set()
        self._outputs = set()

    def __eq__(self, other):
        if not isinstance(other, HasCache):
            return True
        iprops = self._input_props
        oprops = other._input_props
        if iprops.keys() != oprops.keys():
            return False
        for k, v in iprops.items():
            if v != oprops[k]:
                return False
        return True

    def _set_context(self, context):
        self._context = weakref.ref(context)

    def _set_inputs(self, *inputs):
        self._inputs = set(inputs)

    def _add_inputs(self, *inputs):
        self._inputs.update(inputs)

    def _set_outputs(self, *outputs):
        self._outputs = set(outputs)

    def _add_outputs(self, *outputs):
        self._outputs.update(outputs)

    def __prop(self, key):
        from .protocol_base import ProtocolBase
        from .foreign_key import ForeignKey
        cur = self._context()
        return getattr(cur, key, None)
        return cur.get(key, None)
        #for k in key.split('.'):
        #    if isinstance(cur, ForeignKey):
        #        cur = cur.ref
        #    if not isinstance(cur, ProtocolBase):
        #        return
        #    cur = cur.get(k)
        #    #cur = cur.get(k, None)
        #return cur

    @property
    def _input_props(self):
        return {} if not self._context else {
            k: self.__prop(k)
            for k in self._inputs
            if self.__prop(k)
        }

    @property
    def _output_props(self):
        return {} if not self._context else {
            k: self.__prop(k)
            for k in self._outputs
            if self.__prop(k)
        }

    def __prop_value(self, key):
        val = self._context()._get_prop_value(key)
        return val.for_json() if isinstance(val, LiteralValue) else val

    def _input_values(self):
        return {} if not self._context else {
            k: self.__prop_value(k)
            for k in self._inputs
        }

    def is_dirty(self):
        return self._dirty or (self._cache != self._input_values())

    def set_clean(self, recursive=False):
        self._dirty = False
        self._cache = self._input_values()

    def touch(self, recursive=False):
        self._dirty = True
        if recursive:
            for k, p in self._output_props.items():
                p.touch()

    def do_validate(self, force=False):
        for k, p  in self._input_props.items():
            p.do_validate(force)

        if self._dirty or force:
            from .wrapper_types import ArrayWrapper
            if not isinstance(self, ArrayWrapper):
                self.set_clean()
            self.validate()
            self.set_clean()

    # add a _validated property for compatiblity with Literals
    def get_validated(self):
        return not self._dirty

    def set_validated(self, value):
        if value:
            self.set_clean()
        else:
            self.touch()
    _validated = property(get_validated, set_validated)


class HasInstanceQuery:

    @classmethod
    def one(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves exactly one instance corresponding to query

        Query can used all usual operators"""
        from .query import Query
        ret = list(
            Query(cls._instances)._filter_or_exclude(
                *attrs, load_lazy=load_lazy, **attrs_value))
        if len(ret) == 0:
            raise ValueError('Entry %s does not exist' % attrs_value)
        elif len(ret) > 1:
            import logging
            cls.logger.error(ret)
            raise ValueError('Multiple objects returned')
        return ret[0]

    @classmethod
    def one_or_none(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves exactly one instance corresponding to query

        Query can used all usual operators"""
        from .query import Query
        ret = list(
            Query(cls._instances)._filter_or_exclude(
                *attrs, load_lazy=load_lazy, **attrs_value))
        if len(ret) == 0:
            return None
        elif len(ret) > 1:
            import logging
            cls.logger.error(ret)
            raise ValueError('Multiple objects returned')
        return ret[0]

    @classmethod
    def first(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves exactly one instance corresponding to query

        Query can used all usual operators"""
        from .query import Query
        return next(
            Query(cls._instances).filter(
                *attrs, load_lazy=load_lazy, **attrs_value))

    @classmethod
    def filter(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves a list of instances corresponding to query

        Query can used all usual operators"""
        from .query import Query
        return list(
            Query(cls._instances).filter(
                *attrs, load_lazy=load_lazy, **attrs_value))

    @classproperty
    def _instances(cls):
        return (v() for v in cls.__instances__.valuerefs() if v())

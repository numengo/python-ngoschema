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


class HasParent:

    _parent_ref = None
    _children_dict = None

    def _set_parent(self, value):
        if value is None:
            if self._parent_ref and self._parent_ref():
                self._parent_ref._children_dict.pop(id(self))
                self._parent_ref = None
            return
        from .foreign_key import ForeignKey
        if isinstance(value, ForeignKey):
            self._parent_ref = value._ref
        if isinstance(value, HasParent):
            self._parent_ref = weakref.ref(value)
        self._parent_ref().register_child(self)

    def _get_parent(self):
        return self._parent_ref() if self._parent_ref else None

    _parent = property(_get_parent, _set_parent)

    def register_child(self, child):
        if self._children_dict is None:
            self._children_dict = weakref.WeakValueDictionary()
        self._children_dict[id(child)] = child

    def _get_children(self):
        return [wr() for wr in self._children_dict.valuerefs()]

    _children = property(_get_children)

class RootRelativeCname:

    def resolve_relative_cname(self, value):
        val =  str(value)
        return '%s.%s' % (self.canonicalName, val[1:]) if val[0]=='#' else val

    def get_relative_cname(self, child):
        base = '%s.' % self.canonicalName
        return str(child.canonicalName).replace(base, '#')

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
            raise ValueError("impossible to resolve reference for relative canonical name in %s", self.__class__)
        return self._root() if self._root else None

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
        for k in key.split('.'):
            if isinstance(cur, ForeignKey):
                cur = cur.ref
            if not isinstance(cur, ProtocolBase):
                return
            cur = cur.get(k)
            #cur = cur.get(k, None)
        return cur

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
        #return self._dirty or any((p.is_dirty() for p in self._input_props.values()))

    def set_clean(self, recursive=False):
        self._dirty = False
        self._cache = self._input_values()
        #if recursive:
        #    for o in self._outputs:
        #        o.set_clean()
    
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

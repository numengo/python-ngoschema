# *- coding: utf-8 -*-
"""
Project definition and main actions

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import weakref
import re
from python_jsonschema_objects.literals import LiteralValue
from python_jsonschema_objects.wrapper_types import ArrayWrapper

from ..decorators import memoized_property
from .. import utils

class HasLogger:
    logger = None

    @classmethod
    def init_class_logger(cls):
        from .. import utils
        # not using the cls_fullname property because it s too early for some meta
        cls.logger = logging.getLogger(utils.fullname(cls))
        cls.set_logLevel(cls.__log_level__)

    @classmethod
    def set_logLevel(cls, logLevel):
        if not getattr(cls, 'logger', None):
            cls.init_class_logger()
        level = logging.getLevelName(logLevel)
        cls.__log_level__ = level
        cls.logger.setLevel(level)


class HasName:
    _name = None

    def set_name(self, value):
        self._name = str(value) if value else None


class HasParent:

    _parent_ref = None
    _children_dict = None

    def _set_parent(self, value):
        if value is None:
            if self._parent_ref is not None:
                self._parent_ref._unregister_child(self)
                self._parent_ref = None
            return
        from ngoschema.models.foreign_key import ForeignKey
        if isinstance(value, ForeignKey):
            self._parent_ref = value.ref # very moche
        else:
            self._parent_ref = value
        self._parent_ref._register_child(self)

    def _get_parent(self):
        return self._parent_ref

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

    def _get_root(self):
        cur = self
        while cur._parent:
            cur = cur._parent
        return cur

    def _get_path(self):
        cur = self
        path = []
        while cur:
            par = cur._parent
            if not par:
                break
            found = False
            for k, v in par.items():
                if utils.is_sequence(v):
                    if hasattr(v, '__itemtype__'):
                        itype = v.__itemtype__
                        if hasattr(itype, '_class'): # case it s a reference
                            itype = itype._class
                        if not isinstance(cur, itype):
                            continue
                    for i, e in enumerate(v):
                        if e is cur:
                            path.insert(0, i)
                            path.insert(0, k)
                            found = True
                            break
                elif v is cur:
                    path.insert(0, k)
                    found = True
                if found:
                    break
            else:
                assert False, k
            cur = par
        return path

    def _get_relative_path(self, src):
        dst_p = self._get_path()
        src_p = src._get_path()
        # find common root - take common elements and the go back to the root array if element is in an array
        common = [i for i, j in zip(dst_p, src_p) if i == j]
        lc = len(common)
        while lc and utils.is_integer(dst_p[lc]):
            common.pop()
            lc = len(common)
        path = ['..'] * (len([p for p in src_p[len(common):] if not utils.is_integer(p)])) + dst_p[len(common):]
        return path

    @memoized_property
    def handler(self):
        return self._get_root()._handler

    @memoized_property
    def session(self):
        return self.handler._session

    _children = property(_get_children)


class HasCanonicalName(HasName, HasParent):

    def get_name(self):
        return self._name

    def set_name(self, value):
        value = value.replace('-', '_')
        n = str(value) if value else None
        if self._name != n:
            HasName.set_name(self, n)
            self._touch_children()

    def _set_parent(self, value):
        if self._parent is not value:
            HasParent._set_parent(self, value)

    _parent = property(HasParent._get_parent,_set_parent)

    _cname = None
    def _update_cname(self):
        not_redef = (self._get_prop('canonicalName') is not None
                    and self._get_prop_value('canonicalName') == self._cname
                    and self._cname is not None) or self._cname is None
        par = self._parent
        par_cn = None
        while par:
            if isinstance(par, HasCanonicalName) and par._name is not None:
                break
            par = par._parent
        cname = '%s.%s' % (par._cname, self._name or '') if par and par._cname else self._name
        # invalidate cache
        if not_redef and cname is not None:
            self._cname = cname
            self._set_prop_value('canonicalName', cname)

    def _touch_children(self):
        self._update_cname()
        for c in self._children:
            c._touch_children()

    def _register_child(self, child):
        HasParent._register_child(self, child)
        child._touch_children()

    def _unregister_child(self, child):
        HasParent._unregister_child(self, child)
        child._touch_children()

    def resolve_cname(self, cname):
        return self.session.resolve_cname(cname)


class RootRelativeCname:

    def resolve_relative_cname(self, value):
        val =  str(value)
        return '%s.%s' % (self._cname, val[1:]) if val[0] == '#' else val

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


class HasCache:
    #_dirty = True
    _context = None
    _prop_name = None
    _inputs_cached = {}
    _validated_data = None
    _expr_inputs = []
    _expr_pattern = None

    def _set_context_info(self, context, prop_raw):
        self._context = context
        self._prop_name = prop_raw

    def register_expr(self, expr):
        from ngoschema.utils.jinja2 import get_variables
        self._expr_inputs = get_variables(expr)
        self._expr_pattern = expr

    def has_expr(self):
        return self._expr_pattern is not None

    def eval_expr(self, **inputs):
        from ..utils.jinja2 import TemplatedString
        try:
            return TemplatedString(self._expr_pattern)(this=self._context, **inputs)
        except Exception as er:
            # inputs might not all be defined. input data are not cached
            pass

    def _inputs(self):
        if self._prop_name:
            return self._context.__dependencies__.get(self._prop_name, []) + self._expr_inputs
        return [] + self._expr_inputs

    @property
    def _outputs(self):
        if self._prop_name:
            return [k for k, v in self._context.__dependencies__.items() if self._prop_name in v]
        return []


    #@property
    #def validated_data(self):
    #    from ngoschema import LiteralValue, ArrayWrapper, ProtocolBase
    #    if not self._validated_data:
    #        if self.validate():
    #            if isinstance(self, LiteralValue):
    #                self._validated_data = self._value
    #            if isinstance(self, ArrayWrapper):
    #                self._validated_data = [el.validated_data() for el in self.typed_elems]
    #            if isinstance(self, ProtocolBase):
    #                self._validated_data = {k: p.validated_data() for k, p in self._properties.items() if p}
    #    return self._validated_data

    def _inputs_data(self):
        ret = {}
        for input in self._inputs():
            ret[input] = utils.get_descendant(self._context, input)
        return ret

    def validate(self):
        if self.is_dirty():
            inputs = self._inputs_data()
            data = None
            if isinstance(self, LiteralValue):
                data = self._value
            elif isinstance(self, ArrayWrapper):
                data = self.data
            if self.has_expr():
                data = self.eval_expr(**inputs) or data
            self._validate(data)
            self._inputs_cached = inputs
        return True

    def _validate(self, data):
        """to be overloaded"""

    def is_dirty(self):
        return self._validated_data is None or self._inputs_data() != self._inputs_cached

    def touch(self):
        if self._validated_data is not None:
            self._validated_data = None
            # touch outputs
            for output in self._outputs:
                parts = utils.split_path(output)
                par = self
                if len(parts)>1:
                    par = utils.get_descendant(o, parts[:-1])
                last = parts[-1]
                if utils.is_string(last):
                    getattr(par, last) # to set maybe missing prop
                    o = par._properties[last] if last in par._properties else None
                else:
                    o = par[last]
                if o:
                    o.touch()
            # touch parent
            if getattr(self, '_parent', False):
                self._parent.touch()

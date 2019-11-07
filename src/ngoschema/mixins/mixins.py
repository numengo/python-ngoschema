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
from python_jsonschema_objects.classbuilder import LiteralValue

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

    def get_root(self):
        cur = self
        while cur._parent:
            cur = cur._parent
        return cur

    def get_path(self):
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

    def get_relative_path(self, src):
        dst_p = self.get_path()
        src_p = src.get_path()
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
        return self.get_root()._handler

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


class HasCache:
    _context = None
    _cache = None
    _inputs = set()
    _outputs = set()

    def __init__(self, context=None, inputs=None, outputs=None):
        self._context = context
        self._inputs = inputs or set()
        self._outputs = outputs or set()
        self._dirty = True

    def _set_context(self, context):
        self._context = context

    def _set_inputs(self, *inputs):
        self._inputs = set(inputs)

    def _add_inputs(self, *inputs):
        self._inputs.update(inputs)

    def _set_outputs(self, *outputs):
        self._outputs = set(outputs)

    def _add_outputs(self, *outputs):
        self._outputs.update(outputs)

    def __prop(self, key):
        cur = self._context
        return getattr(cur, key, None)

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
        val = self._context._get_prop_value(key)
        return val.for_json() if isinstance(val, LiteralValue) else val

    @property
    def _input_values(self):
        return {} if not self._context else {
            k: self.__prop_value(k)
            for k in self._inputs
        }

    def is_dirty(self):
        return self._dirty or (self._cache != self._input_values)

    def set_clean(self, recursive=False):
        self._dirty = False
        self._cache = self._input_values

    def touch(self, recursive=False):
        self._dirty = True
        if recursive:
            for k, p in self._output_props.items():
                p.touch()

    def do_validate(self, force=False):
        """validate only if property is dirty or if `force` is True """
        # validate inputs
        for k, p  in self._input_props.items():
            p.do_validate(force)

        if self._dirty or force:
            from ..wrapper_types import ArrayWrapper
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

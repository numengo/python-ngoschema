# *- coding: utf-8 -*-
"""
Base class for metadata (inherited by all components normally)

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import weakref

from future.utils import with_metaclass
from python_jsonschema_objects.util import safe_issubclass
#from python_jsonschema_objects.wrapper_types import ArrayWrapper
import python_jsonschema_objects.classbuilder as pjo_classbuilder

from . import utils
from .classbuilder import ProtocolBase
from .wrapper_types import ArrayWrapper
from .classbuilder import get_builder
from .classbuilder import touch_instance_prop
from .schema_metaclass import SchemaMetaclass
from .foreign_key import ForeignKey
from .foreign_key import touch_all_refs

class Metadata(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to deal with metadata and parents/children relationships
    """
    schemaUri = "http://numengo.org/draft-05/schema#/definitions/Metadata"

    _pks = None

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)

    def __repr__(self):
        if not self._short_repr_:
            return pjo_classbuilder.ProtocolBase.__repr__(self)
        repr = self.__class__.__name__
        repr += ' name=%s' % self.cname
        return "<%s id=%i>" % (repr, id(self))

    def get_primaryKeys(self):
        if not self._pks:
            pks = self._properties.get('primaryKeys')
            if not pks:
                pks = [k for k, v in self._properties.items() if isinstance(v, ForeignKey)]
            self._pks = pks if pks else ['name']
        return self._pks

    @property
    def primaryKeysValues(self):
        ret = [self._properties.get(pk) for pk in self.pks]
        return ret[0] if len(ret)==1 else ret

    @property
    def pks(self):
        return self.get_primaryKeys()

    _parent = None
    def set_parent(self, value):
        #parent_ref = value._ref if isinstance(value, ForeignKey) else weakref.ref(value)
        if isinstance(value, ForeignKey):
            parent_wref = value._ref
        else:
            parent_wref = weakref.ref(value) if value else None
        if not self._parent or self._parent is not parent_wref:
            self._parent = parent_wref
            if parent_wref and hasattr(self, '_properties'):
                for propname in self:
                    prop = self[propname]
                    if isinstance(prop, Metadata):
                        if prop._lazy_loading:
                            prop._set_prop_value('parent', parent_wref())
                        else:
                            prop.parent = parent_wref()
                    elif isinstance(prop, ArrayWrapper):
                        prop.parent = parent_wref()
            self._update_cname()

    @property
    def parent_ref(self):
        if self.parent and self.parent.ref:
            return self.parent.ref
        return self._parent() if self._parent else None
        #if not self._parent and self.parent and self.parent.ref:
        #    self._parent = self.parent
        #return self._parent.ref if self._parent else None

    # iname to store in a cache the name of the instance as a string
    _iname = None
    def set_name(self, value):
        self._iname = str(value)
        self._update_cname()

    @property
    def iname(self):
        """instane name as a string property"""
        return self._iname or '<anonymous>'

    # cache for canonical name
    _cname = None
    def _update_cname(self, value=None):
        old_value = self._cname
        cname = '%s.%s' % (self.parent_ref.cname, self.iname) \
                            if self.parent_ref \
                            else self.iname
        if value and value != cname:
            self._cname = value
        elif not self._cname or self.parent_ref:
            self._cname = cname
        #if value and value != self._iname and value != self.iname:
        #    self._cname = value
        #else:
        #    self._cname = '%s.%s' % (self._parent().cname, self.iname) \
        #                    if self._parent and self._parent() \
        #                    else self.iname
        if self._lazy_loading:
            return
        # this function is called at early stage of component initialiation
        # when _properties is not yet allocated => just a safegard
        if hasattr(self, '_properties'):
            #if not self._lazy_loading:
                #if hasattr(self, '_properties') and self.children:
                #    for child in self.children:
                #        child.ref._update_cname()
            #else:
            #    self._set_prop_value('canonicalName', self._cname)
            if self._cname != old_value:
                self.canonicalName = self._cname
                touch_instance_prop(self, 'canonicalName')
                #for propname in self:
                #    prop = self._properties.get(propname)
                #    if hasattr(prop, '_update_cname'):
                #        prop._update_cname()

    @property
    def cname(self):
        """canonical name as a string property"""
        return self._cname or self.iname

    def set_canonicalName(self, value):
        if self._cname != str(value):
            self._update_cname(str(value))

    def resolve_cname(self, ref_cname):
        # use generators because of 'null' which might lead to different paths
        def _resolve_cname(cn, cur, cur_cn, cur_path):
            if isinstance(cur, (dict, Metadata)):
                # can' t trust the cname
                # rebuild canonical name from name
                cn2 = cur_cn + [str(getattr(cur, 'iname') or cur.get('name') or '<anonymous>')]
                if cn2 == cn[0:len(cn2)]:
                    if cn2 == cn:
                        yield cur, cn, cn2, cur_path
                    for k, v in cur.items():
                        if isinstance(v, (dict, Metadata)) or isinstance(v, (list, ArrayWrapper)):
                            for _ in _resolve_cname(cn, v, cn2, cur_path + [k]):
                                yield _
            if isinstance(cur, (list, ArrayWrapper)):
                for i, v in enumerate(cur):
                    for _ in _resolve_cname(cn, v, cur_cn, cur_path + [i]):
                        yield _


        cur = self
        cur_cn = self.cname.split('.')
        cname = str(ref_cname)
        cn = cname.split('.')
        path = []
        if cname.startswith('#'):
            cn = cur_cn + cname[1:].split('.')
        else:
            i = 0
            while i < len(cur_cn) and i < len(cn) and cur_cn[i] == cn[i]:
                i += 1
            path = ['..'] * (len(cur_cn)-i)
            for _ in range(len(cur_cn)-i):
                cur = cur._parent
            #cur_cn = str(cur.cname).split('.')[:-1]
        # replace all nulls by <anonymous> which is used in ProtocolBase
        cn = [e.replace('null', '<anonymous>') for e in cn]
        # first search without last element, as last one might not be a named object
        # but the name of an attribute
        for d, c, e, p in _resolve_cname(cn[:-1], cur, cur_cn[:-1], path):
            if cn[-1] in d and not utils.is_method(d[cn[-1]]):
                # if a method with samme name is defined, wrong path
                p.append(cn[-1])
                return p
            # we can continue the search from last point. we remove the last element of the
            # canonical name which is going to be read again
            for d2, c2, e2, p2 in _resolve_cname(cn, d, e[:-1], p):
                return p2
        raise Exception('Unresolvable canonical name %s in %s' % (ref_cname, self.cname))

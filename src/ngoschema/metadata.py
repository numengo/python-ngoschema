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

from . import utils
from .mixins import HasParent
from .protocol_base import ProtocolBase
from .wrapper_types import ArrayWrapper
from .schema_metaclass import SchemaMetaclass
from .foreign_key import ForeignKey
from .canonical_name import CN_KEY

class Metadata(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to deal with metadata and parents/children relationships
    """
    schemaUri = "http://numengo.org/draft-05/schema#/definitions/Metadata"

    _pks = None

    def __init__(self, lazy_loading=None, **props):
        ProtocolBase.__init__(self, lazy_loading=True, **props)
        if lazy_loading and set(['name', 'parent', 'canonicalName']).intersection(props.keys()):
            par = self._parent
            if 'canonicalName' in props:
                self._lazy_data.setdefault('canonicalName', props['canonicalName'])
            elif par:
                cn = '%s.%s' % (par.canonicalName, self._get_prop_value('name', '<anonynous>'))
                self._lazy_data.setdefault('canonicalName', cn)

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

    _cname = None
    def get_canonicalName(self):
        ret = self._get_prop_value('canonicalName')
        self._cname = str(ret)
        return ret

    def resolve_cname(self, ref_cname):
        # use generators because of 'null' which might lead to different paths
        def _resolve_cname(cn, cur, cur_cn, cur_path):
            if isinstance(cur, (dict, Metadata)):
                # can' t trust the cname
                # rebuild canonical name from name
                cn2 = cur_cn + [str(cur['name'])]
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
        cur_cn = str(cur['canonicalName']).split('.')
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
                # if a method with same name is defined, wrong path
                p.append(cn[-1])
                return p
            # we can continue the search from last point. we remove the last element of the
            # canonical name which is going to be read again
            for d2, c2, e2, p2 in _resolve_cname(cn, d, e[:-1], p):
                return p2
        raise Exception('Unresolvable canonical name %s in %s' % (ref_cname, self.canonicalName))

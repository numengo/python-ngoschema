# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from ..utils import GenericClassRegistry, is_mapping
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from ..managers.type_builder import type_builder, scope
from ..resolvers.uri_resolver import resolve_uri

logger = logging.getLogger(__name__)


class RelationshipDescriptor:

    def __init__(self, pname, rtype):
        self.pname = pname
        self.rtype = rtype

    def __get__(self, obj, owner=None):
        if obj is None and owner is not None:
            return self
        fk = self.pname
        ik = obj[fk]
        return obj.items_type(fk).resolve(ik, session=obj.session)

    def __set__(self, obj, value):
        obj[self.pname] = value._identityKeys
        pass


class RelationshipBuilder(GenericClassRegistry):
    _registry = {}

    #@staticmethod
    #def register(id):
    #    return GenericClassRegistry.register(RelationshipBuilder, id)

    #@staticmethod
    #def get(id):
    #    return GenericClassRegistry.get(RelationshipBuilder, id)

    #@staticmethod
    #def contains(id):
    #    return GenericClassRegistry.contains(RelationshipBuilder, id)

    #@staticmethod
    def build(self, id, schema=None, bases=(), attrs=None):
        from ..relationships import Relationship, ForeignKey
        from ..protocols import TypeProtocol, ObjectProtocol, ArrayProtocol, TypeProxy
        cname = default_ns_manager.get_id_cname(id)
        clsname = cname.split('.')[-1]
        attrs = attrs or {}
        if self.contains(id):
            return self.get(id)
        if schema is None:
            schema = resolve_uri(id)
        attrs = dict(attrs or {})
        attrs['name'] = clsname
        attrs['_id'] = id
        fs = schema.get('foreignSchema')
        attrs['_foreignSchema'] = fs = scope(fs, id)
        fc = type_builder.load(fs)
        is_fc_proxy = hasattr(fc, '_proxyUri')
        attrs['_foreignClass'] = fc
        attrs['_cardinality'] = attrs.get('_cardinality') or schema.get('cardinality', 'OneToOne')
        fks = attrs.get('_foreignKeys') or schema.get('foreignKeys', [])
        if not is_fc_proxy:
            fks = fks or fc._primaryKeys # just add
        attrs['_foreignKeys'] = fks
        attrs['_one2many'] = attrs.get('_one2many') or 'OneTo' not in attrs['_cardinality']
        attrs['_ordering'] = attrs.get('_ordering') or schema.get('ordering', [])
        attrs['_reverse'] = attrs.get('_reverse') or schema.get('reverse', False)
        attrs['_inheritance'] = attrs.get('_inheritance') or schema.get('inheritance', False)
        if not any([issubclass(b, Relationship) for b in bases]):
            bases = (Relationship, ) + bases
        # schema is left empty and class is built using attributes
        cls = ObjectProtocol.build(id, {}, bases, attrs)
        bps = schema.get('backPopulates')
        if bps and is_mapping(bps):
            for n, bp  in bps.items():
                bp_fs = scope(bp['foreignSchema'], id)
                bp_fc = type_builder.load(bp_fs)
                bp_id = fs + f'/relationships/{bp}'
                bp_rl = {'foreignSchema': id.split('/relationships')[0]}
                if not hasattr(bp_fc, '_proxyUri'):
                    bp_fc._localRelationships[bp] = self.build(bp_id, bp_rl)
        self._registry[id] = cls
        return cls

    #@staticmethod
    def load(self, id):
        from ..protocols import TypeProxy
        if id not in self._registry:
            self._registry[id] = self.build(id)
        return self._registry[id]


relationship_builder = RelationshipBuilder()

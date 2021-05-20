# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from ..utils import GenericClassRegistry
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from ..managers.type_builder import TypeBuilder, scope
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

    @staticmethod
    def register(id):
        return GenericClassRegistry.register(RelationshipBuilder, id)

    @staticmethod
    def build(id, schema=None, bases=(), attrs=None):
        from ..relationships import Relationship, ForeignKey
        from ..protocols import TypeProtocol, ObjectProtocol, ArrayProtocol, TypeProxy
        cname = default_ns_manager.get_id_cname(id)
        clsname = cname.split('.')[-1]
        attrs = attrs or {}
        if RelationshipBuilder.contains(id):
            return RelationshipBuilder.get(id)
        if schema is None:
            schema = resolve_uri(id)
        attrs = dict(attrs or {})
        attrs['name'] = clsname
        attrs['_id'] = id
        fk = attrs.get('_foreignKey') or schema.get('foreignKey')
        fs = schema.get('foreignSchema')
        bp = schema.get('backPopulates')
        attrs['_foreignSchema'] = fs = scope(fs, id)
        fc = TypeBuilder.load(fs)
        attrs['_foreignClass'] = fc
        if not any([issubclass(b, Relationship) for b in bases]):
            bases = (Relationship, ) + bases
        cls = ObjectProtocol.build(id, schema, bases, attrs)
        if bp:
            bp_id = fs + f'/relationships/{bp}'
            bp_rl = {'foreignSchema': id.split('/relationships')[0]}
            fc._relationships[bp] = RelationshipBuilder.build(bp_id, bp_rl)
        RelationshipBuilder._registry[id] = cls
        return cls

    @staticmethod
    def load(id):
        from ..protocols import TypeProxy
        if id not in RelationshipBuilder._registry:
            RelationshipBuilder._registry[id] = RelationshipBuilder.build(id)
        return RelationshipBuilder._registry[id]


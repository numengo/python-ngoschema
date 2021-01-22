# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from ..utils import GenericClassRegistry
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from ..managers.type_builder import TypeBuilder, scope
from ..resolvers.uri_resolver import resolve_uri

logger = logging.getLogger(__name__)


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
        fs = schema.get('foreignSchema')
        bp = schema.get('backPopulates')
        if fs:
            attrs['_foreignSchema'] = scope(fs, id)
        if not any([issubclass(b, Relationship) for b in bases]):
            bases = (Relationship, ) + bases
        cls = ObjectProtocol.build(id, schema, bases, attrs)
        if bp:
            fc = TypeBuilder.load(fs)
            attrs['_foreignClass'] = fc
            fc._relationships[bp] = cls
        RelationshipBuilder._registry[id] = cls
        return cls

    @staticmethod
    def load(id):
        from ..protocols import TypeProxy
        if id not in RelationshipBuilder._registry:
            RelationshipBuilder._registry[id] = RelationshipBuilder.build(id)
        return RelationshipBuilder._registry[id]


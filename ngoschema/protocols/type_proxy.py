# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .type_protocol import TypeProtocol


class TypeProxy(TypeProtocol):
    _proxyUri = None

    @staticmethod
    def build(uri, schema=None):
        from ..managers.namespace_manager import default_ns_manager
        from ..managers.type_builder import type_builder
        from .object_protocol import ObjectProtocol
        from .array_protocol import ArrayProtocol
        sch, bases, attrs = type_builder._on_construction[uri]
        schema = schema or sch
        clsname = attrs.get('_clsname') or default_ns_manager.get_id_cname(uri)
        protocol = {'object': ObjectProtocol, 'array': ArrayProtocol}.get(sch['type'], TypeProtocol)
        #bases += (protocol, TypeProxy) if not issubclass(protocol, bases) else ()
        bases += (protocol, ) if not issubclass(protocol, bases) else ()
        attrs = {k: v for k, v in attrs.items() if not k.startswith('__')}
        attrs['_proxyUri'] = uri
        attrs['_id'] = uri
        attrs['_schema'] = schema
        attrs['__doc__'] = 'reference to %s' % clsname
        return type(clsname, (TypeProxy, ) + bases, attrs)

    def __new__(cls, *args, **kwargs):
        return cls.proxy_type()(*args, **kwargs)

    @classmethod
    def proxy_type(cls):
        from ..managers.type_builder import type_builder
        return type_builder.get(cls._proxyUri)

    @classmethod
    def check(cls, value, **opts):
        p = cls.proxy_type()
        return p and p.check(value, **opts)

    @classmethod
    def has_default(cls):
        p = cls.proxy_type()
        return p and p.has_default()

    @classmethod
    def convert(cls, value, **opts):
        p = cls.proxy_type()
        return p and p.convert(value, **opts)

    @classmethod
    def serialize(cls, value, **opts):
        p = cls.proxy_type()
        return p and p.serialize(value, **opts)

    @classmethod
    def inputs(cls, value, **opts):
        p = cls.proxy_type()
        return p and p.inputs(value, **opts)

    @classmethod
    def validate(cls, value, **opts):
        p = cls.proxy_type()
        return p and p.validate(value, **opts)

    @classmethod
    def evaluate(cls, value, **opts):
        p = cls.proxy_type()
        return p and p.evaluate(value, **opts)

    @classmethod
    def __instancecheck__(cls, instance):
        kls = cls.proxy_type()
        return isinstance(instance, kls) if kls else False

    @classmethod
    def __subclasshook__(cls, subclass):
        kls = cls.proxy_type()
        return issubclass(subclass, kls) if kls else False

    @classmethod
    def __hash__(cls):
        return hash(cls._proxyUri)

    def __repr__(self):
        rc = self.proxy_type()
        return repr(rc) if rc else f'<TypeProxy $id={self._proxyUri}>'

    def __str__(self):
        rc = self.proxy_type()
        return str(rc) if rc else f'<TypeProxy $id={self._proxyUri}>'

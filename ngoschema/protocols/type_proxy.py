# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import copy
from collections import OrderedDict, Mapping

from ..resolver import resolve_uri, scope
from .type_protocol import TypeProtocol


class TypeProxy(TypeProtocol):
    _proxy_uri = None
    _proxy_type = None

    @staticmethod
    def build(uri, schema=None):
        from ..managers.namespace_manager import default_ns_manager
        from ..managers.type_builder import TypeBuilder
        from .object_protocol import ObjectProtocol
        from .array_protocol import ArrayProtocol
        schema = schema or {}
        sch, bases, attrs = TypeBuilder._on_construction[uri]
        clsname = attrs.get('_clsname') or default_ns_manager.get_id_cname(uri)
        protocol = {'object': ObjectProtocol, 'array': ArrayProtocol}.get(sch['type'], TypeProtocol)
        #bases += (protocol, TypeProxy) if not issubclass(protocol, bases) else ()
        bases += (protocol, ) if not issubclass(protocol, bases) else ()
        attrs = {k: v for k, v in attrs.items() if not k.startswith('__')}
        attrs['_proxy_uri'] = uri
        attrs['_id'] = uri
        attrs['_schema'] = schema
        attrs['__doc__'] = 'reference to %s' % clsname
        return type(clsname, (TypeProxy, ) + bases, attrs)

    def __init__(self, *args, **kwargs):
        #self.proxy_type.__init__(*args, **kwargs)
        pass

    def __call__(self, *args, **kwargs):
        return self.proxy_type(*args, **kwargs)

    @classmethod
    def proxy_type_cls(cls):
        if not cls._proxy_type:
            from ..managers.type_builder import TypeBuilder
            cls._proxy_type = cls._py_type = TypeBuilder.get(cls._proxy_uri)
        return cls._proxy_type

    @property
    def proxy_type(self):
        if not self._proxy_type:
            self._proxy_type = self._py_type = self.proxy_type_cls()
        return self._proxy_type

    @classmethod
    def check(cls, value, **opts):
        return cls.proxy_type_cls() and cls.proxy_type_cls().check(value, **opts)

    @classmethod
    def has_default(cls):
        return cls.proxy_type_cls() and cls.proxy_type_cls().has_default()

    @classmethod
    def convert(cls, value, **opts):
        return cls.proxy_type_cls().convert(value, **opts)

    @classmethod
    def serialize(cls, value, **opts):
        return cls.proxy_type_cls().serialize(value, **opts)

    @classmethod
    def inputs(cls, value, **opts):
        return cls.proxy_type_cls().inputs(value, **opts)

    @classmethod
    def validate(cls, value, **opts):
        return cls.proxy_type_cls().validate(value, **opts)

    @classmethod
    def evaluate(cls, value, **opts):
        return cls.proxy_type_cls().evaluate(value, **opts)

    @classmethod
    def __instancecheck__(cls, instance):
        kls = cls.proxy_type_cls()
        return isinstance(instance, kls) if kls else False

    #def __subclasscheck__(cls, subclass):
    #    return issubclass(subclass, cls.proxy_type_cls())

    @classmethod
    def __subclasshook__(cls, subclass):
        kls = cls.proxy_type_cls()
        return issubclass(subclass, kls) if kls else False

    @classmethod
    def __hash__(cls):
        return hash(cls._proxy_uri)

    def __repr__(self):
        rc = self.proxy_type
        return repr(rc) if rc else f'<TypeProxy $id={self._proxy_uri}>'

    def __str__(self):
        rc = self.proxy_type
        return str(rc) if rc else f'<TypeProxy $id={self._proxy_uri}>'

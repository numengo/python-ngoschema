# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import copy
from collections import OrderedDict, Mapping

from ..utils import ReadOnlyChainMap, apply_through_collection
from ..resolver import resolve_uri, scope
from .type_protocol import TypeProtocol


class TypeProxy(TypeProtocol):
    _proxy_uri = None
    _proxy_type = None

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return self.ref_class(*args, **kwargs)

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
        bases += (protocol,) if not issubclass(protocol, bases) else ()
        return type(clsname, (TypeProxy, *bases), {
            '_proxy_uri': uri,
            '_schema': schema,
            '__doc__': 'reference to %s' % clsname})

    @classmethod
    def _proxy_type_registry(cls):
        if not cls._proxy_type:
            from ..managers.type_builder import TypeBuilder
            cls._proxy_type = cls._py_type = TypeBuilder.get(cls._proxy_uri)
        return cls._proxy_type

    @classmethod
    def __instancecheck__(cls, instance):
        return cls._proxy_type_registry() and isinstance(instance, cls._proxy_type_registry())

    @classmethod
    def __subclasscheck__(cls, subclass):
        return cls._proxy_type_registry() and issubclass(subclass, cls._proxy_type_registry())

    def __hash__(self):
        return hash(type(self))

    #def __repr__(self):
    #    rc = self.ref_class
    #    return repr(rc) if rc else f'<TypeProxy ref={self._ref}>'
    #
    #def __str__(self):
    #    rc = self.ref_class
    #    return str(rc) if rc else f'<TypeProxy ref={self._ref}>'

    #def __getattr__(self, item):
    #    return getattr(self.proxy_type, item)

    @classmethod
    def _properties_raw_trans(cls, name):
        return cls._proxy_type_registry()._properties_raw_trans(name)

    @classmethod
    def items_type(cls, name):
        return cls._proxy_type_registry().items_type(name)

    @property
    def ref_class(self):
        from ..managers.type_builder import TypeBuilder
        if self._proxy_type is None and self._proxy_uri in TypeBuilder._registry:
            self._proxy_type = self._proxy_type_registry()
            self.__dict__.update(self._proxy_type.__dict__)
        return self._proxy_type

    @classmethod
    def check(cls, value, **opts):
        return cls._proxy_type_registry().check(value, **opts)

    @classmethod
    def convert(cls, value, **opts):
        return cls._proxy_type_registry().convert(value, **opts)

    @classmethod
    def serialize(cls, value, **opts):
        return cls._proxy_type_registry().serialize(value, **opts)

    @classmethod
    def inputs(cls, value, **opts):
        return cls._proxy_type_registry().inputs(value, **opts)

    @classmethod
    def validate(cls, value, **opts):
        return cls._proxy_type_registry().validate(value, **opts)


class TypeProxy(TypeProtocol):
    _proxy_uri = None
    _proxy_type = None

    def __init__(self, uri):
        self._proxy_uri = uri

    def __call__(self, *args, **kwargs):
        return self.proxy_type(*args, **kwargs)

    @property
    def proxy_type(self):
        if not self._proxy_type:
            from ..managers.type_builder import TypeBuilder
            self._proxy_type = self._py_type = TypeBuilder.get(self._proxy_uri)
        return self._proxy_type

    def check(self, value, **opts):
        return self.proxy_type and self.proxy_type.check(value, **opts)

    def convert(self, value, **opts):
        return self.proxy_type.convert(value, **opts)

    def evaluate(self, value, **opts):
        return self.proxy_type.evaluate(value, **opts)

    def serialize(self, value, **opts):
        return self.proxy_type.serialize(value, **opts)

    def inputs(self, value, **opts):
        return self.proxy_type.inputs(value, **opts)

    def validate(self, value, **opts):
        return self.proxy_type.validate(value, **opts)

    def __instancecheck__(self, instance):
        return self.proxy_type and isinstance(instance, self.proxy_type)

    def __subclasscheck__(self, subclass):
        return self.proxy_type and issubclass(subclass, self.proxy_type)

    def __repr__(self):
        rc = self.proxy_type
        return repr(rc) if rc else f'<TypeProxy $id={self._proxy_uri}>'

    def __str__(self):
        rc = self.proxy_type
        return str(rc) if rc else f'<TypeProxy $id={self._proxy_uri}>'

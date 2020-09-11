# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import copy
from collections import OrderedDict, Mapping

from ..utils import ReadOnlyChainMap, apply_through_collection
from ..resolver import resolve_uri, scope
from ..types.jsch_validators import default_meta_validator
from ..types.type import Type

logger = logging.getLogger(__name__)


def unref_schema(schema, base_id):
    if '$ref' in schema:
        schema = schema.copy()
        ref = scope(schema.pop('$ref'), base_id)
        schema.update(unref_schema(resolve_uri(ref), ref))
    return schema


class TypeBuilder:
    _registry = {}
    _on_construction = {}

    class TypeProxy:
        _ref = None
        _ref_class = None
        _schema = {}

        def __init__(self, *args, **kwargs):
            pass

        @classmethod
        def _ref_class_registry(cls):
            return TypeBuilder._registry.get(cls._ref)

        @classmethod
        def __instancecheck__(cls, instance):
            return isinstance(instance, cls._ref_class_registry())

        @classmethod
        def __subclasscheck__(cls, subclass):
            return issubclass(subclass, cls._ref_class_registry())

        def __hash__(self):
            return hash(type(self))

        def __repr__(self):
            rc = self.ref_class
            return repr(rc) if rc else f'<TypeProxy ref={self._ref}>'

        def __str__(self):
            rc = self.ref_class
            return str(rc) if rc else f'<TypeProxy ref={self._ref}>'

        def __getattr__(self, item):
            return getattr(self.ref_class, item)

        @classmethod
        def _properties_raw_trans(cls, name):
            return cls._ref_class_registry()._properties_raw_trans(name)

        @classmethod
        def item_type(cls, name):
            return cls._ref_class_registry().item_type(name)

        @property
        def ref_class(self):
            if self._ref_class is None and self._ref in TypeBuilder._registry:
                self._ref_class = self._ref_class_registry()
                self.__dict__.update(self._ref_class.__dict__)
            return self._ref_class

            return self._ref_class or self._ref_class_registry()

        def __call__(self, *args, **kwargs):
            return self.ref_class(*args, **kwargs)

        def serialize(self, value, **opts):
            return self.ref_class.serialize(value, **opts)

        def validate(self, value, **opts):
            from ngoschema.types import Object
            return Object.validate(self.ref_class, value, **opts)
            return TypeProtocol.validate(self.ref_class, value, **opts)
            return self.ref_class._validate(value, **opts)

        @staticmethod
        def build(ref, schema=None):
            from ..managers.namespace_manager import default_ns_manager
            from .object_protocol import ObjectProtocol
            from .array_protocol import ArrayProtocol
            schema = schema or {}
            sch, bases, attrs = TypeBuilder._on_construction[ref]
            clsname = attrs.get('_clsname') or default_ns_manager.get_id_cname(ref)
            protocol = {'object': ObjectProtocol, 'array': ArrayProtocol}.get(sch['type'], Type)
            bases += (protocol, ) if not issubclass(protocol, bases) else ()
            return type(clsname, (TypeBuilder.TypeProxy, *bases), {
                '_ref': ref,
                '_schema': schema,
                '__doc__': 'reference to %s' % clsname})

    @staticmethod
    def register(id):
        """Decorator to register a protocol based class """
        def to_decorate(cls):
            TypeBuilder._registry[id] = cls
            cls._id = id
            return cls
        return to_decorate

    @staticmethod
    def build(id, schema=None, bases=(), attrs=None):
        from ..types.constants import _True, _False
        from .object_protocol import ObjectProtocol
        from .array_protocol import ArrayProtocol
        if id in TypeBuilder._registry:
            return TypeBuilder._registry[id]
        if id in TypeBuilder._on_construction:
            return TypeBuilder.TypeProxy.build(id)()
        if schema is None:
            schema = resolve_uri(id)
        if schema is True:
            return _True
        if schema is False:
            return _False()
        attrs = attrs or {}
        TypeBuilder._on_construction[id] = (schema, bases, attrs)
        if '$ref' in schema:
            schema = schema.copy()
            ref = schema.pop('$ref')
            cls = TypeBuilder.load(scope(ref, id))
            if schema:
                cls = cls.extend_type(**schema)
        elif 'object' in schema.get('type', ''):
            cls = ObjectProtocol.build(id, schema, bases, attrs)
        elif 'array' in schema.get('type', ''):
            cls = ArrayProtocol.build(id, schema, bases, attrs)
        else:
            cls = Type.build(id, schema, bases, attrs)(**schema)
        TypeBuilder._on_construction.pop(id)
        return TypeBuilder.register(id)(cls)

    @staticmethod
    def load(id):
        if id not in TypeBuilder._registry:
            if id in TypeBuilder._on_construction:
                return TypeBuilder.TypeProxy(id)
            TypeBuilder._registry[id] = TypeBuilder.build(id)
        return TypeBuilder._registry[id]

    @staticmethod
    def check_schema(schema):
        from jsonschema.exceptions import SchemaError
        for error in default_meta_validator.iter_errors(schema):
            raise SchemaError.create_from(error)

    @staticmethod
    def schema_mro(id, schema=None):
        schema = schema or resolve_uri(id)
        def _schema_mro(id, sch):
            for e in sch.get('extends', []):
                i = scope(e, id)
                s = resolve_uri(i)
                yield i, s
                for m in _schema_mro(i, s):
                    yield m
        return OrderedDict(_schema_mro(id, schema))

    @staticmethod
    def expand(id, schema=None):
        def scope_refs(id, schema):
            def _scope_refs(coll, key, level):
                if isinstance(coll, Mapping):
                    v = coll[key]
                    if isinstance(v, Mapping) and '$ref' in v:
                        v['$ref'] = scope(v['$ref'], id)
            apply_through_collection(schema, _scope_refs)

        schema = copy.deepcopy(schema or resolve_uri(id))
        mro = TypeBuilder.schema_mro(id, schema)
        scope_refs(id, schema)
        for i, s in mro.items():
            scope_refs(i, s)
        extends = list(mro.keys())
        required = list(schema.get('required', [])) + sum([list(s.get('required', [])) for s in mro.values()], [])
        read_only = list(schema.get('readOnly', [])) + sum([list(s.get('readOnly', [])) for s in mro.values()], [])
        not_serialized = list(schema.get('notSerialized', [])) + sum([list(s.get('notSerialized', [])) for s in mro.values()], [])
        properties = ReadOnlyChainMap(schema.get('properties', {}),
                                      *[s.get('properties', {}) for i, s in mro.items()])
        pattern_properties = ReadOnlyChainMap(schema.get('patternProperties', {}), *[s.get('patternProperties', {}) for s in mro.values()])
        if extends:
            schema['extends'] = extends
        if required:
            schema['required'] = set(required)
        if read_only:
            schema['readOnly'] = set(read_only)
        if not_serialized:
            schema['notSerialized'] = set(not_serialized)
        if properties:
            schema['properties'] = properties
        if pattern_properties:
            schema['patternProperties'] = pattern_properties
        return schema


class SchemaMetaclass(type):
    """Metaclass for instrumented classes defined by a schema based on ObjectProtocol.

    :param _id: id of schema to be resolved in loaded schemas using resolve_uri
    :param _schema: json schema (optional, schema can be supplied via _id
    :param _lazy_loading: attribute is only built and validated on first access
    :param _attribute_by_name: attributes can be accessed also by their names according to setting ATTRIBUTE_NAME_FIELD
    :param _add_logging: init method is decorated with a logger and all methods are decorated to log exceptions.
    :param _assert_args: if a method documentation is present, its content its parsed to detect attribute types and decorate
    the method with the proper check and conversion (default is True).
    """

    def __new__(cls, clsname, bases, attrs):
        #from .object_protocol import ObjectProtocol
        schema = attrs.get('_schema', {})
        id = attrs.get('_id')
        if not schema and id:
            schema = resolve_uri(id)
        elif bases:
            schema['extends'] = [b._id for b in bases if hasattr(b, '_id')]
        schema.setdefault('type', 'object')
        id = id or clsname
        # remove previous entry in registry
        if id in TypeBuilder._registry:
            del TypeBuilder._registry[id]
        attrs['_clsname'] = clsname
        return TypeBuilder.register(id)(TypeBuilder.build(id, schema, bases, attrs=attrs))

    def __subclasscheck__(cls, subclass):
        """Just modify the behavior for classes that aren't genuine subclasses."""
        # https://stackoverflow.com/questions/40764347/python-subclasscheck-subclasshook
        if super().__subclasscheck__(subclass):
            return True
        else:
            # Not a normal subclass, implement some customization here.
            cls_id = getattr(cls, '_id', None)
            scls_id = getattr(cls, '_id', None)

            def _is_subclass(class_id):
                if class_id == scls_id:
                    return True
                for e in resolve_uri(class_id).get('extends', []):
                    if _is_subclass(e):
                        return True
                return False

            return _is_subclass(cls_id)

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import copy
from collections import OrderedDict, Mapping
from jsonschema.validators import extend
from jsonschema.exceptions import UndefinedTypeCheck

from ..utils import ReadOnlyChainMap, apply_through_collection
from ..resolver import resolve_uri, scope
from .jsch_validators import Draft201909Validator, default_meta_validator

logger = logging.getLogger(__name__)


def untype_schema(schema):
    """go through schema items to remove instances of classes of Type and retrieve their schema."""
    from ..protocols.type_protocol import TypeProtocol
    schema = dict(schema)
    for k, v in list(schema.items()):
        if isinstance(v, TypeProtocol):
            schema[k] = dict(v._schema)
        elif isinstance(v, type) and issubclass(v, TypeProtocol):
            schema[k] = {'$ref': v._id}
        elif isinstance(v, Mapping):
            schema[k] = untype_schema(v)
    return schema


class TypeBuilder:
    _registry = {}
    _type_registry = {}
    _on_construction = {}

    @staticmethod
    def register(type):
        """Decorator to register a protocol based class """
        def to_decorate(cls):
            TypeBuilder._type_registry[type] = cls
            cls._type = type
            cls._schema = dict(cls._schema, type=cls._type)
            #if not cls._schema:
            #    cls._schema = {'type': cls._type}
            if cls._validator is None:
                cls._validator = DefaultValidator(cls._schema)
            return cls
        return to_decorate

    @staticmethod
    def is_type(value, id):
        """Reproduce is_type method of jsonschema.Type"""
        t = TypeBuilder._type_registry.get(id)
        if not t:
            raise UndefinedTypeCheck(id)
        return t.check(value)

    @staticmethod
    def detect_type(value):
        for k, t in TypeBuilder._type_registry.items():
            if t.check(value):
                return k, t

    @staticmethod
    def get_type(id):
        return TypeBuilder._type_registry[id]

    @staticmethod
    def get(id):
        return TypeBuilder._registry.get(id)

    @staticmethod
    def contains(id):
        return id in TypeBuilder._registry

    @staticmethod
    def build(id, schema=None, bases=(), attrs=None):
        from .namespace_manager import NamespaceManager
        from ..protocols import TypeProtocol, ObjectProtocol, ArrayProtocol, TypeProxy
        from ..types.constants import _True, _False
        if TypeBuilder.contains(id):
            return TypeBuilder.get(id)
        if id in TypeBuilder._on_construction:
            return TypeProxy.build(id)()
        if schema is None:
            schema = resolve_uri(id)
        if schema is True:
            return _True()
        if schema is False:
            return _False()
        attrs = attrs or {}
        TypeBuilder._on_construction[id] = (schema, bases, attrs)
        if '$ref' in schema:
            schema = schema.copy()
            ref = schema.pop('$ref')
            cls = TypeBuilder.load(scope(ref, id))
            if schema:
                cls = cls.extend_type(id, **schema)
        elif 'object' in schema.get('type', ''):
            cls = ObjectProtocol.build(id, schema, bases, attrs)
        elif 'array' in schema.get('type', ''):
            cls = ArrayProtocol.build(id, schema, bases, attrs)
        else:
            cls = TypeProtocol.build(id, schema, bases, attrs)()
        TypeBuilder._on_construction.pop(id)
        TypeBuilder._registry[id] = cls
        NamespaceManager.register_ns(id)
        return cls

    @staticmethod
    def load(id):
        from ..protocols import TypeProxy
        if id not in TypeBuilder._registry:
            if id in TypeBuilder._on_construction:
                return TypeProxy.build(id)()
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


register_type = TypeBuilder.register


DefaultValidator = extend(Draft201909Validator, type_checker=TypeBuilder)

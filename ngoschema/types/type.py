# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import inflection
from collections import Mapping, Sequence, OrderedDict
from jsonschema.validators import extend
from jsonschema.exceptions import UndefinedTypeCheck

from .. import DEFAULT_CONTEXT
from ..utils import ReadOnlyChainMap as ChainMap, Context
from ..resolver import scope, resolve_uri, UriResolver
from ..decorators import classproperty
from ..exceptions import InvalidValue, ValidationError, ConversionError
from .jsch_validators import Draft201909Validator

logger = logging.getLogger(__name__)


def untype_schema(schema):
    """go through schema items to remove instances of classes of Type and retrieve their schema."""
    from .type import Type
    schema = dict(schema)
    for k, v in list(schema.items()):
        if isinstance(v, Type):
            schema[k] = dict(v._schema)
        elif isinstance(v, type) and issubclass(v, Type):
            schema[k] = dict(v._schema)
        elif isinstance(v, Mapping):
            schema[k] = untype_schema(v)
    return schema


class TypeChecker(object):
    _registry = OrderedDict()

    @staticmethod
    def register(id):
        """Decorator to register a protocol based class """
        def to_decorate(cls):
            TypeChecker._registry[id] = cls
            cls._type = id
            return cls
        return to_decorate

    @staticmethod
    def is_type(value, id):
        """Reproduce is_type method of jsonschema.Type"""
        t = TypeChecker._registry.get(id)
        if not t:
            raise UndefinedTypeCheck(id)
        return t.check(value)

    @staticmethod
    def detect_type(value):
        for k, t in TypeChecker._registry.items():
            if t.check(value):
                return k, t

    @staticmethod
    def get(id):
        return TypeChecker._registry.get(id)

    @staticmethod
    def contains(id):
        return id in TypeChecker._registry


DefaultValidator = extend(Draft201909Validator, type_checker=TypeChecker)


class Type:
    """
    Type defined by a json-schema specification

    _type is the json-schema type label (null, object, string, integer, boolean, ...)
    _py_type should define which type to use in python (str, object, pathlib.Path, ...)

    t = types.Type(type='integer', minimum=0)
    t(1) = 1
    t(-1) raises InvalidValue Error

    s = types.String()
    s("hello {{name}}!", name='world') == 'hello world!'
    """
    _id = None
    _type = None
    _py_type = None
    _schema = {}
    _validator = DefaultValidator({})
    _context = DEFAULT_CONTEXT
    _repr = None
    _str = None

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from .type_builder import TypeBuilder
        from .namespace_manager import default_ns_manager
        attrs = attrs or {}
        ref = schema.get('$ref')
        cname = default_ns_manager.get_id_cname(ref or id)
        clsname = cname.split('.')[-1]
        # convert schema items provided as a class or instance of Type
        schema = untype_schema(schema)
        extra_bases = tuple(TypeBuilder.load(scope(e, id)) for e in schema.get('extends', []))
        # extract type and ref from schema and add the corresponding python types in bases
        if ref:
            extra_bases += (TypeBuilder.load(scope(ref, id)), )
        # add enum type if detected
        if 'enum' in schema:
            from .literals import Enum
            extra_bases += (Enum, )
        if 'type' in schema:
            extra_bases += (TypeChecker._registry[schema['type']], )
        # filter bases to remove duplicates
        extra_bases = tuple(b for b in extra_bases if not issubclass(b, bases))
        if not bases and not extra_bases:
            extra_bases = (Type, )
        attrs['_schema'] = schema = dict(ChainMap(schema, *[b._schema for b in bases + extra_bases if hasattr(b, '_schema')]))
        if 'rawLiterals' in schema:
            attrs['_raw_literals'] = schema['rawLiterals']
        attrs['_logger'] = logging.getLogger(cname)
        attrs['_validator'] = DefaultValidator(schema, resolver=UriResolver.create(uri=id, schema=schema))
        return type(clsname, bases + extra_bases, attrs)

    @classmethod
    def qualname(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def extend_type(cls, name, *bases, **schema):
        return TypeChecker.register(inflection.underscore(name))(Type.build(name, schema, bases=(cls, )+bases))

    def __init__(self, **schema):
        # create a chainmap of all schemas and validators of ancestors, reduce it and make it persistent
        from .type_builder import TypeBuilder
        schema = untype_schema(schema)
        self._schema_chained = ChainMap(schema,
                                *[getattr(s, '_schema', {}) for s in self.__class__.__mro__],
                                *[resolve_uri(e) for e in schema.get('extends', [])])
        self._schema = schema = dict(self._schema_chained)
        TypeBuilder.check_schema(schema)
        self._id = schema.get('$id', None) or self._id
        self._validator = DefaultValidator(schema, resolver=UriResolver.create(uri=self._id, schema=schema))
        if not self._py_type:
            if 'type' in schema:
                self._type = ty = schema['type']
                self._py_type =TypeChecker._registry[ty]._py_type

    @staticmethod
    def _make_context(self, context=None, *extra_contexts):
        ctx = context if context is not None else self._context
        self._context = ctx.create_child(*extra_contexts)

    def __instancecheck__(cls, instance):
        """Override for isinstance(instance, cls)."""
        return cls.check(instance, convert=False)

    @classmethod
    def check(cls, value, **opts):
        return Type._check(cls, value, **opts)

    def _check(cls, value, convert=False, **opts):
        """
        Default type checker, checking if the value is of compatible type.
        Can be overloaded for special treatments (according the convert method).

        :param value: data checked for compatibility
        :param convert: convert instance if possible
        :return: True if compatible
        """
        py_type = cls._py_type
        if py_type is None:
            return True
        if isinstance(value, py_type):
            return True
        if convert:
            try:
                value = cls.convert(value, **opts)
                return True
            except ConversionError as er:
                return False
        return False

    def __call__(self, value, convert=True, validate=True, serialize=False,  **opts):
        """
        Instanciating the type for a given value, evaluating the value using the context with the convert method,
        and optionally validating the instance.

        :param value: data to instanciate
        :param validate: activate validation
        :param context: evaluation context
        :return: typed instance
        """
        typed = value
        if typed is None and self.has_default():
            typed = self.default()
            typed = typed.copy() if hasattr(typed, 'copy') else typed
        if not self.check(typed) or convert:
            typed = self.convert(typed, **opts)
            # if Type is used directly, _py_type is defined in the instance not the class and convert is a class method
            # need recast in instance
            if self.__class__._py_type is None and self._py_type:
                typed = self._py_type(typed) if typed is not None else None
        if validate:
            self.validate(typed)
        return self.serialize(typed, **opts) if serialize else typed

    @classmethod
    def convert(cls, value, **opts):
        return Type._convert(cls, value, **opts)

    def _convert(cls, value, **opts):
        """
        Convert/evaluate a value according to context.
        :param value: input value
        :return: typed instance
        """
        py_type = cls._py_type
        if py_type is None or value is None:
            return value
        if isinstance(value, py_type):
            return value
        try:
            return py_type(value)
        except Exception as er:
            raise ConversionError("Impossible to convert %r to %s" % (value, cls._py_type))

    def validate(self, value, excludes=[], as_dict=False, **opts):
        """
        Check the type of value and validate according to schema or raise ngoschema.InvalidValue
        """
        errors = {
            '/'.join(e.schema_path): e.message
            for e in self._validator.iter_errors(value, {k: self._schema[k]
                                                         for k in self._schema if k not in excludes})}
        return errors if as_dict else self._format_error(value, errors)

    @classmethod
    def _format_error(cls, value, errors):
        if errors:
            msg = '\n'.join([f"Problem validating {cls._type} with {value}:"] + [f'\t{k}: {errors[k]}' for k in errors])
            raise InvalidValue(msg)

    def inputs(self, value, **opts):
        return set()

    @classmethod
    def has_default(cls):
        return Type._has_default(cls)

    def _has_default(self):
        return 'default' in self._schema

    def default(self, **opts):
        return Type._default(self, **opts)

    def _default(self, **opts):
        if 'default' in self._schema:
            return self(self._schema['default'], raw_literals=True, validate=False, **opts)
        return self._py_type() if self._py_type else None

    @classmethod
    def is_literal(cls):
        return False

    @classmethod
    def is_array(cls):
        return False

    @classmethod
    def is_object(cls):
        return False

    def serialize(self, value, **opts):
        """
        Serialize value for json according to type json-schema definition.
        Default behaviour is to return the typed python object, therefore,
        complex types should be overloaded to implement formatting (usually to string)
        :param value: value to serialize for json
        :param context: context for type evaluation
        :return: json friendly object
        """
        return value

    _sch_repr = None
    @staticmethod
    def _repr_schema(self):
        if self._sch_repr is None:
            self._sch_repr = OrderedDict(self._schema)
            if 'type' in self._sch_repr:
                self._sch_repr.move_to_end('type', False)
        return self._sch_repr

    def __repr__(self):
        if self._repr is None:
            s = ', '.join(['%s=%r' %(k, v) for k, v in self._repr_schema(self).items()])
            self._repr = '%s(%s)' % (Type.qualname(), s)
        return self._repr

    def __str__(self):
        if self._str is None:
            def serialize(k, v):
                if isinstance(v, Mapping):
                    return '%s{%i}' % (k, len(v))
                if isinstance(v, Sequence) and not isinstance(v, str):
                    return '%s[%i]' % (k, len(v))
                return '%s=%r' % (k, v)
            s = ' '.join([serialize(k, v) for k, v in self._repr_schema(self).items()])
            self._str = '<%s %s>' % (self.qualname(), s)
        return self._str

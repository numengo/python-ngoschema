# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import copy
from abc import abstractmethod
from collections import OrderedDict, Mapping, Sequence

from .. import DEFAULT_CONTEXT
from ..utils import ReadOnlyChainMap, apply_through_collection
from ..resolver import resolve_uri, scope, UriResolver
from ..exceptions import InvalidValue, ValidationError, ConversionError
from .. import settings

PRIMITIVE_VALIDATE = settings.DEFAULT_PRIMITIVE_VALIDATE

logger = logging.getLogger(__name__)


class TypeProtocol:
    _id = None
    _type = None
    _py_type = None
    _schema = {}
    _validator = None
    _context = DEFAULT_CONTEXT
    _default_cache = None
    _repr = None
    _str = None
    _dependencies = {}
    _mro_type = ()
    _validate = PRIMITIVE_VALIDATE

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from ..managers.type_builder import TypeBuilder, untype_schema, DefaultValidator
        from ..managers.namespace_manager import default_ns_manager
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
            from ..types import Enum
            attrs['_enum'] = schema['enum']
            extra_bases += (Enum, )
        if 'type' in schema:
            extra_bases += (TypeBuilder.get_type(schema['type']), )
        # filter bases to remove duplicates
        extra_bases = tuple(b for b in extra_bases if not issubclass(b, bases))
        if not bases and not extra_bases:
            extra_bases = (TypeProtocol, )
        attrs['_schema'] = schema = dict(ReadOnlyChainMap(schema, *[b._schema for b in bases + extra_bases if hasattr(b, '_schema')]))
        if 'rawLiterals' in schema:
            attrs['_raw_literals'] = schema['rawLiterals']
        if 'validate' in schema:
            attrs['_validate'] = schema['validate']
        attrs['_id'] = id
        attrs['_logger'] = logging.getLogger(cname)
        attrs['_validator'] = DefaultValidator(schema, resolver=UriResolver.create(uri=id, schema=schema))
        attrs['_mro_type'] = [b for b in bases + extra_bases if isinstance(b, type) and issubclass(b, TypeProtocol)]
        return type(clsname, bases + extra_bases, attrs)

    def __init__(self, value=None, context=None, **kwargs):
        # prepare data
        opts = kwargs
        if value is None:
            value = kwargs
            opts = {}
        validate = opts.pop('validate', self._validate)
        self._data = self._evaluate(value, validate=validate, context=context, **opts)
        self.set_context(context, opts)

    def create_context(self, context=None, *extra_contexts):
        ctx = context if context is not None else self._context
        return ctx.create_child(*extra_contexts)

    def set_context(self, context=None, *extra_contexts):
        ctx = self.create_context(context, *extra_contexts)
        self._context = ctx

    @classmethod
    def check(cls, value, **opts):
        return cls._check(cls, value, **opts)

    def _check(self, value, convert=False, **opts):
        """
        Default type checker, checking if the value is of compatible type.
        Can be overloaded for special treatments (according the convert method).

        :param value: data checked for compatibility
        :param convert: convert instance if possible
        :return: True if compatible
        """
        py_type = self._py_type
        if py_type is None:
            return True
        if isinstance(value, py_type):
            return True
        if convert:
            try:
                value = self.convert(value, **opts)
                return True
            except ConversionError as er:
                return False
        return False

    @classmethod
    def has_default(cls):
        return cls._has_default(cls)

    def _has_default(self):
        return 'default' in self._schema

    @classmethod
    def default(cls, **opts):
        return cls._default(cls, **opts)

    def _default(self, **opts):
        if 'default' in self._schema:
            return self._schema['default']
            #self._default_cache = self.convert(self._schema['default'], **opts)
        else:
            return self._py_type() if self._py_type else None

    @classmethod
    def convert(cls, value, **opts):
        return cls._convert(cls, value, **opts)

    def _convert(self, value, **opts):
        """
        Convert/evaluate a value according to context.
        :param value: input value
        :return: typed instance
        """
        py_type = self._py_type
        if py_type is None or value is None:
            return value
        if isinstance(value, py_type):
            return value
        try:
            return py_type(value)
        except Exception as er:
            raise ConversionError("Impossible to convert %r to %s" % (value, self._py_type))

    @classmethod
    def _format_error(cls, value, errors):
        if errors:
            msg = '\n'.join([f"Problem validating {cls} with {value}:"] + [f'\t{k}: {errors[k]}' for k in errors])
            raise InvalidValue(msg)

    def _do_validate(self, value, excludes=[], with_type=True, as_dict=False, **opts):
        """
        Validate the value according to schema
        Return dictionnary of errors or raise ngoschema.InvalidValue
        """
        if not with_type:
            excludes = list(excludes) + ['type']
        errors = {
            '/'.join(e.schema_path): e.message
            for e in self._validator.iter_errors(value, {k: self._schema[k]
                                                         for k in self._schema if k not in excludes})}
        return errors if as_dict else self._format_error(value, errors)

    def _evaluate(self, value, convert=True, context=None, **opts):
        validate = opts.get('validate', self._validate)
        ctx = self.create_context(context, opts)
        if value is None:
            if not self._has_default():
                return None
            value = self._default()
            value = value.copy() if hasattr(value, 'copy') else value
        typed = value if self.check(value, convert=False, context=ctx) else self.convert(value, context=ctx, **opts)
        if not self._check(typed, convert=convert, context=ctx):
            self._do_validate(typed, with_type=True, **opts)
        if convert:
            typed = self._convert(typed, context=ctx, **opts)
        if validate:
            opts.pop('items', None)
            self._do_validate(typed, items=False, with_type=False, **opts)
        return typed

    def _serialize(self, value, **opts):
        """
        Serialize value for json according to type json-schema definition.
        Default behaviour is to return the typed python object, therefore,
        complex types should be overloaded to implement formatting (usually to string)
        :param value: value to serialize for json
        :param context: context for type evaluation
        :return: json friendly object
        """
        return value

    def _inputs(self, value, **opts):
        return set()

    @classmethod
    def is_primitive(cls):
        return False

    @classmethod
    def is_object(cls):
        return False

    @classmethod
    def is_array(cls):
        return False

    @classmethod
    def qualname(cls):
        return cls.__module__ + '.' + cls.__name__

    _sch_repr = None
    def _repr_schema(self):
        if self._sch_repr is None:
            self._sch_repr = sch_repr = OrderedDict(self._schema)
            if 'type' in sch_repr:
                sch_repr.move_to_end('type', False)
        return self._sch_repr

    def __repr__(self):
        if self._repr is None:
            s = ', '.join(['%s=%r' %(k, v) for k, v in TypeProtocol._repr_schema(self).items()])
            self._repr = '%s(%s)' % (self.qualname(), s)
        return self._repr

    def __str__(self):
        if self._str is None:
            def serialize(k, v):
                if isinstance(v, Mapping):
                    return '%s{%i}' % (k, len(v))
                if isinstance(v, Sequence) and not isinstance(v, str):
                    return '%s[%i]' % (k, len(v))
                return '%s=%r' % (k, v)
            s = ' '.join([serialize(k, v) for k, v in TypeProtocol._repr_schema(self).items()])
            self._str = '<%s %s>' % (self.qualname(), s)
        return self._str

    @classmethod
    def extend_type(cls, id, *bases, **schema):
        import inflection
        from ..managers.type_builder import TypeBuilder
        return TypeBuilder.register(inflection.underscore(id))(TypeProtocol.build(id, schema, bases=(cls, )+bases))

    @property
    def context(self):
        return self._context


class SchemaMetaclass(type):
    """Metaclass for instrumented classes defined by a schema based on TypeProtocol.

    :param _id: id of schema to be resolved in loaded schemas using resolve_uri
    :param _schema: json schema (optional, schema can be supplied via _id
    :param _lazy_loading: attribute is only built and validated on first access
    :param _attribute_by_name: attributes can be accessed also by their names according to setting ATTRIBUTE_NAME_FIELD
    :param _add_logging: init method is decorated with a logger and all methods are decorated to log exceptions.
    :param _assert_args: if a method documentation is present, its content its parsed to detect attribute types and decorate
    the method with the proper check and conversion (default is True).
    """

    def __new__(cls, clsname, bases, attrs):
        from ..managers.type_builder import TypeBuilder
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
        return TypeBuilder.build(id, schema, bases, attrs=attrs)

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

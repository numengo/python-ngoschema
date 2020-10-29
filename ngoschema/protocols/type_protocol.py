# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import copy
from abc import abstractmethod
from collections import OrderedDict, Mapping, Sequence

from ..utils import ReadOnlyChainMap, shorten
from ngoschema.resolvers.uri_resolver import resolve_uri, scope, UriResolver
from .context import Context
from .validator import Validator
from .serializer import Serializer, Deserializer
from .. import settings

PRIMITIVE_VALIDATE = settings.DEFAULT_PRIMITIVE_VALIDATE

logger = logging.getLogger(__name__)


#def value_opts(*args, value=None, **kwargs):
#    opts = kwargs
#    if args:
#        assert len(args) == 1
#        value = args[0]
#    if value is None:
#        value = kwargs
#        opts = {}
#    return value, opts


class TypeProtocol(Serializer):
    _serializer = Serializer
    _type = None
    _description = None
    _comment = None
    _serializer = Serializer

    def __init__(self, serializer=None, **opts):
        self._serializer = serializer or self._serializer
        self._serializer.__init__(self, **opts)
        self._type = self._schema.get('type', self._type)
        self._comment = self._schema.get('$comment', self._comment)
        self._description = self._schema.get('description', self._description)

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from ..managers.type_builder import TypeBuilder, DefaultValidator
        from ..managers.namespace_manager import default_ns_manager
        from ..types import Type
        attrs = attrs or {}
        ref = schema.get('$ref')
        cname = default_ns_manager.get_id_cname(ref or id)
        clsname = cname.split('.')[-1]
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
            extra_bases = (Type, )
        attrs['_schema'] = schema = dict(ReadOnlyChainMap(schema, *[b._schema for b in bases + extra_bases if hasattr(b, '_schema')]))
        if 'rawLiterals' in schema:
            attrs['_rawLiterals'] = schema['rawLiterals']
        if 'default' in schema:
            attrs['_default'] = schema['default']
        attrs['_id'] = id
        attrs['_logger'] = logging.getLogger(cname)
        attrs['_js_validator'] = DefaultValidator(schema, resolver=UriResolver.create(uri=id, schema=schema))
        #attrs['_mro_type'] = [b for b in bases + extra_bases if isinstance(b, type) and issubclass(b, TypeProtocol)]
        return type(clsname, bases + extra_bases, attrs)

    @staticmethod
    def _inputs(self, value, **opts):
        return set()

    @classmethod
    def inputs(cls, value, **opts):
        return cls._inputs(cls, value, **opts)

    @staticmethod
    def _has_default(self, **opts):
        return bool(self._default)

    @classmethod
    def has_default(cls, **opts):
        return cls._has_default(cls, **opts)

    def default(self, value=None, **opts):
        return self._deserialize(self, value or self._default, evaluate=False, **opts)

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
        cm = cls.__module__
        qn = cm + '.' if not cm.startswith('_') else ''
        return qn + cls.__name__

    def __repr__(self):
        s = ', '.join(['%s=%r' %(k, v) for k, v in self._repr_schema(self).items()])
        return '%s(%s)' % (self.qualname(), shorten(s, max_size=100, str_fun=str))

    def __str__(self):
        def serialize(k, v):
            if isinstance(v, Mapping):
                return '%s{%i}' % (k, len(v))
            if isinstance(v, Sequence) and not isinstance(v, str):
                return '%s[%i]' % (k, len(v))
            return '%s=%r' % (k, v)
        s = ' '.join([serialize(k, v) for k, v in self._repr_schema(self).items()])
        return '<%s %s>' % (self.qualname(), shorten(s, max_size=100, str_fun=str))

    @classmethod
    def extend_type(cls, id, *bases, **schema):
        import inflection
        from ..managers.type_builder import TypeBuilder
        return TypeBuilder.register(inflection.underscore(id))(TypeProtocol.build(id, schema, bases=(cls, )+bases))


class SchemaMetaclass(type):
    """Metaclass for instrumented classes defined by a schema based on TypeProtocol.

    :param _id: id of schema to be resolved in loaded schemas using resolve_uri
    :param _schema: json schema (optional, schema can be supplied via _id
    :param _lazyLoading: attribute is only built and validated on first access
    :param _attributeByName: attributes can be accessed also by their names according to setting ATTRIBUTE_NAME_FIELD
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

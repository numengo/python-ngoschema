# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from ..protocols.type_protocol import TypeProtocol
from ..managers.type_builder import register_type
from ..utils import ReadOnlyChainMap
from ..resolver import resolve_uri, UriResolver
from ..exceptions import InvalidValue, ConversionError
from ..utils import shorten, inline
from .. import settings

logger = logging.getLogger(__name__)


class Type(TypeProtocol):
    _raw_literals = False

    def __init__(self, context=None, **schema):
        # create a chainmap of all schemas and validators of ancestors, reduce it and make it persistent
        from ..managers.type_builder import TypeBuilder, untype_schema, DefaultValidator
        schema = untype_schema(schema)
        self._mro_type = [b for b in self.__class__.__mro__ if issubclass(b, TypeProtocol)]
        self._schema_chained = ReadOnlyChainMap(schema,
                                *[b._schema for b in self._mro_type],
                                *[resolve_uri(e) for e in schema.get('extends', [])])
        self._schema = schema = dict(self._schema_chained)
        TypeBuilder.check_schema(schema)
        self._id = schema.get('$id') or self._id
        self._type = ty = schema.get('type')
        self._py_type = schema.get('pyType')
        self._raw_literals = schema.get('rawLiterals', self._raw_literals)
        self._validator = DefaultValidator(schema, resolver=UriResolver.create(uri=self._id, schema=schema))
        if not self._py_type:
            if 'type' in schema:
                self._py_type = TypeBuilder.get_type(ty)._py_type
        self._make_context(context)

    def __call__(self, *args, serialize=False, **kwargs):
        """
        Instanciating the type for a given value, evaluating the value using the context with the convert method,
        and optionally validating the instance.

        :param value: data to instanciate
        :param validate: activate validation
        :param context: evaluation context
        :return: typed instance
        """
        from .strings import Expr, Pattern
        value = args[0] if args else kwargs
        opts = kwargs if args else {}
        typed = self._evaluate(value, **opts)
        return self._serialize(self, typed, **opts) if serialize else typed

    def _convert(self, value, **opts):
        from .strings import Expr, Pattern
        raw_literals = opts.pop('raw_literals', self._raw_literals)
        typed = value
        if value and not raw_literals:
            try:
                if Expr.check(value):
                    typed = Expr.convert(value, **opts)
                elif Pattern.check(value):
                    typed = Pattern.convert(value, **opts)
            except Exception as er:
                logger.warning('impossible to convert %s: %s', shorten(inline(str(value))), er)
                logger.error(er, exc_info=True)
                typed = value
            return TypeProtocol._convert(self, typed, **opts)
        return typed

    def _inputs(self, value, context=None, **opts):
        from .strings import Expr, Pattern
        raw_literals = opts.pop('raw_literals', self._raw_literals)
        if not raw_literals:
            if Pattern.check(value):
                return Pattern.inputs(value, **opts)
            if Expr.check(value):
                return Expr.inputs(value, **opts)
        return set()


class Primitive(Type):

    @classmethod
    def is_primitive(cls):
        return True


@register_type('enum')
class Enum(Primitive):
    _schema = {'enum': []}
    _enum = []

    def __init__(self, **schema):
        Primitive.__init__(self, **schema)
        self._enum = self._schema.get('enum', self._enum)

    def _check(self, value, **opts):
        return value in self._enum or TypeProtocol._check(self, value, **opts)

    def _convert(self, value, context=None, **opts):
        from .numerics import Integer
        from .strings import String
        enum = self._enum
        if Integer.check(value, **opts):
            i = Integer.convert(value, **opts)
            if i > len(enum):
                raise ConversionError('Index %i exceeds enum size of %r' % (i, enum))
            return enum[i]
        if String.check(value):
            s = String.convert(value, **opts)
            if s in enum:
                return s
        raise ConversionError('Impossible to convert %s to enum %r' % (value, enum))

    def _default(self, **opts):
        return TypeProtocol._default(self, **opts) or self._enum[0]

    def _has_default(self):
        return bool(self._enum) or TypeProtocol._has_default(self)


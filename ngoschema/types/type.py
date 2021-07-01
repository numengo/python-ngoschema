# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from ..protocols.type_protocol import TypeProtocol
from ..managers.type_builder import register_type
from ..utils import ReadOnlyChainMap
from ..resolvers.uri_resolver import resolve_uri, UriResolver
from ..exceptions import InvalidValue, ConversionError
from ..utils import shorten, inline
from .. import settings

logger = logging.getLogger(__name__)


class Type(TypeProtocol):

    def __init__(self, **opts):
        TypeProtocol.__init__(self, **opts)
        from ..managers import type_builder
        schema = dict(self._schema)
        if not self._pyType:
            ty = schema.get('type')
            if 'type' in schema:
                self._pyType = type_builder.get_type(ty)._pyType

    def __call__(self, value, deserialize=True, serialize=False, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        value = self._deserialize(self, value, **opts) if deserialize else value
        return self._serialize(self, value, deserialize=False, **opts) if serialize else value


class Primitive(Type):
    _rawLiterals = False

    @classmethod
    def is_primitive(cls):
        return True

    def __init__(self, **opts):
        Type.__init__(self, **opts)
        self._rawLiterals = self._schema.get('rawLiterals', self._rawLiterals)

    @staticmethod
    def _check(self, value, **opts):
        from collections import Mapping, Sequence
        if not self._pyType:
            if isinstance(value, (Mapping, Sequence)) and not isinstance(value, str):
                raise TypeError('%s is not a primitive.' % shorten(value, str_fun=repr))
            return value
        else:
            return Type._check(self, value, **opts)

    @staticmethod
    def _inputs(self, value, **opts):
        from .strings import Expr, Pattern
        raw_literals = opts.pop('raw_literals', self._rawLiterals)
        if not raw_literals:
            if Pattern.check(value):
                return Pattern.inputs(value, **opts)
            if Expr.check(value):
                return Expr.inputs(value, **opts)
        return set()

    @staticmethod
    def _convert(self, value, **opts):
        from .strings import Expr, Pattern
        raw_literals = opts.pop('raw_literals', self._rawLiterals)
        if value and not raw_literals:
            try:
                if Expr.check(value):
                    value = Expr.convert(value, **opts)
                elif Pattern.check(value):
                    value = Pattern.convert(value, **opts)
            except Exception as er:
                logger.warning('impossible to convert %s: %s', shorten(inline(str(value))), er)
                #logger.error(er, exc_info=True)
        # only convert if not raw literals
        return value if raw_literals else Type._convert(self, value, **opts)


@register_type('enum')
class Enum(Primitive):
    _enum = []

    def __init__(self, **opts):
        Primitive.__init__(self, **opts)
        self._enum = self._schema.get('enum', [])
        if self._enum and not self._default:
            self._default = self._enum[0]

    @staticmethod
    def _check(self, value, **opts):
        if value in self._enum or Primitive._check(self, value, **opts):
            return value
        raise TypeError('%s is not of type enum %s.' % (value, self._enum))

    @staticmethod
    def _convert(self, value, context=None, **opts):
        from .numerics import Integer
        from .strings import String
        enum = self._enum
        if String.check(value):
            s = String.convert(value, **opts)
            if s in enum:
                return s
        if Integer.check(value, convert=True):
            i = Integer.convert(value)
            if i in enum:
                return i
            if i > len(enum):
                raise ConversionError('Index %i exceeds enum size of %r' % (i, enum))
            return enum[i]

        if not s:
            return self._enum[0]
        raise ConversionError('Impossible to convert %s to enum %r' % (value, enum))

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import builtins
import numbers
import decimal
import logging
from past.types import basestring

import re
from ..exceptions import ValidationError, ConversionError, ExpressionError
from .type import Type, TypeChecker
from .. import settings
from ..utils import shorten, inline
from ..utils.jinja2 import TemplatedString

logger = logging.getLogger(__name__)


@TypeChecker.register('literal')
class Literal(Type):
    _py_type = str
    _raw_literals = False

    def __init__(self, **schema):
        Type.__init__(self, **schema)
        if 'rawLiterals' in schema:
            self._raw_literals = schema['rawLiterals']

    @classmethod
    def is_literal(cls):
        return True

    @classmethod
    def convert(cls, value, raw_literals=None, **opts):
        raw_literals = raw_literals or cls._raw_literals
        if raw_literals or value is None:
            return value
        try:
            if Expr.check(value):
                typed = Expr.convert(value, **opts)
            elif Pattern.check(value):
                typed = Pattern.convert(value, **opts)
            else:
                typed = value
        except Exception as er:
            logger.warning('impossible to convert %s: %s', shorten(inline(value)), er)
            logger.error(er, exc_info=True)
            typed = value
        return Type._convert(cls, typed, **opts)

    def inputs(self, value, raw_literals=None, **opts):
        raw_literals = raw_literals or self._raw_literals
        if not raw_literals:
            if Pattern.check(value):
                return Pattern.inputs(value, **opts)
            if Expr.check(value):
                return Expr.inputs(value, **opts)
        return set()

    @classmethod
    def check(cls, value, **opts):
        return Boolean.check(value) or Number.check(value) or Literal._check(cls, value, **opts)

    def _check(cls, value, convert=False, **opts):
        if value is None:
            return False
        if Expr.check(value):
            if not convert:
                return True
            try:
                value = Expr.convert(value, **opts)
                return cls.check(value)
            except Exception as er:
                return False
        return Type._check(cls, value, convert=convert, **opts)

    def default(self, **opts):
        if 'default' in self._schema:
            s = self._schema.get('default')
            if Expr.check(s) or Pattern.check(s):
                return s
            return self(s, validate=False, **opts) if s else s
        return self._py_type() if self._py_type else None


@TypeChecker.register('boolean')
class Boolean(Literal):
    """
    json-schema 'boolean' type
    """
    _schema = {'type': 'boolean'}
    _py_type = bool
    _TRUES = settings.BOOLEAN_TRUE_STR_LIST
    _FALSES = settings.BOOLEAN_FALSE_STR_LIST

    @classmethod
    def check(cls, value, **opts):
        return isinstance(value, bool)

    @classmethod
    def convert(self, value, **opts):
        """
        Converts to boolean.
        If the input is a string, check against the list settings.BOOLEAN_TRUE_STR_LIST
        and settings.BOOLEAN_FALSE_STR_LIST
        If the input is an integer, check 0 or 1

        :param value: value to instanciate
        :param context: evaluation context
        :return: urllib.parse.ParsedResult instance
        """
        if Boolean.check(value, convert=False):
            return value
        if String.check(value):
            value = value.lower()
            if value in self._TRUES:
                return True
            if value in self._FALSES:
                return False
            raise ConversionError('Impossible to convert %s to boolean from %r' % (value, (self._FALSES, self._TRUES)))
        if Integer.check(value):
            value = Integer.convert(value, **opts)
            if value in [0, 1]:
                return bool(value)
        raise ConversionError('Impossible to convert %s to boolean.' % value)

    def default(self, **opts):
        return self._schema.get('default', False)


@TypeChecker.register('integer')
class Integer(Literal):
    """
    json-schema 'integer' type
    """
    _schema = {'type': 'integer'}
    _py_type = int

    @classmethod
    def check(cls, value, **opts):
        return isinstance(value, int)


@TypeChecker.register('string')
class String(Literal):
    """
    json-schema 'string' type
    """
    _schema = {'type': 'string'}
    _py_type = str

    @classmethod
    def check(cls, value, **opts):
        return isinstance(value, str)

    def serialize(self, value, **opts):
        raw_literals = opts.get('raw_literals', self._raw_literals)
        if Pattern.check(value) and not raw_literals:
            try:
                return String.convert(value, **opts)
            except Exception as er:
                pass
        return value


@TypeChecker.register('enum')
class Enum(String):
    _enum = []

    def __init__(self, **schema):
        String.__init__(self, **schema)
        self._enum = self._schema['enum']

    @classmethod
    def check(cls, value, **opts):
        return String.check(value) or Integer.check(value)

    def convert(self, value, context=None, **opts):
        enum = self._enum
        if Integer.check(value, **opts):
            i = Integer.convert(value, **opts)
            if i > len(self._enum):
                raise ConversionError('Index %i exceeds enum size of %r' % (i, enum))
            return self._enum[i]
        if String.check(value):
            s = String.convert(value, **opts)
            if s in self._enum:
                return s
        raise ConversionError('Impossible to convert %s to enum %r' % (value, enum))

    def default(self, **opts):
        return self._schema.get('default') or self._schema['enum'][0]

    def has_default(self):
        return bool(self._enum)


class Expr(Literal):
    _expr_regex = re.compile(r"[a-zA-Z_]+[\w\.]*")

    @staticmethod
    def check(value, **opts):
        return String.check(value) and value.startswith("`")

    @classmethod
    def convert(cls, value, context=None, **opts):
        context = Type._make_context(cls, context, opts)
        typed = eval(str(value)[1:], dict(context))
        return Type._convert(cls, typed, **opts)

    @staticmethod
    def inputs(value, **opts):
        return set(Expr._expr_regex.findall(str(value))).difference(builtins.__dict__)


class Pattern(String):

    @staticmethod
    def check(value, **opts):
        return String.check(value) and ("{{" in value or "{%" in value)

    @classmethod
    def convert(cls, value, context=None, **opts):
        context = Type._make_context(cls, context, opts)
        ctx = context.merged
        ctx.setdefault('this', ctx)
        return TemplatedString(value)(ctx)

    @staticmethod
    def inputs(value, **opts):
        from ngoschema.utils.jinja2 import get_jinja2_variables
        return set(get_jinja2_variables(value))


@TypeChecker.register('number')
class Number(Literal):
    """
    Associate json-schema 'number' to decimal.Decimal
    """
    _schema = {'type': 'number'}
    _py_type = decimal.Decimal
    _dcm_context = decimal.Context()

    @staticmethod
    def check(value, **opts):
        return isinstance(value, (numbers.Number, decimal.Decimal))

    def __init__(self, precision=12, **schema):
        self._dcm_context = decimal.Context(prec=precision)
        super().__init__(**schema)

    def __call__(self, value, **opts):
        decimal.setcontext(self._dcm_context)
        return Literal.__call__(self, value, **opts)


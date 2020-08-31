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
from .type import TypeProtocol, Primitive
from ..managers.type_builder import register_type
from .. import settings
from ..utils.jinja2 import TemplatedString

logger = logging.getLogger(__name__)


#@register_type('literal')
#class Literal(Type):
#    _raw_literals = False
#
#    def __init__(self, **schema):
#        Type.__init__(self, **schema)
#        self._raw_literals = self._schema.get('rawLiterals', self._raw_literals)
#
#    @classmethod
#    def is_primitive(cls):
#        return True
#
#    def _convert(self, value, **opts):
#        raw_literals = opts.pop('raw_literals', self._raw_literals)
#        typed = value
#        if value and not raw_literals:
#            try:
#                if Expr.check(value):
#                    typed = Expr.convert(value, **opts)
#                elif Pattern.check(value):
#                    typed = Pattern.convert(value, **opts)
#            except Exception as er:
#                logger.warning('impossible to convert %s: %s', shorten(inline(str(value))), er)
#                logger.error(er, exc_info=True)
#                typed = value
#            return TypeProtocol._convert(self, typed, **opts)
#        return typed
#
#    def _inputs(self, value, context=None, **opts):
#        raw_literals = opts.pop('raw_literals', self._raw_literals)
#        if not raw_literals:
#            if Pattern.check(value):
#                return Pattern.inputs(value, **opts)
#            if Expr.check(value):
#                return Expr.inputs(value, **opts)
#        return set()


@register_type('string')
class String(Primitive):
    """
    json-schema 'string' type
    """
    _schema = {'type': 'string'}
    _py_type = str

    def _serialize(self, value, **opts):
        raw_literals = opts.get('raw_literals', self._raw_literals)
        if Pattern.check(value) and not raw_literals:
            try:
                return String.convert(value, **opts)
            except Exception as er:
                pass
        return value


class Expr(String):
    _expr_regex = re.compile(r"[a-zA-Z_]+[\w\.]*")

    #@classmethod
    #def check(cls, value, **opts):
    #    return Expr._check(cls, value, **opts)

    def _check(self, value, **opts):
        return String.check(value) and value.startswith("`")

    def _convert(self, value, context=None, **opts):
        TypeProtocol._make_context(self, context, opts)
        typed = eval(str(value)[1:], dict(self._context))
        return TypeProtocol._convert(self, typed, **opts)

    def _inputs(self, value, **opts):
        return set(Expr._expr_regex.findall(str(value))).difference(builtins.__dict__)


class Pattern(String):

    def _check(self, value, **opts):
        return String.check(value) and ("{{" in value or "{%" in value)

    def _convert(self, value, context=None, **opts):
        String._make_context(self, context, opts)
        ctx = self._context.merged
        ctx.setdefault('this', ctx)
        return TemplatedString(value)(ctx)

    def _inputs(self, value, **opts):
        from ngoschema.utils.jinja2 import get_jinja2_variables
        return set(get_jinja2_variables(value))


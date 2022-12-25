# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import builtins
import numbers
import decimal
import ipaddress
import logging
from past.types import basestring

import re
from ..exceptions import ValidationError, ConversionError, ExpressionError
from .type import TypeProtocol, Primitive
from ..managers.type_builder import register_type
from .. import settings
from ..utils.jinja2 import TemplatedString

logger = logging.getLogger(__name__)

# formats (with regex or normalized standard) should be normally be checked through jsch_validators.format


@register_type('string')
class String(Primitive):
    """
    json-schema 'string' type
    """
    _schema = {'type': 'string'}
    _pyType = str
    _length = None
    _minLength = None
    _maxLength = None
    _pattern = None
    _format = None
    _re = None

    def __init__(self, **opts):
        Primitive.__init__(self, **opts)
        self._length = self._schema.get('length', self._length)
        self._minLength = self._schema.get('minLength', self._minLength)
        self._maxLength = self._schema.get('maxLength', self._maxLength)
        self._pattern = self._schema.get('pattern', self._pattern)
        self._format = self._schema.get('format', self._format)
        if self._pattern:
            self._re = re.compile(self._pattern)

    @staticmethod
    def _check(self, value, context=None, **opts):
        value = TypeProtocol._check(self, value, context=None, **opts)
        if self._pattern:
            if not self._re.match(value, **opts):
                raise TypeError('%s is not formatted properly [%s].' % (value, self._pattern))
        return value


class Expr(String):
    _expr_regex = re.compile(r"[a-zA-Z_]+[\w\.]*")

    @staticmethod
    def _check(self, value, **opts):
        if String.check(value) and value.startswith("`"):
            return value
        raise TypeError('%s is not of type "expr".' % value)

    @staticmethod
    def _convert(self, value, context=None, **opts):
        context = context or self._context
        ctx = context.merged
        ctx.setdefault('this', self)
        typed = eval(str(value)[1:], ctx)
        return TypeProtocol._convert(self, typed, **opts)

    @staticmethod
    def _inputs(self, value, **opts):
        return set(Expr._expr_regex.findall(str(value))).difference(builtins.__dict__)


class Pattern(String):

    @staticmethod
    def _check(self, value, **opts):
        if String.check(value) and ("{{" in value or "{%" in value):
            return value
        raise TypeError('%s is not of type "pattern".' % value)

    @staticmethod
    def _convert(self, value, context=None, **opts):
        ctx = (context or self.create_context(**opts)).merged
        ctx.setdefault('this', None)
        if value is not None:
            return TemplatedString(value)(ctx)

    @staticmethod
    def _inputs(self, value, **opts):
        from ngoschema.utils.jinja2 import get_jinja2_variables
        return set(get_jinja2_variables(value))


@register_type('html')
class WebContent(String):
    _schema = {'type': 'html'}

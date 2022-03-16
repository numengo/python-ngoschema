# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import builtins
import numbers
import decimal
import logging
from past.types import basestring

from ..exceptions import ValidationError, ConversionError, ExpressionError
from .type import TypeProtocol, Primitive
from ..managers.type_builder import register_type
from .. import settings

logger = logging.getLogger(__name__)


class Numeric(Primitive):
    _minimum = None
    _maximum = None
    _exclusiveMinimum = None
    _exclusiveMaximum = None

    def __init__(self, **opts):
        Primitive. __init__(self, **opts)
        self._minimum = self._schema.get('minimum', self._minimum)
        self._maximum = self._schema.get('maximum', self._maximum)
        self._exclusiveMinimum = self._schema.get('exclusiveMinimum', self._exclusiveMinimum)
        self._exclusiveMaximum = self._schema.get('exclusiveMaximum', self._exclusiveMaximum)


@register_type('number')
class Number(Numeric):
    _pyType = decimal.Decimal
    _dcmContext = decimal.Context()

    def __init__(self, precision=12, **opts):
        Numeric. __init__(self, **opts)
        self._dcmContext = decimal.Context(prec=precision)

    @staticmethod
    def _check(self, value, **opts):
        if isinstance(value, (numbers.Number, decimal.Decimal, float, int)):
            return value
        raise TypeError('%s is not of type "number".' % value)

    @staticmethod
    def _evaluate(self, value, **opts):
        decimal.setcontext(self._dcmContext)
        return Primitive._evaluate(self, value, **opts)

    @staticmethod
    def _serialize(self, value, **opts):
        return value.to_eng_string(context=self._dcmContext)


@register_type('integer')
class Integer(Numeric):
    _pyType = int

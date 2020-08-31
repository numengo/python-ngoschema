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


@register_type('integer')
class Integer(Primitive):
    """
    json-schema 'integer' type
    """
    _py_type = int


@register_type('number')
class Number(Primitive):
    """
    Associate json-schema 'number' to decimal.Decimal
    """
    _py_type = decimal.Decimal
    _dcm_context = decimal.Context()

    def _check(self, value, **opts):
        return isinstance(value, (numbers.Number, decimal.Decimal)) or TypeProtocol._check(Number, value, **opts)

    def __init__(self, precision=12, **schema):
        self._dcm_context = decimal.Context(prec=precision)
        super().__init__(**schema)

    def __call__(self, value, **opts):
        decimal.setcontext(self._dcm_context)
        return Primitive.__call__(self, value, **opts)

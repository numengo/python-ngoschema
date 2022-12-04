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
from ..utils import shorten, inline
from ..utils.jinja2 import TemplatedString

logger = logging.getLogger(__name__)


@register_type('boolean')
class Boolean(Primitive):
    _pyType = bool
    _TRUES = settings.BOOLEAN_TRUE_STR_LIST
    _FALSES = settings.BOOLEAN_FALSE_STR_LIST

    @staticmethod
    def _convert(self, value, **opts):
        """
        Converts to boolean.
        If the input is a string, check against the list settings.BOOLEAN_TRUE_STR_LIST
        and settings.BOOLEAN_FALSE_STR_LIST
        If the input is an integer, check 0 or 1

        :param value: value to instanciate
        :param context: evaluation context
        :return: urllib.parse.ParsedResult instance
        """
        from .strings import String
        from .numerics import Integer
        if Boolean.check(value):
            return value
        if String.check(value):
            value = value.lower()
            if value in self._TRUES:
                return True
            if value in self._FALSES:
                return False
            raise ConversionError('Impossible to convert %s to boolean from %r'\
                                  % (value, (self._FALSES, self._TRUES)))
        if Integer.check(value):
            value = Integer.convert(value, **opts)
            if value in [0, 1]:
                return bool(value)
        raise ConversionError('Impossible to convert %s to boolean.' % value)


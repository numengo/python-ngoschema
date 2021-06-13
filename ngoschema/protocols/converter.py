# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from ..exceptions import ConversionError
from ..utils import shorten
from .checker import Checker


class Converter(Checker):
    _logger = logging.getLogger(__name__)
    _checker = Checker

    def __init__(self, checker=None, **opts):
        self._checker = checker or self._checker
        self._checker.__init__(self, **opts)

    @staticmethod
    def _convert(self, value, **opts):
        py_type = opts.get('pyType', self._pyType)
        if py_type is None or value is None:
            return value
        if isinstance(value, py_type):
            return value
        try:
            return py_type(value)
        except Exception as er:
            #self._logger.error(er, exc_info=True)
            raise ConversionError("Impossible to convert %r to %s" % (shorten(value, str_fun=repr), self._pyType))

    def __call__(self, value, check=True, **opts):
        return self._convert(self, value, **opts)

    @classmethod
    def check(cls, value, convert=False, **opts):
        try:
            value = cls._convert(cls, value, **opts) if convert else value
            value = cls._check(cls, value, **opts)
            return True
        except Exception as er:
            return False

    @classmethod
    def convert(cls, value, check=True, **opts):
        return cls._convert(cls, value, check=False, **opts)

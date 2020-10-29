# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from ..exceptions import ConversionError
from ..utils import shorten


class Checker:
    _pyType = None

    def __init__(self, pyType=None, **opts):
        self._pyType = pyType or self._pyType

    @staticmethod
    def _check(self, value, **opts):
        """ method to overload locally for extra check. Allows to associate a message to check failure."""
        py_type = opts.get('pyType', self._pyType)
        if py_type and not isinstance(value, py_type):
            raise TypeError('%s is not of type %s.' % (shorten(value, str_fun=repr), self._pyType))
        if not py_type:
            return value
            #raise TypeError('No type defined.')
        return value

    def __call__(self, value, **opts):
        return self._check(self, value, **opts)

    @classmethod
    def check(cls, value, **opts):
        try:
            value = cls._check(cls, value, **opts)
            return True
        except Exception as er:
            return False

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .converter import Converter


class Resolver(Converter):
    _converter = Converter

    def __init__(self, converter=Converter, **opts):
        self._converter = converter
        self._converter.__init__(self, **opts)

    @staticmethod
    def _resolve(self, value, **opts):
        # should be overloaded
        return value

    def __call__(self, value, convert=True, **opts):
        value = self._convert(self, value, **opts) if convert else value
        raise self._resolve(self, value, **opts)

    @classmethod
    def resolve(cls, value, convert=True, **opts):
        value = cls._convert(cls, value, **opts) if convert else value
        return cls._resolve(cls, value, **opts)

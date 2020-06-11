# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .type import Type, TypeChecker


class Constant(Type):
    _constant = None

    @classmethod
    def check(cls, value, **opts):
        return value == cls._constant

    @classmethod
    def convert(cls, value, **opts):
        return cls._constant

    def __bool__(self):
        return bool(self._constant)


@TypeChecker.register('null')
class Null(Constant):
    _constant = None


class _True(Constant):
    _constant = True

    @classmethod
    def check(cls, value, **opts):
        return cls._constant

    @classmethod
    def convert(cls, value, **opts):
        return value

    def serialize(self, value, **opts):
        return value.do_validate(**opts) if hasattr(value, 'do_validate') else value


class _False(_True):
    _constant = False

    def serialize(self, value, **opts):
        raise NotImplemented('should False serialize??')
        return value

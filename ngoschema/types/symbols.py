# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import importlib
import inspect
import types
import re

from ..exceptions import InvalidValue
from ..utils import qualname
from .type import Type, TypeChecker
from .type_builder import TypeBuilder
from .literals import String
from .object import Object


@TypeChecker.register('importable')
class Importable(String):
    """
    Associate json-schema 'importable' to an imported symbol
    """
    _schema = {'type': 'importable'}
    DOT = re.compile(r"\.")

    @classmethod
    def convert(cls, value, context=None, convert=True, **opts):
        typed = value
        if String.check(value, convert=False):
            value = String.convert(value, **opts)
            poss = [m.start() for m in cls.DOT.finditer("%s." % value)]
            # going backwards
            for pos in reversed(poss):
                try:
                    m = value[0:pos]
                    ret = importlib.import_module(m)
                    for a in value[pos + 1:].split("."):
                        if not a:
                            continue
                        ret = getattr(ret, a, None)
                        if not ret:
                            raise InvalidValue("%s is not an importable object" % value)
                    typed = ret
                    break
                except Exception as er:
                    continue
        if typed is not None and not cls.check(typed, convert=False, **opts):
            raise InvalidValue("%s is not a %s" % (value, cls._type))
        return typed

    @classmethod
    def check(cls, value, convert=False, **opts):
        if String.check(value, convert=False) and convert:
            try:
                value = cls.convert(value, **opts)
            except (Exception, InvalidValue) as er:
                return False
        return cls._check_symbol(value)

    @staticmethod
    def _check_symbol(value):
        return Module._check_symbol(value) or Function._check_symbol(value) or Class._check_symbol(value)\
               or Method._check_symbol(value) or Instance._check_symbol(value) or Callable._check_symbol(value)

    def serialize(self, value, **opts):
        if value and not String.check(value):
            m = getattr(value, '__module__', None)
            value = '%s.%s' % (m, qualname(value)) if m else qualname(value)
        return String.serialize(self, value, **opts)


@TypeChecker.register('module')
class Module(Importable):
    _schema = {'type': 'module'}

    @staticmethod
    def _check_symbol(value):
        return isinstance(value, types.ModuleType)

    def serialize(self, value, **opts):
        if value and not String.check(value):
            value = value.__name__
        return String.serialize(self, value, **opts)


@TypeChecker.register('function')
class Function(Importable):
    _schema = {'type': 'function'}

    @staticmethod
    def _check_symbol(value):
        return isinstance(value, types.FunctionType)


@TypeChecker.register('class')
class Class(Importable):
    _schema = {'type': 'class'}

    @staticmethod
    def _check_symbol(value):
        return isinstance(value, type)


@TypeChecker.register('method')
class Method(Importable):
    _schema = {'type': 'method'}

    @staticmethod
    def _check_symbol(value):
        return inspect.ismethod(value)


class StaticMethod(Function):

    @staticmethod
    def _check_symbol(value):
        return Function.check(value) and hasattr(value, '__class__')


class Instance(Importable):

    @staticmethod
    def _check_symbol(value):
        if getattr(value, "__class__"):
            return isinstance(value, value.__class__) and not inspect.isclass(value)
        return False


class Callable(Importable):

    @staticmethod
    def _check_symbol(value):
        if getattr(value, "__class__"):
            return isinstance(value, value.__class__) and not inspect.isclass(value)
        return False



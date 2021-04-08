# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import importlib
import inspect
import types
import re

from ..exceptions import ConversionError
from ..utils import qualname
from ..managers.type_builder import register_type
from .type import TypeProtocol, Primitive
from .strings import String
from .object import Object

logger = logging.getLogger(__name__)


@register_type('importable')
class Symbol(Primitive):
    """
    Associate json-schema 'importable' to an imported symbol
    """
    DOT = re.compile(r"\.")
    _pyType = None
    _builtins = importlib.__builtins__

    @staticmethod
    def _convert(self, value, **opts):
        typed = self._builtins.get(value, value)
        if String.check(typed):
            value = String.convert(typed, **opts)
            poss = [m.start() for m in Symbol.DOT.finditer("%s." % typed)]
            # going backwards
            for pos in reversed(poss):
                try:
                    m = value[0:pos]
                    ret = importlib.import_module(m)
                    for a in typed[pos + 1:].split("."):
                        if not a:
                            continue
                        ret = getattr(ret, a, None)
                        if not ret:
                            raise ConversionError("%s is not an importable object" % value)
                    typed = ret
                    break
                except Exception as er:
                    continue
            else:
                logger.error("%s is not an importable object" % value)
                #raise ConversionError("%s is not an importable object" % value)
        if typed is not None and not self.check_symbol(typed):
            raise ConversionError("%s is not a %s" % (value, self._type))
        return typed

    @staticmethod
    def _check(self, value, **opts):
        if self.check_symbol(value) or TypeProtocol._check(self, value, **opts):
            return value
        raise TypeError('%s is not of type symbol.' % value)

    @classmethod
    def check_symbol(cls, value):
        return isinstance(value, cls._pyType) if cls._pyType else True

    @staticmethod
    def _serialize(self, value, **opts):
        value = String._serialize(self, value, **opts)
        if value:
            if not String.check(value):
                if isinstance(value, types.ModuleType):
                    value = value.__name__
                else:
                    m = getattr(value, '__module__', None)
                    value = '%s.%s' % (m, qualname(value)) if m else qualname(value)
        return value


@register_type('module')
class Module(Symbol):
    _pyType = types.ModuleType

    #def _serialize(self, value, **opts):
    #    if value and not String.check(value):
    #        value = value.__name__
    #    return String._serialize(self, value, **opts)


@register_type('function')
class Function(Symbol):
    _pyType = types.FunctionType


@register_type('class')
class Class(Symbol):
    _pyType = type


@register_type('method')
class Method(Function):
    _pyType = types.MethodType


@register_type('staticmethod')
class StaticMethod(Method):

    @classmethod
    def check_symbol(cls, value):
        return Method.check(value) and hasattr(value, '__class__')


@register_type('classmethod')
class ClassMethod(Method):

    @classmethod
    def check_symbol(cls, value):
        return Method.check(value) and isinstance(value, classmethod)


@register_type('instance')
class Instance(Class):
    _pyType = None

    @classmethod
    def check_symbol(cls, value):
        if getattr(value, "__class__"):
            return isinstance(value, value.__class__) and not isinstance(value, type)
        return False


@register_type('callable')
class Callable(Symbol):
    _pyType = None

    @classmethod
    def check_symbol(cls, value):
        return callable(value)



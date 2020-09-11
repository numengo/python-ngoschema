# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

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


@register_type('importable')
class Symbol(Primitive):
    """
    Associate json-schema 'importable' to an imported symbol
    """
    DOT = re.compile(r"\.")
    _py_type = None
    _builtins = importlib.__builtins__

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
        if typed is not None and not self.check_symbol(typed):
            raise ConversionError("%s is not a %s" % (value, self._type))
        return typed

    def _check(self, value, **opts):
        return self.check_symbol(value) or TypeProtocol._check(self, value, **opts)

    @classmethod
    def check_symbol(cls, value):
        return isinstance(value, cls._py_type) if cls._py_type else True

    def _serialize(self, value, **opts):
        if value and not String.check(value):
            m = getattr(value, '__module__', None)
            value = '%s.%s' % (m, qualname(value)) if m else qualname(value)
        return String._serialize(self, value, **opts)


@register_type('module')
class Module(Symbol):
    _py_type = types.ModuleType

    def _serialize(self, value, **opts):
        if value and not String.check(value):
            value = value.__name__
        return String._serialize(self, value, **opts)


@register_type('function')
class Function(Symbol):
    _py_type = types.FunctionType


@register_type('class')
class Class(Symbol):
    _py_type = type


@register_type('method')
class Method(Function):
    _py_type = types.MethodType


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
    _py_type = None

    @classmethod
    def check_symbol(cls, value):
        if getattr(value, "__class__"):
            return isinstance(value, value.__class__) and not isinstance(value, type)
        return False


@register_type('callable')
class Callable(Symbol):
    _py_type = None

    @classmethod
    def check_symbol(cls, value):
        return callable(value)



# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from ..protocols import TypeProtocol, Serializer
from ..managers.type_builder import register_type
from ..exceptions import InvalidValue


class Constant(TypeProtocol):

    def __init__(self, **opts):
        pass

    def _check(self, value, **opts):
        if self._pyType:
            return value
        raise TypeError(value)

    #def _evaluate(self, value, **opts):
    #    if self.check(value):
    #        return self.convert(value, **opts)
    #    return self._format_errors(value, {'type': f'{value} is not {cls._pyType}'})

    @classmethod
    def __bool__(cls):
        return bool(cls._pyType)

    def _serialize(self, value, **opts):
        return value if self._pyType else None

    #def _has_default(self, **opts):
    #    return False
    #
    #def _default(self, **opts):
    #    return None


@register_type('null')
class Null(Constant):
    _pyType = None


@register_type('true')
class _True(Constant):
    _pyType = True

    @staticmethod
    def _convert(self, value, **opts):
        from .strings import Expr, Pattern, Primitive
        if Expr.check(value) or Pattern.check(value):
            return Primitive.convert(value, **opts)
        return value

    @staticmethod
    def _serialize(self, value, **opts):
        if isinstance(value, Serializer):
            return value._serialize(value, **opts)
        return value

    @staticmethod
    def _validate(self, value, **opts):
        return value


@register_type('false')
class _False(Constant):
    _pyType = False

    @staticmethod
    def _validate(self, value, **opts):
        raise InvalidValue(value)

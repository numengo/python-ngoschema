# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from ..protocols import TypeProtocol
from ..managers.type_builder import register_type


class Constant(TypeProtocol):

    def __init__(self):
        pass

    def __call__(self, value, serialize=False, **opts):
        if self.check(value, convert=True):
            return value
        return self._format_error(value, {'type': f'{value} is not {self._py_type}'})

    @classmethod
    def check(cls, value, **opts):
        return value is None or cls._py_type

    @classmethod
    def convert(cls, value, **opts):
        return cls._py_type

    @classmethod
    def __bool__(cls):
        return bool(cls._py_type)

    @classmethod
    def serialize(cls, value, **opts):
        return cls._py_type

    @classmethod
    def default(cls, **opts):
        return None


@register_type('null')
class Null(Constant):
    _py_type = None


@register_type('true')
class _True(Constant):
    _py_type = True

    @classmethod
    def convert(cls, value, **opts):
        return value

    @classmethod
    def serialize(cls, value, **opts):
        return value.do_serialize(**opts) if hasattr(value, 'do_serialize') else value


@register_type('false')
class _False(Constant):
    _py_type = False


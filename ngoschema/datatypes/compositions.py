# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from .type import Type
from ..utils import shorten, is_mapping
from ..exceptions import ConversionError


class SchemaComposition(Type):
    _keyword = None
    _operator = None
    _types = []

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        for k in set(schema_compositions.keys()).intersection(schema.keys()):
            return schema_compositions[k](id, **schema)

    def __init__(self, id, **opts):
        from ..managers.type_builder import type_builder
        Type.__init__(self, **opts)
        schs = self._schema.get(self._keyword, [])
        self._types = [type_builder.build(f'{id}/{self._keyword}/{i}', s) for i, s in enumerate(schs)]
        self._otypes = tuple([t for t in self._types if t.is_object()])

    ## ADDED FROM Type... to adapt????
    #def __call__(self, value, deserialize=True, serialize=False, **opts):
    #    opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
    #    value = self._deserialize(self, value, **opts) if deserialize else value
    #    return self._serialize(self, value, deserialize=False, **opts) if serialize else value

    @staticmethod
    def _check(self, value, **opts):
        checks = [t.check(value, **opts) for t in self._types]
        return self._operator(checks)

    @staticmethod
    def _convert(self, value, **opts):
        if isinstance(value, self._otypes):
            return value
        for t in self._types:
            if t.check(value, **opts):
                return t.convert(value, **opts)
        raise ConversionError("Impossible to convert %r to any of %s" % (shorten(value, str_fun=repr), list(self._types)))


# OR
class AnyOf(SchemaComposition):
    _keyword = 'anyOf'
    _operator = any


def one_of(*iterable):
    return len([i for i in iterable if i]) == 1


# XOR
class OneOf(SchemaComposition):
    _keyword = 'oneOf'
    _operator = one_of


# AND
class AllOf(SchemaComposition):
    _keyword = 'allOf'
    _operator = all


def not_of(*iterable):
    return not any(*iterable)


#NOT
class NotOf(SchemaComposition):
    _keyword = 'not'
    operator = not_of


schema_compositions = {
    'anyOf': AnyOf,
    'allOf': AllOf,
    'oneOf': OneOf,
    'notOf': NotOf,
}


def is_schema_composition(schema):
    return is_mapping(schema) and set(schema_compositions.keys()).intersection(schema.keys())

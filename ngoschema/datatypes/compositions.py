# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from operator import xor, or_

from ..protocols.type_protocol import TypeProtocol


class SchemaComposition(TypeProtocol):
    _keyword = None
    _keyword_bool = None
    _schemas = []
    _types = []

    def __init__(self, id, **opts):
        from ..managers.type_builder import type_builder
        TypeProtocol.__init__(self, **opts)
        self._schemas = schs = self._schema.get(self._keyword, [])
        self._types = [type_builder.build(f'{id}/{self._keyword}/{i}', s) for i, s in enumerate(schs)]

    # ADDED FROM Type... to adapt????
    def __call__(self, value, deserialize=True, serialize=False, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        value = self._deserialize(self, value, **opts) if deserialize else value
        return self._serialize(self, value, deserialize=False, **opts) if serialize else value


class AnyOf(SchemaComposition):
    _keyword = 'anyOf'
    _keyword_bool = 'OR'

    @staticmethod
    def _check(self, value, **opts):
        for t in self._types:
            if t.check(value):
                return True
        return False

    @staticmethod
    def _convert(self, value, **opts):
        if isinstance(value, self._types):
            return value
        for t in self._types:
            if t.check(value, **opts):
                return t.convert(value, **opts)


class OneOf(SchemaComposition):
    _keyword = 'oneOf'
    _keyword_bool = 'XOR'


class AllOf(SchemaComposition):
    _keyword = 'allOf'
    _keyword_bool = 'AND'


class NotOf(SchemaComposition):
    _keyword = 'not'
    _keyword_bool = 'NOT'

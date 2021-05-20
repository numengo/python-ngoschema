# *- coding: utf-8 -*-
"""
Json Encoder

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals
import collections
import json

import six
from datetime import date, datetime, time, timedelta
from pathlib import Path
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ..protocols import Serializer
from ..registries import serializers_registry


@serializers_registry.register('json')
class JsonSerializer(with_metaclass(SchemaMetaclass, Serializer)):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/JsonSerializer'
    _indent = 2
    _ensure_ascii = False
    _separators = None
    _default = None
    _encoder = json.JSONEncoder(indent=_indent, ensure_ascii=_ensure_ascii, separators=_separators, default=_default)

    def __init__(self, value=None, indent=2, ensure_ascii=False, separators=None, default=None, meta_opts=None, **opts):
        self._indent = indent
        self._ensure_ascii = ensure_ascii
        self._separators = separators
        self._default = default
        self._encoder = json.JSONEncoder(indent=indent, ensure_ascii=ensure_ascii, separators=separators, default=default)
        #ObjectProtocol.__init__(self, value, **opts)
        #Serializer.__init__(self, **(meta_opts or {}), **self)

    @staticmethod
    def _deserialize(self, value, **opts):
        return JsonSerializer._deserialize_json(self, value, **opts)

    @staticmethod
    def _deserialize_json(self, value, **opts):
        value = Serializer._deserialize(self, value, **opts)
        value = self._encoder.decode(value)
        return value

    @staticmethod
    def _serialize(self, value, **opts):
        return JsonSerializer._serialize_json(self, value, **opts)

    @staticmethod
    def _serialize_json(self, value, **opts):
        value = Serializer._serialize(self, value, **opts)
        return self._encoder.encode(value)

    #@classmethod
    def deserialize_json(self, value, **opts):
        return self._deserialize_json(self, value, **opts)

    #@classmethod
    def serialize_json(self, value, **opts):
        return self._serialize_json(self, value, **opts)


def set_json_defaults(kwargs=None):
    kwargs = kwargs or {}
    kwargs.setdefault('indent', 2)
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('separators', None)
    kwargs.setdefault('default', None)
    return kwargs

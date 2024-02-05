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
import gettext

import six
from datetime import date, datetime, time, timedelta
from pathlib import Path
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ..protocols import Serializer, Deserializer
from ..registries import serializers_registry, deserializers_registry
from .instances_serializer import InstanceDeserializer, InstanceSerializer

_ = gettext.gettext


@deserializers_registry.register('json')
class JsonDeserializer(InstanceDeserializer):
    #_json_decoder = json._default_decoder

    @staticmethod
    def _deserialize(self, value, **opts):
        return JsonDeserializer._deserialize_json(self, value, **opts)

    @staticmethod
    def _deserialize_json(self, value, **opts):
        __doc__ = json.loads.__doc__
        #value = self._json_decoder.decode(value)
        value = json.loads(value)
        return Serializer._deserialize(self, value, **opts)

    #@classmethod
    def deserialize_json(self, value, **opts):
        return self._deserialize_json(self, value, **opts)


@serializers_registry.register('json')
class JsonSerializer(with_metaclass(SchemaMetaclass, InstanceSerializer, JsonDeserializer)):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/JsonSerializer'
    _indent = 2
    _ensure_ascii = False
    _separators = None
    _default_val = None
    _json_encoder = json.JSONEncoder(indent=_indent, ensure_ascii=_ensure_ascii, separators=_separators, default=_default_val)

    def __init__(self, value=None, indent=2, ensure_ascii=False, separators=None, default=None, meta_opts=None, **opts):
        self._indent = indent
        self._ensure_ascii = ensure_ascii
        self._separators = separators
        self._default_val = default
        self._json_encoder = json.JSONEncoder(indent=indent, ensure_ascii=ensure_ascii, separators=separators, default=default)
        InstanceSerializer.__init__(**opts, **(meta_opts or {}))
        #ObjectProtocol.__init__(self, value, **opts)
        #Serializer.__init__(self, **(meta_opts or {}), **self)

    @staticmethod
    def _serialize(self, value, **opts):
        return JsonSerializer._serialize_json(self, value, **opts)

    @staticmethod
    def _serialize_json(self, value, **opts):
        #value = Serializer._serialize(self, value, **opts)
        return self._json_encoder.encode(value)

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

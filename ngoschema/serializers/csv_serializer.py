# *- coding: utf-8 -*-
"""
Csv Encoder

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals
import collections
import pandas as pd
import gettext

from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ..protocols import Serializer, Deserializer
from ..registries import serializers_registry, deserializers_registry

_ = gettext.gettext


@deserializers_registry.register('csv')
class CsvDeserializer(Deserializer):

    @staticmethod
    def _deserialize(self, value, **opts):
        return CsvDeserializer._deserialize_csv(self, value, **opts)

    @staticmethod
    def _deserialize_csv(self, value, **opts):
        __doc__ = pd.read_csv.__doc__
        value = pd.read_csv(value, **opts)
        return Serializer._deserialize(self, value, **opts)

    def deserialize_csv(self, value, **opts):
        return self._deserialize_csv(self, value, **opts)


@serializers_registry.register('csv')
class CsvSerializer(with_metaclass(SchemaMetaclass, Serializer, CsvDeserializer)):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/CsvSerializer'

    @staticmethod
    def _serialize(self, value, **opts):
        return CsvSerializer._serialize_csv(self, value, **opts)

    @staticmethod
    def _serialize_csv(self, value, **opts):
        raise NotImplemented('TODO with pandas')

    def serialize_csv(self, value, **opts):
        return self._serialize_csv(self, value, **opts)

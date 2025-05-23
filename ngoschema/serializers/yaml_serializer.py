# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from ruamel import yaml
from ruamel.yaml import YAML
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from ..registries import deserializers_registry, serializers_registry
from ..protocols import Deserializer, Serializer
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from .instances_serializer import InstanceDeserializer, InstanceSerializer


@deserializers_registry.register('yaml')
class YamlDeserializer(InstanceDeserializer):
    _yaml = YAML(typ="safe")

    @staticmethod
    def _deserialize_yaml(self, value, **opts):
        __doc__ = self._yaml.load.__doc__
        return self._yaml.load(value)

    @staticmethod
    def _deserialize(self, value, from_str=False, **opts):
        if from_str:
            value = YamlSerializer._deserialize_yaml(self, value, **opts)
        return InstanceDeserializer._deserialize(self, value, **opts)

    #@classmethod
    def deserialize_yaml(self, value, **opts):
        return self._deserialize_yaml(self, value, **opts)


@serializers_registry.register('yaml')
class YamlSerializer(with_metaclass(SchemaMetaclass, InstanceSerializer, YamlDeserializer)):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/YamlSerializer'
    _deserializer = YamlDeserializer
    _charset = 'utf-8'
    _indent = 2

    def __init__(self,
                 indent=2,
                 charset='utf-8',
                 **opts):
        InstanceSerializer.__init__(self, **opts)
        self._indent = indent
        self._charset = charset

    @staticmethod
    def _serialize_yaml(self, value, **opts):
        __doc__ = self._yaml.safe_dump.__doc__
        yaml.indent = opts.get('indent', self._indent)
        yaml.allow_unicode = opts.get('charset', self._charset)
        output = StringIO()
        self._yaml.safe_dump(value, output, default_flow_style=False, **opts)
        return output.getvalue()

    @staticmethod
    def _serialize(self, value, as_str=False, **opts):
        opts.setdefault('deserialize', False)
        value = InstanceSerializer._serialize(self, value, **opts)
        return YamlSerializer._serialize_yaml(self, value, **opts) if as_str else value

    #@classmethod
    def serialize_yaml(self, value, **opts):
        return self._serialize_yaml(self, value, **opts)

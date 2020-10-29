# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import collections

from ..utils import xmltodict
from ..types import Array
from ..registries import deserializers_registry, serializers_registry
from ..protocols import Deserializer, Serializer
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol


@deserializers_registry.register('xml')
class XmlDeserializer(Deserializer):
    _charset = 'utf-8'
    _process_namespaces = False
    _namespace_separator = ':'
    _disable_entities = True
    _process_comments = False

    def __init__(self, **opts):
        self._process_namespaces = opts.get('process_namespaces', self._process_namespaces)
        self._namespace_separator = opts.get('namespace_separator', self._namespace_separator)
        self._disable_entities = opts.get('disable_entities', self._disable_entities)
        self._process_comments = opts.get('process_comments', self._process_comments)

    @staticmethod
    def _deserialize(self, value, **opts):
        return XmlSerializer._deserialize_xml(self, value, **opts)

    @staticmethod
    def _deserialize_xml(self, value, **opts):
        charset = opts.get('charset', self._charset)
        process_namespaces = opts.get('attr_prefix', self._process_namespaces)
        namespace_separator = opts.get('namespace_separator', self._namespace_separator)
        disable_entities = opts.get('disable_entities', self._disable_entities)
        process_comments = opts.get('attr_prefix', self._process_comments)
        value = xmltodict.parse(value,
                                 encoding=charset,
                                 process_namespaces=process_namespaces,
                                 namespace_separator=namespace_separator,
                                 disable_entities=disable_entities,
                                 process_comments=process_comments)
        value = Serializer._deserialize(self, value, **opts)
        if not self._tag:
            keys = list(value.keys())
            if len(keys) != 1:
                raise NotImplemented('ambiguous request. use tag argument.')
            self._tag = keys[0]
        return value[self._tag]

    @classmethod
    def deserialize_xml(cls, value, **opts):
        return cls._deserialize_xml(cls, value, **opts)


@serializers_registry.register('xml')
class XmlSerializer(with_metaclass(SchemaMetaclass, Serializer, XmlDeserializer)):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/XmlSerializer'
    _deserializer = XmlDeserializer
    _tag = None
    _postprocessor = None
    _attr_prefix = '@'
    _cdata_key = '#text'
    _force_list = True
    _pretty = True
    _indent = '\t'
    _newl = '\n'
    _short_empty_elements = True
    _force_list = ('xs:include', 'xs:import', 'xs:element', 'xs:unique', 'xs:simpleType', 'xs:attributeGroup',
                  'xs:group', 'xs:complexType', 'xs:restriction',
                  'include', 'import', 'element', 'unique', 'simpleType', 'attributeGroup', 'group',
                  'complexType', 'restriction')

    def __init__(self, **opts):
        Serializer.__init__(self, **opts)
        self._tag = tag = opts.get('tag', self._tag)
        self._attr_prefix = attr_prefix = opts.get('attr_prefix', self._attr_prefix)
        self._cdata_key = opts.get('cdata_key', self._cdata_key)
        self._force_list = opts.get('force_list', self._force_list)
        self._pretty = opts.get('pretty', self._pretty)
        self._indent = opts.get('indent', self._indent)
        self._newl = opts.get('newl', self._newl)
        self._short_empty_elements = opts.get('short_empty_elements', self._short_empty_elements)
        if not tag and self._instanceClass:
            self._tag = self._instanceClass.__name__

        # this default post processor makes all non attribute be list
        _prefix = str(attr_prefix)

        def default_postprocessor(path, key, value):
            return (key, value) if key.startswith(_prefix) or key.endswith('schema') else (key, Array.convert(value))

        self._postprocessor = opts.get('postprocessor', default_postprocessor)

    @staticmethod
    def _serialize(self, value, **opts):
        return XmlSerializer._serialize_xml(self, value, **opts)

    @staticmethod
    def _serialize_xml(self, value, **opts):
        value = Serializer._serialize(self, value, **opts)
        tag = opts.get('tag', self._tag)
        attr_prefix = opts.get('attr_prefix', self._attr_prefix)
        cdata_key = opts.get('cdata_key', self._cdata_key)
        force_list = opts.get('force_list', self._force_list)
        pretty = opts.get('pretty', self._pretty)
        indent = opts.get('indent', self._indent)
        newl = opts.get('newl', self._newl)
        short_empty_elements = opts.get('short_empty_elements', self._short_empty_elements)
        value = xmltodict.unparse({tag: value},
                                 attr_prefix=attr_prefix,
                                 cdata_key=cdata_key,
                                 force_list=force_list,
                                 pretty=pretty,
                                 indent=indent,
                                 newl=newl,
                                 short_empty_elements=short_empty_elements,
                                 **opts)
        return value

    @staticmethod
    def _serialize(self, value, **opts):
        return XmlSerializer._serialize_xml(self, value, **opts)

    @classmethod
    def serialize_xml(cls, value, **opts):
        return cls._serialize_xml(cls, value, **opts)

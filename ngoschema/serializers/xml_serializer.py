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
    _processNamespaces = False
    _namespaceSeparator = ':'
    _disableEntities = True
    _processComments = False
    _forceList = ('xs:include', 'xs:import', 'xs:element', 'xs:unique', 'xs:simpleType', 'xs:attributeGroup',
                  'xs:group', 'xs:complexType', 'xs:restriction',
                  'include', 'import', 'element', 'unique', 'simpleType', 'attributeGroup', 'group',
                  'complexType', 'restriction')

    def __init__(self, **opts):
        self._processNamespaces = opts.get('process_namespaces', XmlDeserializer._processNamespaces)
        self._namespaceSeparator = opts.get('namespace_separator', XmlDeserializer._namespaceSeparator)
        self._disableEntities = opts.get('disable_entities', XmlDeserializer._disableEntities)
        self._processComments = opts.get('process_comments', XmlDeserializer._processComments)
        self._forceList = opts.get('force_list', XmlDeserializer._forceList)
        Deserializer.__init__(self, **opts, **self)

    @staticmethod
    def _deserialize(self, value, **opts):
        return XmlSerializer._deserialize_xml(self, value, **opts)

    @staticmethod
    def _deserialize_xml(self, value, **opts):
        charset = opts.get('charset', self._charset)
        process_namespaces = opts.get('attr_prefix', self._processNamespaces)
        namespace_separator = opts.get('namespace_separator', self._namespaceSeparator)
        disable_entities = opts.get('disable_entities', self._disableEntities)
        process_comments = opts.get('attr_prefix', self._processComments)
        force_list = opts.get('force_list', self._forceList)
        value = xmltodict.parse(value,
                                 encoding=charset,
                                 force_list=force_list,
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

    #@classmethod
    def deserialize_xml(self, value, **opts):
        return self._deserialize_xml(self, value, **opts)


@serializers_registry.register('xml')
class XmlSerializer(with_metaclass(SchemaMetaclass, Serializer, XmlDeserializer)):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/XmlSerializer'
    _deserializer = XmlDeserializer
    _tag = None
    _postprocessor = None
    _attrPrefix = '@'
    _cdataKey = '#text'
    _pretty = True
    _indent = '\t'
    _newl = '\n'
    _shortEmptyElements = True

    def __init__(self, **opts):
        Serializer.__init__(self, **opts)
        self._tag = tag = opts.get('tag', XmlSerializer._tag)
        self._attrPrefix = attr_prefix = opts.get('attr_prefix', XmlSerializer._attrPrefix)
        self._cdataKey = opts.get('cdata_key', XmlSerializer._cdataKey)
        self._forceList = opts.get('force_list', XmlSerializer._forceList)
        self._pretty = opts.get('pretty', XmlSerializer._pretty)
        self._indent = opts.get('indent', XmlSerializer._indent)
        self._newl = opts.get('newl', XmlSerializer._newl)
        self._shortEmptyElements = opts.get('short_empty_elements', XmlSerializer._shortEmptyElements)
        if not tag and self._instanceClass:
            self._tag = self._instanceClass.__name__

        # this default post processor makes all non attribute be list
        _prefix = str(attr_prefix)

        def default_postprocessor(path, key, value):
            return (key, value) if key.startswith(_prefix) or key.endswith('schema') else (key, Array.deserialize(value))

        self._postprocessor = opts.get('postprocessor', default_postprocessor)

    @staticmethod
    def _serialize(self, value, **opts):
        return XmlSerializer._serialize_xml(self, value, **opts)

    @staticmethod
    def _serialize_xml(self, value, **opts):
        value = Serializer._serialize(self, value, **opts)
        tag = opts.get('tag', self._tag)
        attr_prefix = opts.get('attr_prefix', self._attrPrefix)
        cdata_key = opts.get('cdata_key', self._cdataKey)
        force_list = opts.get('force_list', self._forceList)
        pretty = opts.get('pretty', self._pretty)
        indent = opts.get('indent', self._indent)
        newl = opts.get('newl', self._newl)
        short_empty_elements = opts.get('short_empty_elements', self._shortEmptyElements)
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

    #@classmethod
    def serialize_xml(self, value, **opts):
        return self._serialize_xml(self, value, **opts)

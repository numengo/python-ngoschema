# *- coding: utf-8 -*-
"""
Base class for loading objects from files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import six
import logging
from abc import abstractmethod

from future.utils import with_metaclass

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import json
from ruamel import yaml
from ruamel.yaml import YAML

from ..decorators import assert_arg
from ..exceptions import InvalidOperation, InvalidValue
from ..utils import file_link_format
from ..utils import xmltodict
from ..datatypes import Path, PathFile
from ..datatypes import Array, Tuple
from ..managers.type_builder import wrap
from ..serializers.instances_serializer import InstanceSerializer, InstanceDeserializer
from ..serializers.file_serializer import FileSaver
from ..serializers.json_serializer import JsonSerializer, JsonDeserializer
from ..serializers.xml_serializer import XmlSerializer, XmlDeserializer
from ..serializers.yaml_serializer import YamlSerializer, YamlDeserializer
from ..protocols import SchemaMetaclass, with_metaclass
from ..protocols.object_protocol import ObjectProtocol
from ..datatypes.object import Serializer, ObjectSerializer, ObjectDeserializer, Object
from ..protocols.repository import Repository
from ..registries import repositories_registry
from ..models.files import File, Document
#from .models.instances import InstanceList, Entity

logger = logging.getLogger(__name__)


@repositories_registry.register('file')
class FileRepository(with_metaclass(SchemaMetaclass, Repository, FileSaver)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/FileRepository'
    _saver = FileSaver
    _encoder = Serializer

    def __init__(self, value=None, meta_opts=None, **opts):
        ObjectProtocol.__init__(self, value, **opts)
        opts.update(self.no_defaults())
        # FileSaver.__init__(self, **opts)  # Saver already initialized in Repository, only misses filepath
        Repository.__init__(self, **opts)
        FileSaver.set_filepath(self, opts.get('filepath'))
        # to initialize the encoder
        meta_opts = meta_opts or {}
        meta_opts.setdefault('instance_class', self._instanceClass)
        self._encoder.__init__(self, **meta_opts)

    @staticmethod
    def _commit(self, value, filepath=None, with_tags=True, many=False, **opts):
        values_all = Repository._commit(self, value, many=many, save=False, **opts)
        #values_serialized = self._serializer._serialize(self, values_all, many=many, with_tags=with_tags, **opts)
        stream = self._encoder._serialize(self, values_all, many=many, with_tags=with_tags, as_str=True, **opts)
        filepath = self.set_filepath(filepath) if filepath else self._filepath
        if not filepath:
            self._logger.error("missing filepath to dump values")
            return
        if not filepath.parent.exists():
            self._logger.info("creating missing directory '%s'", file_link_format(filepath.parent))
            os.makedirs(str(filepath.parent))
        if filepath.exists():
            orig = filepath.open().read()
            if stream == orig:
                self._logger.info("File '%s' already exists with same content. Not overwriting.",
                                  file_link_format(filepath))
                return
        self._logger.info("DUMP %s", file_link_format(filepath))
        self._logger.debug("data:\n%r ", stream)
        self.save(stream, serialize=False)
        return self


@assert_arg(0, PathFile)
def load_object_from_file(fp, repository_class=None, session=None, file_opts=None, repo_opts=None, **opts):
    repo_class = repository_class or JsonFileRepository
    repo = repo_class(repo_opts or {}, session=session)
    logger.info("LOAD %s from %s", repo._instanceClass or '<class unknown>', file_link_format(fp))
    return repo.load_file(fp, session=repo.session)


@assert_arg(1, Path)
def serialize_object_to_file(obj, fp, repository_class=None, session=None, **opts):
    repo_class = repository_class or JsonFileRepository
    repo = repo_class(filepath=fp, session=session, **opts)
    logger.info("DUMP %s from %s", repo._instanceClass, file_link_format(fp))
    repo.commit(obj, **opts)


@repositories_registry.register('json')
class JsonFileRepository(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/JsonFileRepository'
    _encoder = JsonSerializer
    _deserializer = InstanceDeserializer
    _serializer = InstanceSerializer
    #_instanceClass = Document
    #instanceClass = None

    def __init__(self, value=None, **opts):
        FileRepository.__init__(self, value, **opts)

    #@staticmethod
    #def _serialize(self, data, **opts):
    #    # TODO: suppress _serialize from Repository to use the one in Serializer
    #    return json.dumps(
    #        data,
    #        indent=self.get("indent", 2),
    #        ensure_ascii=self.get("ensure_ascii", False),
    #        separators=self.get("separators", None),
    #        default=self.get("default", None))


@assert_arg(0, PathFile)
def load_json_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp, repository_class=JsonFileRepository, session=session, **kwargs)


@assert_arg(1, Path)
def save_to_json(obj, fp, session=None, **kwargs):
    kwargs.setdefault('evaluate', False)
    return serialize_object_to_file(obj, fp, repository_class=JsonFileRepository, session=session, **kwargs)


@repositories_registry.register('yaml')
class YamlFileRepository(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/YamlFileRepository'
    _encoder = YamlSerializer
    _deserializer = InstanceDeserializer
    _serializer = InstanceSerializer
    #instanceClass = Document

    # CRO 15/1/23: try to refactor and get rid of (de)serialize_data functions
    # which should be done at the encoder level
    #def deserialize_data(self):
    #    data = self.document._serialize(self._yaml.load, **self._extended_properties)
    #    return data
    #
    #def serialize_data(self, data):
    #    yaml.indent = self.get("indent", 2)
    #    yaml.allow_unicode = self.get("encoding", "utf-8") == "utf-8"
    #
    #    output = StringIO()
    #    self._yaml.safe_dump(data, output, default_flow_style=False, **self._extended_properties)
    #    return output.getvalue()


@assert_arg(0, PathFile)
def load_yaml_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp, repository_class=YamlFileRepository, session=session, **kwargs)


@assert_arg(1, Path)
def save_to_yaml(obj, fp, session=None, **kwargs):
    return serialize_object_to_file(obj, fp, repository_class=YamlFileRepository, session=session, **kwargs)


@repositories_registry.register('xml')
class XmlFileRepository(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/XmlFileRepository'
    _encoder = XmlSerializer
    _deserializer = InstanceDeserializer
    _serializer = InstanceSerializer
    #instanceClass = Document
    #_tag = None

    def __init__(self, value=None, postprocessor=None, **opts):
        FileRepository.__init__(self, value, **opts)
        #self._instanceClass = opts.get('instanceClass', self._instanceClass)
        #self._serializer = JsonSerializer(no_defaults=self.no_defaults,
        #                                  use_entity_keys=self.use_entity_keys)
        #self.tag = self._tag = self.tag or self._tag or self._instanceClass.__name__
        # this default post processor makes all non attribute be list
        _prefix = str(self._attrPrefix)

        def default_postprocessor(path, key, value):
            return (key, value) if key.startswith(_prefix) or key.endswith('schema') else (key, Array.convert(value))

        self._postprocessor = postprocessor or default_postprocessor

    #def deserialize_data(self):
    #    force_list = ('xs:include', 'xs:import', 'xs:element', 'xs:unique', 'xs:simpleType', 'xs:attributeGroup',
    #                  'xs:group', 'xs:complexType', 'xs:restriction',
    #                  'include', 'import', 'element', 'unique', 'simpleType', 'attributeGroup', 'group',
    #                  'complexType', 'restriction')
    #
    #    parsed = self.document._serialize(xmltodict.parse,
    #                                      attr_prefix=str(self.attr_prefix),
    #                                      cdata_key=str(self.cdata_key),
    #                                      force_list=force_list,
    #                                      #postprocessor=self._postprocessor
    #                                      )
    #    if not self._tag:
    #        keys = list(parsed.keys())
    #        if len(keys) != 1:
    #            raise NotImplemented('ambiguous request. use tag argument.')
    #        self._tag = keys[0]
    #    return parsed[self._tag]

    #def serialize_data(self, data):
    #    return xmltodict.unparse(
    #        {self._tag: data},
    #        pretty=bool(self.pretty),
    #        indent=str(self.indent),
    #        newl=str(self.newl),
    #        attr_prefix=str(self.attr_prefix),
    #        cdata_key=str(self.cdata_key),
    #        short_empty_elements=bool(self.short_empty_elements)
    #    )


@assert_arg(0, PathFile)
def load_xml_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp,
                                 repository_class=XmlFileRepository,
                                 session=session,
                                 **kwargs)


@assert_arg(1, Path)
def save_to_xml(obj, fp, session=None, **kwargs):
    return serialize_object_to_file(obj, fp, repository_class=XmlFileRepository, session=session, **kwargs)

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


from ..decorators import assert_arg
from ..utils import file_link_format
from ..datatypes import Path, PathFile
from ..datatypes import Array
from ..serializers.instances_serializer import InstanceSerializer, InstanceDeserializer
from ..serializers.file_serializer import FileSaver
from ..serializers.json_serializer import JsonSerializer
from ..serializers.xml_serializer import XmlSerializer
from ..serializers.yaml_serializer import YamlSerializer
from ..protocols import SchemaMetaclass, with_metaclass
from ..protocols.object_protocol import ObjectProtocol
from ..datatypes.object import Serializer
from ..protocols.repository import Repository
from ..registries import repositories_registry
from .memory_repository import MemoryRepository, DataframeRepository

logger = logging.getLogger(__name__)


@repositories_registry.register('file')
class FileRepository(with_metaclass(SchemaMetaclass, MemoryRepository, FileSaver)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/FileRepository'
    _saver = FileSaver
    _encoder = Serializer

    def __init__(self, value=None, meta_opts=None, **opts):
        MemoryRepository.__init__(self, value, meta_opts=meta_opts, **opts)
        opts.update(self.no_defaults())
        # FileSaver.__init__(self, **opts)  # Saver already initialized in Repository, only misses filepath
        FileSaver.set_filepath(self, opts.get('filepath'))
        # to initialize the encoder
        meta_opts = meta_opts or opts
        meta_opts.setdefault('instance_class', self._instanceClass)
        self._encoder.__init__(self, **meta_opts)

    @staticmethod
    def _commit(self, value=None, filepath=None, dump_file=True, with_tags=True, many=False, **opts):
        # one or more values can be commited, using the many optional argument
        if value is not None:
            values_all = MemoryRepository._commit(self, value, many=many, save=False, **opts)
        else:
            values_all = self._content
        # out of _commit comes the whole content of the repository, so the following commands should use the setting of the repository
        # already done in encoder ! values_serialized = self._serializer._serialize(self, values_all, many=self._many, with_tags=with_tags, **opts)
        if dump_file:
            stream = self._encoder._serialize(self, values_all, many=self._many, with_tags=with_tags, as_str=True, **opts)
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
            return stream


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

    def __init__(self, value=None, **opts):
        FileRepository.__init__(self, value, **opts)


@assert_arg(0, PathFile)
def load_object_from_file_json(fp, session=None, **kwargs):
    return load_object_from_file(fp, repository_class=JsonFileRepository, session=session, **kwargs)


@assert_arg(1, Path)
def save_object_to_file_json(obj, fp, session=None, **kwargs):
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
def load_object_from_file_yaml(fp, session=None, **kwargs):
    return load_object_from_file(fp, repository_class=YamlFileRepository, session=session, **kwargs)


@assert_arg(1, Path)
def save_object_to_file_yaml(obj, fp, session=None, **kwargs):
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
def load_object_from_file_xml(fp, session=None, **kwargs):
    return load_object_from_file(fp,
                                 repository_class=XmlFileRepository,
                                 session=session,
                                 **kwargs)


@assert_arg(1, Path)
def save_object_to_file_xml(obj, fp, session=None, **kwargs):
    return serialize_object_to_file(obj, fp, repository_class=XmlFileRepository, session=session, **kwargs)


class CsvFileRepository(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/repositories/$defs/CsvFileRepository"
    #_loader = pd.read_csv

    @staticmethod
    def _serialize(self, value, **opts):
        return ObjectProtocol._serialize(self, value, **opts)
        #return CsvSerializer._serialize_csv(self, value, **opts)

    @staticmethod
    def _deserialize(self, value, **opts):
        return ObjectProtocol._deserialize(self, value, **opts)
        #return CsvSerializer._serialize_csv(self, value, **opts)

    def get_dataframe(self):
        return pd.read_csv(str(self.csv))

    def get_by_id(self, *identity_keys):
        return DataframeRepository.get_by_id(self, *identity_keys)


@assert_arg(0, PathFile)
def load_object_from_file_csv(fp, session=None, **kwargs):
    return load_object_from_file(fp,
                                 repository_class=CsvFileRepository,
                                 session=session,
                                 **kwargs)


@assert_arg(1, Path)
def save_object_to_file_csv(obj, fp, session=None, **kwargs):
    return serialize_object_to_file(obj, fp, repository_class=CsvFileRepository, session=session, **kwargs)

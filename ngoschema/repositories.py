# *- coding: utf-8 -*-
"""
Base class for loading objects from files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import logging
from abc import abstractmethod

from future.utils import with_metaclass

from .types import Path, PathFile
from .decorators import assert_arg
from .session import session_maker, scoped_session

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import json
from ruamel import yaml
from ruamel.yaml import YAML
from ngoschema.utils import xmltodict, file_link_format

from .exceptions import InvalidOperation
from .query import Query
#from .protocol_base import ProtocolBase
from .models.document import Document
#from .schema_metaclass import SchemaMetaclass
from .utils.json import ProtocolJSONEncoder
from .utils import Registry, GenericClassRegistry, filter_collection
from .models.entity import Entity, NamedEntity
from .types import ObjectMetaclass, ObjectProtocol, Array

logger = logging.getLogger(__name__)

repository_registry = GenericClassRegistry()


class Repository(with_metaclass(ObjectMetaclass)):
    """
    Class to store read/write operations of objects
    """
    _schema_id = 'https://numengo.org/ngoschema/repositories#/$defs/Repository'

    def __init__(self, **kwargs):
        ObjectProtocol.__init__(self, **kwargs)
        self._catalog = Registry()
        self._pkeys = None
        if self.primaryKeys is not None and self.primaryKeys:
            self._pkeys = tuple(self.primaryKeys)
        elif self.objectClass and issubclass(self.objectClass, Entity):
            self._pkeys = tuple(self.objectClass._primaryKeys)
        self._session = None
        self._encoder = ProtocolJSONEncoder(no_defaults=self.no_defaults, use_entity_ref=self.use_entity_ref)

    @property
    def session(self):
        return self._session

    def _identity_key(self, instance):
        if self.objectClass and not isinstance(instance, self.objectClass):
            raise Exception("%r is not an instance of %r" % (instance, self.objectClass))
        if self._pkeys:
            if len(self._pkeys) == 1:
                k = self._pkeys[0]
                return instance._property_type(k).serialize(instance[k])
            else:
                return tuple([instance._property_type(k).serialize(instance[k]) for k in self._pkeys])
        return id(instance)

    def register(self, instance):
        self._catalog.register(self._identity_key(instance), instance)
        if isinstance(instance, ObjectProtocol):
            instance._repo = self

    def unregister(self, instance):
        self._catalog.unregister(self._identity_key(instance))
        if isinstance(instance, ObjectProtocol):
            instance._repo = None

    def get_instance(self, key):
        return self._catalog[key]

    @property
    def instances(self):
        return list(self._catalog.values())

    def filter(self, *attrs, order_by=False, **attrs_value):
        """
        Make a `Query` on registered documents
        """
        __doc__ = Query.filter.__doc__
        return Query(self.instances).filter(
            *attrs, order_by=order_by, **attrs_value)

    def pre_commit(self):
        values = self.instances
        if not self.many:
            if not len(values)==1:
                raise Exception('handler is configured for 1 registered objects (%i).' % len(list(values)))
            o = values[0]
            #o.do_validate()
            return self._encoder.default(o)
        else:
            return [self._encoder.default(o) for o in values if o.do_validate()]

    @abstractmethod
    def commit(self):
        data = self.pre_commit()
        pass

    @abstractmethod
    def pre_load(self):
        return {}

    def load(self):
        data = self.pre_load()
        if self.many:
            objs = [self.objectClass(**d) if self.objectClass else d for d in data]
            for obj in objs:
                self.register(obj)
            return objs
        else:
            obj = self.objectClass(**data) if self.objectClass else data
            self.register(obj)
            return obj


class FilterRepositoryMixin(object):
    _schema_id = 'https://numengo.org/ngoschema/repositories#/$defs/FilterRepositoryMixin'

    def filter_data(self, data):
        only = self.only.for_json() if self.only else ()
        but = self.but.for_json() if self.but else ()
        rec = bool(self.recursive)
        return filter_collection(data, only, but, rec)


class MemoryRepository(with_metaclass(ObjectMetaclass, Repository, FilterRepositoryMixin)):
    _schema_id = 'https://numengo.org/ngoschema/repositories#/$defs/MemoryRepository'

    def commit(self):
        raise InvalidOperation('commit is not possible with MemoryRepository')

    def pre_load(self):
        return {}
        raise InvalidOperation('pre_load is not possible with MemoryRepository')


class FileRepository(with_metaclass(ObjectMetaclass, Repository, FilterRepositoryMixin)):
    _schema_id = 'https://numengo.org/ngoschema/repositories#/$defs/FileRepository'

    def __init__(self, filepath=None, document=None, **kwargs):
        if filepath is not None:
            document = document or Document()
            document.filepath = filepath
        Repository.__init__(self, document=document, **kwargs)

    @abstractmethod
    def deserialize_data(self):
        pass

    def pre_load(self):
        doc = self.document
        if not doc.loaded:
            doc.load()
        data = self.deserialize_data()
        data = self.filter_data(data)
        return data

    @abstractmethod
    def serialize_data(self, data):
        pass

    def dumps(self):
        data = self.pre_commit()
        return self.serialize_data(data)

    def commit(self):
        stream = self.dumps()
        doc = self.document
        fpath = doc.filepath
        if not fpath.parent.exists():
            self._logger.info("creating missing directory '%s'", file_link_format(fpath.parent))
            os.makedirs(str(fpath.parent))
        if fpath.exists():
            doc.load()
            if stream == doc.contentRaw:
                self._logger.info("File '%s' already exists with same content. Not overwriting.", file_link_format(fpath))
                return

        self._logger.info("DUMP %s", file_link_format(fpath))
        self._logger.debug("data:\n%r ", stream)
        doc.write(stream)


@assert_arg(0, PathFile)
def load_object_from_file(fp, repo=None, session=None, **kwargs):
    session = session or scoped_session(session_maker())()
    repo = repo or JsonFileRepository
    handler = repo(filepath=fp, **kwargs)
    session.bind_repo(handler)
    logger.info("LOAD %s from %s", handler.objectClass or '<class unknown>', file_link_format(fp))
    handler.load()
    instances = handler.instances
    return instances if handler.many else instances[0]


@assert_arg(1, Path)
def serialize_object_to_file(obj, fp, repo=None, session=None, **kwargs):
    session = session or scoped_session(session_maker())()
    repo = repo or JsonFileRepository
    handler = repo(filepath=fp, **kwargs)
    session.bind_repo(handler)
    logger.info("DUMP %s from %s", handler.objectClass, file_link_format(fp))
    handler.register(obj)
    handler.commit()


@repository_registry.register()
class JsonFileRepository(with_metaclass(ObjectMetaclass, FileRepository)):
    _schema_id = 'https://numengo.org/ngoschema/repositories#/$defs/JsonFileRepository'

    def __init__(self, **kwargs):
        FileRepository.__init__(self, **kwargs)

    def deserialize_data(self):
        data = self.document._deserialize(json.loads, **{k: v for k, v in self.do_validate().items() if k not in self._properties})
        return data

    def serialize_data(self, data):
        return json.dumps(
            data,
            indent=self.get("indent", 2),
            ensure_ascii=self.get("ensure_ascii", False),
            separators=self.get("separators", None),
            default=self.get("default", None),
        )


@assert_arg(0, PathFile)
def load_json_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp, repo=JsonFileRepository, session=session, **kwargs)


@repository_registry.register()
class YamlFileRepository(with_metaclass(ObjectMetaclass, FileRepository)):
    _schema_id = 'https://numengo.org/ngoschema/repositories#/$defs/YamlFileRepository'
    _yaml = YAML(typ="safe")

    def deserialize_data(self):
        data = self.document._deserialize(self._yaml.load, **self._extended_properties)
        return data

    def serialize_data(self, data):
        yaml.indent = self.get("indent", 2)
        yaml.allow_unicode = self.get("encoding", "utf-8") == "utf-8"

        output = StringIO()
        self._yaml.safe_dump(data, output, default_flow_style=False, **self._extended_properties)
        return output.getvalue()


@assert_arg(0, PathFile)
def load_yaml_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp, repo=YamlFileRepository, session=session, **kwargs)


@repository_registry.register()
class XmlFileRepository(with_metaclass(ObjectMetaclass, FileRepository)):
    _schema_id = 'https://numengo.org/ngoschema/repositories#/$defs/XmlFileRepository'

    def __init__(self, tag=None, postprocessor=None, **kwargs):
        FileRepository.__init__(self, **kwargs)
        self._encoder = ProtocolJSONEncoder(no_defaults=self.no_defaults,
                                            use_entity_ref=self.use_entity_ref)
        self._tag = tag
        if not tag and self.objectClass:
            self._tag = self.objectClass.__name__

        # this default post processor makes all non attribute be list
        _prefix = str(self.attr_prefix)

        def default_postprocessor(path, key, value):
            return (key, value) if key.startswith(_prefix) or key.endswith('schema') else (key, Array.convert(value))

        self._postprocessor = postprocessor or default_postprocessor

    def deserialize_data(self):
        force_list = ('xs:include', 'xs:import', 'xs:element', 'xs:unique', 'xs:simpleType', 'xs:attributeGroup',
                      'xs:group', 'xs:complexType', 'xs:restriction',
                      'include', 'import', 'element', 'unique', 'simpleType', 'attributeGroup', 'group',
                      'complexType', 'restriction')

        parsed = self.document._deserialize(xmltodict.parse,
                                          attr_prefix=str(self.attr_prefix),
                                          cdata_key=str(self.cdata_key),
                                          force_list=force_list,
                                          #postprocessor=self._postprocessor
                                          )
        if not self._tag:
            keys = list(parsed.keys())
            if len(keys) != 1:
                raise NotImplemented('ambiguous request. use tag argument.')
            self._tag = keys[0]
        return parsed[self._tag]

    def serialize_data(self, data):
        return xmltodict.unparse(
            {self._tag: data},
            pretty=bool(self.pretty),
            indent=str(self.indent),
            newl=str(self.newl),
            attr_prefix=str(self.attr_prefix),
            cdata_key=str(self.cdata_key),
            short_empty_elements=bool(self.short_empty_elements)
        )


@assert_arg(0, PathFile)
def load_xml_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp,
                                 repo=XmlFileRepository,
                                 session=session,
                                 **kwargs)



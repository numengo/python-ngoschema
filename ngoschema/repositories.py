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
import subprocess
import tempfile
from abc import abstractmethod

import six
from future.utils import with_metaclass

from .decorators import assert_arg, SCH_PATH_FILE, SCH_PATH
from .session import session_maker, scoped_session
from .utils import default_jinja2_env, TemplatedString
from .utils.jinja2 import _jinja2_globals

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import json
from ruamel import yaml
from ruamel.yaml import YAML
import xmltodict

from .exceptions import InvalidOperationException
from .query import Query
from .protocol_base import ProtocolBase
from .models.document import Document
from .schema_metaclass import SchemaMetaclass
from .utils.json import ProtocolJSONEncoder
from .utils import Registry, GenericClassRegistry, filter_collection, is_mapping, is_sequence, to_list
from .models.entity import Entity, NamedEntity

logger = logging.getLogger(__name__)

repository_registry = GenericClassRegistry()


class Repository(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to store read/write operations of objects
    """
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/Repository"

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)
        self._catalog = Registry()
        self._class = self.objectClass._imported if self.objectClass is not None else None
        self._pkeys = None
        if self.primaryKeys is not None and self.primaryKeys:
            self._pkeys = self.primaryKeys.for_json()
        elif issubclass(self._class, Entity):
            self._pkeys = tuple(self._class._primaryKeys)
        self._session = None
        self._encoder = ProtocolJSONEncoder(no_defaults=self.no_defaults, remove_refs=self.remove_refs)

    @property
    def session(self):
        return self._session

    def _identity_key(self, instance):
        if self._class and not isinstance(instance, self._class):
            raise Exception("%r is not an instance of %r" % (instance, self._class))
        if self._pkeys:
            if len(self._pkeys) == 1:
                return instance._get_prop_value(self._pkeys[0])
            else:
                return tuple([instance._get_prop_value(k) for k in self._pkeys])
        return id(instance)

    def register(self, instance):
        self._catalog.register(self._identity_key(instance), instance)
        instance._handler = self

    def unregister(self, instance):
        self._catalog.unregister(self._identity_key(instance))
        instance._handler = None

    def get_instance(self, key):
        return self._catalog[key]

    def resolve_cname_path(self, cname):
        # use generators because of 'null' which might lead to different paths
        def _resolve_cname_path(cn, cur, cur_cn, cur_path):
            cn = [e.replace('<anonymous>', 'null') for e in cn]
            # empty path, yield current path and doc
            if not cn:
                yield cur, cn, cur_path
            if is_mapping(cur):
                cn2 = cur_cn + [cur.get('name', 'null')]
                if cn2 == cn[0:len(cn2)]:
                    if cn2 == cn:
                        yield cur, cn, cur_path
                    for k, v in cur.items():
                        if is_mapping(v) or is_sequence(v):
                            for _ in _resolve_cname_path(cn, v, cn2, cur_path + [k]):
                                yield _
            if is_sequence(cur):
                for i, v in enumerate(cur):
                    for _ in _resolve_cname_path(cn, v, cur_cn, cur_path + [i]):
                        yield _

        cn_path = cname.split('.')
        for i in self.instances:
            if not isinstance(i, NamedEntity) and cname.startswith(str(i.canonicalName)):
                continue
            # found ancestor
            cur_cn = []
            # first search without last element, as last one might not be a named object
            # but the name of an attribute
            for d, c, p in _resolve_cname_path(cn_path[:-1], i, cur_cn, []):
                if cn_path[-1] in d or d.get('name', '<anonymous>') == cn_path[-1]:
                    p.append(cn_path[-1])
                    return i, p
                # we can continue the search from last point. we remove the last element of the
                # canonical name which is going to be read again
                for d2, c2, p2 in _resolve_cname_path(cn_path, d, c[:-1], p):
                    return i, p2
        raise Exception("Unresolvable canonical name '%s' in '%s'" % (cname, i))

    def resolve_cname(self, cname):
        cur, path = self.resolve_cname_path(cname)
        for p in path:
            cur = cur[p]
        return cur

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
            return self._encoder.default(values[0])
        else:
            return [self._encoder.default(o) for o in values]

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
            objs = [self._class(**d) if self._class else d for d in data]
            for obj in objs:
                self.register(obj)
            return objs
        else:
            obj = self._class(**data) if self._class else data
            self.register(obj)
            return obj


class FilterRepositoryMixin(object):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/FilterRepositoryMixin"

    def filter_data(self, data):
        only = self.only.for_json() if self.only else ()
        but = self.but.for_json() if self.but else ()
        rec = bool(self.recursive)
        return filter_collection(data, only, but, rec)


class MemoryRepository(with_metaclass(SchemaMetaclass, Repository, FilterRepositoryMixin)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/MemoryRepository"

    def commit(self):
        raise InvalidOperationException('commit is not possible with MemoryRepository')

    def pre_load(self):
        return {}
        raise InvalidOperationException('pre_load is not possible with MemoryRepository')


class FileRepository(with_metaclass(SchemaMetaclass, Repository, FilterRepositoryMixin)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/FileRepository"

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
            self.logger.info("creating missing directory '%s'", fpath.parent)
            os.makedirs(str(fpath.parent))
        if fpath.exists():
            doc.load()
            if stream == doc.contentRaw:
                self.logger.info("File '%s' already exists with same content. Not overwriting.", fpath)
                return

        self.logger.info("DUMP file %s", fpath)
        self.logger.debug("data:\n%r ", stream)
        doc.write(stream)



@assert_arg(0, SCH_PATH_FILE)
def load_object_from_file(fp, handler_cls=None, session=None, **kwargs):
    session = session or scoped_session(session_maker())()
    handler_cls = handler_cls or JsonFileRepository
    handler = handler_cls(filepath=fp, **kwargs)
    session.bind_handler(handler)
    logger.info("LOAD %s from '%s'", handler.objectClass or '<unknown>', fp)
    handler.load()
    instances = handler.instances
    return instances if handler.many else instances[0]


@assert_arg(1, SCH_PATH)
def serialize_object_to_file(obj, fp, handler_cls=None, session=None, **kwargs):
    session = session or scoped_session(session_maker())()
    handler_cls = handler_cls or JsonFileRepository
    handler = handler_cls(filepath=fp, **kwargs)
    session.bind_handler(handler)
    logger.info("LOAD %s from '%s'", handler.objectClass, fp)
    handler.register(obj)
    handler.commit()


@repository_registry.register()
class JsonFileRepository(with_metaclass(SchemaMetaclass, FileRepository)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/JsonFileRepository"

    def __init__(self, **kwargs):
        FileRepository.__init__(self, **kwargs)

    def deserialize_data(self):
        data = self.document._deserialize(json.loads, **self._extended_properties)
        return data

    def serialize_data(self, data):
        return json.dumps(
            data,
            indent=self.get("indent", 2),
            ensure_ascii=self.get("ensure_ascii", False),
            separators=self.get("separators", None),
            default=self.get("default", None),
        )


@assert_arg(0, SCH_PATH_FILE)
def load_json_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp, handler_cls=JsonFileRepository, session=session, **kwargs)


@repository_registry.register()
class YamlFileRepository(with_metaclass(SchemaMetaclass, FileRepository)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/YamlFileRepository"
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


@assert_arg(0, SCH_PATH_FILE)
def load_yaml_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp, handler_cls=YamlFileRepository, session=session, **kwargs)


@repository_registry.register()
class XmlFileRepository(with_metaclass(SchemaMetaclass, FileRepository)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/XmlFileRepository"

    def __init__(self, tag=None, postprocessor=None, **kwargs):
        FileRepository.__init__(self, **kwargs)
        self._encoder = ProtocolJSONEncoder(no_defaults=self.no_defaults,
                                            remove_refs=self.remove_refs)
        self._tag = tag
        if not tag and self._class:
            self._tag = self._class.__name__

        # this default post processor makes all non attribute be list
        _prefix = str(self.attr_prefix)

        def default_postprocessor(path, key, value):
            return (key, value) if key.startswith(_prefix) or key.endswith('schema') else (key, to_list(value))

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


@assert_arg(0, SCH_PATH_FILE)
def load_xml_from_file(fp, session=None, **kwargs):
    return load_object_from_file(fp,
                                 handler_cls=XmlFileRepository,
                                 session=session,
                                 **kwargs)


@repository_registry.register()
class Jinja2FileRepository(with_metaclass(SchemaMetaclass, FileRepository)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/Jinja2FileRepository"

    def __init__(self, template=None, environment=None, context=None, protectedRegions=None, **kwargs):
        """
        Serializer based on a jinja template. Template is loaded from
        environment. If no environment is provided, use the default one
        `default_jinja2_env`
        """
        FileRepository.__init__(self, template=template, **kwargs)
        self._jinja = environment or default_jinja2_env()
        self._jinja.globals.update(_jinja2_globals)
        self._context = context or {}
        self._protected_regions = self._jinja.globals['protected_regions'] = protectedRegions or {}

    def pre_commit(self):
        return self._context

    def deserialize_data(self):
        raise Exception("not implemented")

    def serialize_data(self, data):
        self.logger.info("DUMP template '%s' file %s", self.template, self.document.filepath)
        self.logger.debug("data:\n%r ", data)

        stream = self._jinja.get_template(str(self.template)).render(data)
        return six.text_type(stream)


@repository_registry.register()
class Jinja2MacroFileRepository(with_metaclass(SchemaMetaclass, Jinja2FileRepository)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/Jinja2MacroFileRepository"

    def serialize_data(self, data):
        macro_args = self.macroArgs.for_json()
        if 'protected_regions' not in macro_args:
            macro_args.append('protected_regions')
        args = [k for k in macro_args if k in data]
        to_render = "{%% from '%s' import %s %%}{{%s(%s)}}" % (
            self.template, self.macroName, self.macroName, ', '.join(args))
        try:
            template = self._jinja.from_string(to_render)
            context = self._context.copy()
            context.update(**data)
            return template.render(context)
        except Exception as er:
            self.logger.error('SERIALIZE Jinja2MacroFileRepository: %s', er)
            raise er


@repository_registry.register()
class Jinja2MacroTemplatedPathFileRepository(with_metaclass(SchemaMetaclass, Jinja2MacroFileRepository)):
    __schema_uri__ = "http://numengo.org/ngoschema/repositories#/definitions/Jinja2MacroTemplatedPathFileRepository"

    def serialize_data(self, data):
        self.logger.info('SERIALIZE Jinja2MacroFileRepository')
        try:
            tpath = TemplatedString(self.templatedPath)(**self._context)
        except Exception as er:
            self.logger.error('SERIALIZE Jinja2MacroTemplatedPathFileRepository: %s', er)
        fpath = self.outputDir.joinpath(tpath)
        self.document = self.document or Document()
        self.document.filepath = fpath
        if not fpath.parent.exists():
            os.makedirs(str(fpath.parent))
        stream = Jinja2MacroFileRepository.serialize_data(self, data)
        if fpath.suffix in ['.h', '.c', '.cpp']:
            tf = tempfile.NamedTemporaryFile(mode='w+b', suffix=fpath.suffix, dir=fpath.parent, delete=False)
            tf.write(stream.encode('utf-8'))
            tf.close()
            stream = subprocess.check_output(
                'clang-format %s' % tf.name, cwd=str(self.outputDir), shell=True)
            stream = stream.decode('utf-8')
            os.remove(tf.name)
        return stream



# *- coding: utf-8 -*-
"""
Base class for loading objects from files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import six
import re
import operator

from future.utils import with_metaclass

from ngofile.list_files import list_files
from python_jsonschema_objects.util import safe_issubclass

from . import utils
from .resolver import get_resolver
from .classbuilder import ProtocolBase
from .classbuilder import get_builder
from .schema_metaclass import SchemaMetaclass
from .object_transform import ObjectTransform
from .deserializers import YamlDeserializer
from .deserializers import JsonDeserializer

_ = gettext.gettext


class ObjectLoader(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to load and translate models from files
    """

    schemaUri = "http://numengo.org/ngoschema/ObjectLoader"
    deserializers = [JsonDeserializer, YamlDeserializer]
    primaryKey = "name"

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)

        self._oc = utils.import_from_string(str(
            self.objectClass)) if self.objectClass else None

        self._deserializers = [
            utils.import_from_string(str(ds)) for ds in self.deserializers
        ] if self.deserializers else []

        self._transforms = {}
        self._objects = {}

    _pk = None
    @property
    def pk(self):
        if self._pk is None:
            self._pk = re.sub(r"[^a-zA-z0-9\-_]+", "", str(self.primaryKey))
        return self._pk

    def add_transformation(self, transfo):
        """
        Register an object transformation
        """
        transfo_ = transfo if hasattr(
            transfo, 'as_dict') else ObjectTransform(**transfo)
        if transfo_._from is None or transfo._to is None:
            raise ValueError(
                'transformation needs to have fully qualified from/to ' +
                'object classes')
        if issubclass(transfo_._from, self._oc):
            self._transforms[transfo_._to] = transfo_
        if issubclass(self._oc, transfo_._to):
            self._transforms[transfo_._from] = transfo_

    def _get_objects_from_data(self, data, object_class, many=False, **opts):
        """
        Returns a list of objects found in data
        Can be overrided by subclasses to add specific treatments
        """
        if 'schemaUri' in data and hasattr(object_class, 'schemaUri'):
            data_schema_uri = data['schemaUri']
            if data_schema_uri != object_class.schemaUri:
                builder = get_builder()
                if data_schema_uri in builder.resolved:
                    data_class = builder.resolved[data_schema_uri]
                    if not safe_issubclass(data_class, object_class):
                        return []
        return utils.process_collection(data, many=many, object_class=object_class, **opts)

    def load_from_file(self, fp, from_object_class=None, many=False, **opts):
        """
        Load objects from a file
        Call protected method _process_data

        :type fp: path
        :param many: process collection as a list/sequence. if collection is
        a dictionary and many=True, values are processed
        :param opts: options such as from_object_class
        """
        fp.resolve()

        # check if already loaded
        objs = [o for ref, o in self._objects.items() if ref.split('#')[0]==str(fp)]
        if objs:
            return objs if many else objs[0]
            
        parsers = self._deserializers
        for p in parsers:
            try:
                data = p().load(fp, **opts)
                break
            except Exception as er:
                pass
        else:
            raise IOError(
                "Impossible to load %s with parsers %s." % (fp, parsers))

        foc = from_object_class or self._oc
        try:
            obj = self._get_objects_from_data(data, foc, many=many, **opts)
            if not issubclass(self._oc, foc) and foc in self._transforms:
                tf = self._transforms[foc]
                obj = tf.transform(obj, object_class=self._oc, many=many, **opts)
        except Exception as er:
            raise IOError("Impossible to load %s from %s.\n%s" % (foc, fp, er))

        if obj:
            for o in (obj if many else [obj]):
                ref = "%s#%s" % (fp, o[self.pk])
                self._objects[ref] = o
        return obj

    def load_from_directory(self,
                            src,
                            includes=["*"],
                            excludes=[],
                            recursive=False,
                            from_object_class=None,
                            many=False,
                            **opts):
        """
        Load from a search in a directory
       
        :type src: path, isPathDir: True
        :param many: process collection as a list/sequence. if collection is
        a dictionary and many=True, values are processed
        """
        objs = []
        for fp in list_files(src, includes, excludes, recursive, folders=0):
            try:
                ret =  self.load_from_file(fp, from_object_class=from_object_class, many=many, **opts)
                objs += ret if many else [ret]
            except Exception as er:
                self.logger.warning(er)
        return objs

    def query(self, *attrs, **attrs_value):
        """
        Make a generator for a query in loaded objects

        :param attrs: retrieve objects with given attributes defined
        :param attrs_value: retrieve objects with given attribute/value pairs
        """
        def get_child(obj, key_list):
            if key_list[0] in obj:
                child = obj[key_list[0]]
                return child if len(key_list)==1 else get_child(child, key_list[1:])
            return None
        for obj in self:
            for k, v2 in attrs_value.items():
                op = 'eq'
                if '__' in k:
                    ks = k.split('__')
                    if ks[-1] in ['lt', 'le', 'eq', 'ne', 'ge', 'gt', 'in']:
                        op = ks[-1]
                        ks.pop()
                    o = get_child(obj, ks)
                else:
                    o = obj[k] if k in obj else None
                if o is None:
                    break
                v = o.for_json() if hasattr(o, "for_json") else o
                if op not in ['in'] and not getattr(operator, op)(v, v2):
                    break
                elif op == 'in' and not v in v2:
                    break
            else:
                for k in attrs:
                    if not hasattr(obj, k) or getattr(obj, k, None) is None:
                        break
                else:
                    yield obj

    def pick_first(self, **kwargs):
        """
        Pick first object corresponding to query
        """
        return next(self.query(**kwargs), None)

    @property
    def objects(self):
        """
        Return a list of all objects loaded
        """
        return self._objects.values()

    def __iter__(self):
        return six.itervalues(self._objects)

    def get(self, pk):
        """
        Return the first object with the corresponding primary key
        """
        return self.pick_first(**{self.pk: pk})
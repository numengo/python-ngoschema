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

from future.utils import with_metaclass

from ngofile.list_files import list_files

from . import utils
from .classbuilder import ProtocolBase
from .schema_metaclass import SchemaMetaclass
from .transforms import ObjectTransform
from .deserializers import YamlDeserializer
from .deserializers import JsonDeserializer

_ = gettext.gettext


class ObjectLoader(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to load and translate models from files
    """

    schemaUri = "http://numengo.org/ngoschema/object_loader"
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

    def _get_objects_from_data(self, data, objectClass, **opts):
        """
        Returns a list of objects found in data
        Can be overrided by subclasses to add specific treatments
        """
        obj = objectClass(**data)
        return [obj]

    def load_from_file(self, fp, **opts):
        """
        Load objects from a file
        Call protected method _process_data

        :type fp: path
        :param opts: options such as fromObjectClass
        """
        parsers = self._deserializers
        for p in parsers:
            try:
                data = p().load(fp, **opts)
                break
            except Exception as er:
                pass
        else:
            raise IOError(
                "Impossible to load %s with parsers %s.\n%s" % (fp, parsers))

        foc = opts.get('fromObjectClass') or self._oc
        try:
            if issubclass(self._oc, foc):
                objs = self._get_objects_from_data(data, self._oc, **opts)
            elif foc in self._transforms:
                tobjs = self._get_objects_from_data(data, foc)
                tf = self._transforms[foc]
                objs = [
                    tf.transform(tobj, objectClass=self._oc) for tobj in tobjs
                ]
        except Exception as er:
            raise IOError("Impossible to load %s from %s.\n%s" % (foc, fp, er))

        for obj in objs:
            ref = "%s#%s" % (fp, obj[str(self.primaryKey)])
            self._objects[ref] = obj
        return objs

    def load_from_directory(self,
                            src,
                            includes=["*"],
                            excludes=[],
                            recursive=False,
                            **opts):
        """
        Load from a search in a directory
       
        :type src: path
        """
        objs = []
        for fp in list_files(src, includes, excludes, recursive):
            try:
                objs += self.load_from_file(fp, **opts)
            except Exception as er:
                self.logger.warning(er)
        return objs

    def query(self, **kwargs):
        """
        Make a generator for a query in loaded objects
        """
        for path, obj in self._objects.items():
            for k in kwargs.keys():
                v = obj[k].for_json() if hasattr(obj[k],
                                                 "for_json") else obj[k]
                if v != kwargs[k]:
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
        return self.pick_first(**{str(self.primaryKey): pk})
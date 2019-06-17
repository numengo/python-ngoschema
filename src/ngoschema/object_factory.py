# *- coding: utf-8 -*-
"""
Base class for loading objects from files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import itertools
import pprint
from future.utils import with_metaclass

from python_jsonschema_objects.util import safe_issubclass

from . import document
from . import utils
from ngoschema import ProtocolBase
from .classbuilder import get_builder
from .decorators import SCH_PATH_DIR
from .decorators import SCH_PATH_FILE
from .decorators import assert_arg
from .deserializers import JsonDeserializer
from .deserializers import YamlDeserializer
from .object_transform import ObjectTransform
from .query import Query
from .schema_metaclass import SchemaMetaclass


class ObjectFactory(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to load and translate models from files
    """

    schemaUri = "http://numengo.org/draft-05/schema/object-factories#/definitions/ObjectFactory"
    deserializers = [JsonDeserializer, YamlDeserializer]

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)

        if self.objectClass:
            self._objectClass = utils.import_from_string(str(self.objectClass))

        self._deserializers = [
            utils.import_from_string(str(ds)) for ds in self.deserializers
        ] if self.deserializers else []

        self._lz = bool(self.lazy_loading)

        self._transforms = {}

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
        if issubclass(transfo_._from, self._objectClass):
            self._transforms[transfo_._to] = transfo_
        if issubclass(self._objectClass, transfo_._to):
            self._transforms[transfo_._from] = transfo_

    def process_object_data(self,
                            data,
                            from_object_class,
                            many=False,
                            process_opts=None,
                            transform_opts=None):
        """
        Process data and make necessary transformations.

        Can be overrided by subclasses to add specific treatments
        :param data: input dictionary of data
        :param from_object_class: object class corresponding to input data
        :param many: flag to indicate that data corresponds to a collection of several 
        objects, stored as a list or as a dictionary of objects with key the `primaryKey`
        :param process_opts: dictionary of options for `utils.process_object_data`
        :param transform_opts: dictionary of options for `object_transform.ObjectTransform.transform`
        """
        process_opts = process_opts or {}
        transform_opts = transform_opts or {}
        if 'schemaUri' in data and hasattr(from_object_class, '__schema__'):
            data_schema_uri = data['schemaUri']
            if data_schema_uri != from_object_class.__schema__.get('$id'):
                builder = get_builder()
                if data_schema_uri in builder.resolved:
                    data_class = builder.resolved[data_schema_uri]
                    if not safe_issubclass(data_class, from_object_class):
                        raise Exception(
                            'data does not correspond to object class %s' %
                            from_object_class)

        if not issubclass(
                self._objectClass,
                from_object_class) and from_object_class in self._transforms:
            tf = self._transforms[from_object_class]
            data = tf.transform(
                from_object_class(**data), many=many, **transform_opts)

        process_opts[
            'object_class'] = None  # to make sure object is not created here
        ret = utils.process_collection(data, many=many, **process_opts)
        return ret

    def create(self,
               data,
               from_object_class=None,
               many=False,
               process_opts=None,
               transform_opts=None):
        """
        Create an object from a dictionary of data

        :param data: input dictionary of data
        :param from_object_class: if data corresponds to a different object which will
        require a model transformation with the registered transformations
        :param many: flag to indicate that data corresponds to a collection of several 
        objects, stored as a list or as a dictionary of objects with key the `primaryKey`
        :param process_opts: dictionary of options for `utils.process_object_data`
        :param transform_opts: dictionary of options for `object_transform.ObjectTransform.transform`
        """
        process_opts = process_opts or {}
        transform_opts = transform_opts or {}
        foc = from_object_class or self._objectClass
        objs = []
        try:
            objs_data = self.process_object_data(
                data, foc, many=many, process_opts=process_opts)
            if objs_data:
                for data in (objs_data if many else [objs_data]):
                    objs.append(
                        self._objectClass(lazy_loading=self._lz, **data))
                return objs if many else objs[0]
        except Exception as er:
            raise IOError("Impossible to create %s from %s.\n%s" 
                % (foc, utils.coll_pprint(data), er))

    def create_from_document(self,
                             doc,
                             from_object_class=None,
                             many=False,
                             deserializers=[],
                             process_opts=None,
                             transform_opts=None):
        """
        Create an object from data contained in a document

        :param doc: `document.Document` to deserialize to get data
        :param from_object_class: if data corresponds to a different object which will
        require a model transformation with the registered transformations
        :param many: flag to indicate that data corresponds to a collection of several 
        objects, stored as a list or as a dictionary of objects with key the `primaryKey`
        :param deserializers: list of deserializers to try to use if `deserialize`=True
        :param process_opts: dictionary of options for `utils.process_object_data`
        :param transform_opts: dictionary of options for `object_transform.ObjectTransform.transform`
        """
        # check if already loaded
        data = doc.deserialize(deserializers or self._deserializers)
        return self.create(
            data,
            from_object_class=from_object_class,
            many=many,
            process_opts=process_opts,
            transform_opts=transform_opts)

    @assert_arg(1, SCH_PATH_FILE)
    def create_from_file(self,
                         fp,
                         from_object_class=None,
                         many=False,
                         deserializers=[],
                         process_opts=None,
                         transform_opts=None,
                         assert_args=True):
        __doc__ = self.create_from_document.__doc__
        doc = document.get_document_registry().register_from_file(fp)
        return self.create_from_document(
            doc,
            from_object_class=from_object_class,
            many=many,
            process_opts=process_opts,
            deserializers=deserializers,
            transform_opts=transform_opts)

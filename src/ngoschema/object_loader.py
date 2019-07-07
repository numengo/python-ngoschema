# *- coding: utf-8 -*-
"""
Base class for loading objects from files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import itertools
import weakref

from future.utils import with_metaclass
from python_jsonschema_objects.util import safe_issubclass

from . import utils
from ngoschema import ProtocolBase
from .query import Query
from .schema_metaclass import SchemaMetaclass
from .object_factory import ObjectFactory


_default_object_loader = None


def get_object_loader():
    """
    Return the default object loader
    """
    global _default_object_loader
    if _default_object_loader is None:
        _default_object_loader = ObjectLoader()
    return _default_object_loader


class ObjectLoader(with_metaclass(SchemaMetaclass, ObjectFactory)):
    """
    Class to load and translate models from files. Each document is only loaded
    once and if a document is loaded multiple times, the same instance is returned.
    """

    __schema__ = "http://numengo.org/draft-05/schema/object-factories#/definitions/ObjectLoader"
    #primaryKey = "name"

    def __init__(self, **kwargs):
        ObjectFactory.__init__(self, **kwargs)
        self._document_objects = {}
        self._objects = {}

    _pk = None

    @property
    def pk(self):
        if self._pk is None:
            self._pk = str(self.primaryKey)
        return self._pk

    def register(self, *objs):
        """
        Register objects in factory
        """
        self._objects.update({id(o): o for o in objs})

    def create(self,
               data,
               from_object_class=None,
               many=False,
               process_opts=None,
               transform_opts=None):
        ret = ObjectFactory.create(self, data, from_object_class=from_object_class, many=many,
            process_opts=process_opts, transform_opts=transform_opts)
        objs = ret if many else [ret] 
        self.register(*objs)
        return ret

    def create_from_document(self,
                             doc,
                             from_object_class=None,
                             many=False,
                             deserializers=[],
                             process_opts=None,
                             transform_opts=None):
        __doc__ = ObjectFactory.create_from_document.__doc__
        if doc.identifier not in self._document_objects:
            self._document_objects[
                doc.identifier] = ObjectFactory.create_from_document(
                    self,
                    doc,
                    from_object_class=from_object_class,
                    many=many,
                    process_opts=process_opts,
                    deserializers=deserializers,
                    transform_opts=transform_opts)
        return self._document_objects[doc.identifier]

    def first(self, cls=None, **kwargs):
        """
        Return the first object with the corresponding primary key
        """
        o = Query(self._objects.values()).get(**kwargs)
        if cls is None or isinstance(o, cls):
            return o

    def __contains__(self, query):
        if not utils.is_string(query):
            query = query[self.pk]
        return bool(Query(self._objects.values()).filter(**{self.pk: query}).count())

    def filter(self,
               *attrs,
               load_lazy=True,
               order_by=False,
               distinct=False,
               cls=None,
               **attrs_value):
        """
        Make a Query on managed objects
        """ + Query._filter_or_exclude.__doc__
        return Query(self._objects.values(), order_by=order_by, distinct=distinct).\
            filter(*attrs, load_lazy=load_lazy, **attrs_value)

    def exclude(self,
               *attrs,
               load_lazy=True,
               order_by=False,
               distinct=False,
               **attrs_value):
        """
        Make a Query on managed objects
        """ + Query._filter_or_exclude.__doc__
        return Query(self._objects.values(), order_by=order_by, distinct=distinct).\
            exclude(*attrs, load_lazy=load_lazy, **attrs_value)

    def filter_any_of(self,
               *attrs,
               load_lazy=True,
               order_by=False,
               distinct=False,
               **attrs_value):
        """
        Make a Query on managed objects
        """ + Query._filter_or_exclude.__doc__
        return Query(self._objects.values(), order_by=order_by, distinct=distinct).\
            filter_any_of(*attrs, load_lazy=load_lazy, **attrs_value)

    def exclude_any_of(self,
               *attrs,
               load_lazy=True,
               order_by=False,
               distinct=False,
               **attrs_value):
        """
        Make a Query on managed objects
        """ + Query._filter_or_exclude.__doc__
        return Query(self._objects.values(), order_by=order_by, distinct=distinct).\
            exclude_any_of(*attrs, load_lazy=load_lazy, **attrs_value)

    @property
    def objects(self):
        """
        Return a query set of all objects loaded
        """
        return Query(self._objects.values())
        #return Query([ref() for ref in map(lambda ref: ref(), self._objects.values())])

    def __iter__(self):
        return iter(self._objects.values())
        #return iter([ref() for ref in map(lambda ref: ref(), self._objects.values())])

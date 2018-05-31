# *- coding: utf-8 -*-
"""
Utilities and classes to deal with model transformations

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
from future.utils import with_metaclass

from ngofile.pathlist import list_in_modules

from . import utils
from . import str_utils
from ._schemas import ObjectManager
from ._classbuilder import ProtocolBase
from .json import Json

_ = gettext.gettext


class ObjectTransform(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to do simple model to model transformation
    """
    schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/ObjectTransform"

    def _set_from(self, value):
        self._properties['from'], self._from = utils.obj_or_str(value)

    def set_to(self, value):
        self._properties['to'], self._to = utils.obj_or_str(value)

    def transform_from(self, from_dict):
        to_dict = {}
        from_ = self._from.__name__.lower()
        to_ = self._to.__name__.lower()
        translation = {
            'this.%s' % k: 'this.%s' % v
            for k, v in self.fieldsEquivalence.items()
        }
        translation.update({
            '%s.%s' % (from_, k): 'this.%s' % v
            for k, v in self.fieldsEquivalence.items()
        })
        common = utils.gcs(self._from, self._to)
        for k, v in from_dict.items():
            if hasattr(common, k):
                to_dict[k] = v
            elif k in self.fieldsEquivalence:
                #if utils.is_expr(v):
                #    v = str_utils.multiple_replace(v, translation)
                to_dict[self.fieldsEquivalence[k]] = v
            elif k in self.complexTransformsTo:
                tf = self.complexTransformsTo[k]
                to_dict[k] = tf(from_dict)
            else:
                # no transformation
                pass
        return to_dict

    def transform_to(self, to_dict):
        from_dict = {}
        from_ = self._from.__name__.lower()
        to_ = self._to.__name__.lower()
        translation = {
            'this.%s' % v: 'this.%k' % v
            for k, v in self.fieldsEquivalence.items()
        }
        translation.update({
            '%s.%s' % (to_, v): 'this.%s' % k
            for k, v in self.fieldsEquivalence.items()
        })
        common = gcs(self._from, self._to)
        for k, v in list(from_dict.items()):
            if common and hasattr(common, '_schema') and k in common.keys():
                from_dict[k] = v
            elif k in self.fieldsEquivalence.values():
                #if utils.is_expr(v):
                #    v = str_utils.multiple_replace(v, translation)
                from_dict[self.fieldsEquivalence[k]] = v
            elif k in self.complexTransformsFrom:
                tf = self.complexTransformsFrom[k]
                from_dict[k] = tf(to_dict)
            else:
                # no transformation
                pass
        return from_dict


class ObjectTransformManager(ObjectManager):
    extensions = ['.mtm']
    parsers = [Json]

    def __init__(self, *args, **kwargs):
        ObjectManager.__init__(self, ObjectTransform, *args, **kwargs)
        self.pathlist = list_all_dirs_in_modules('transforms')
        if not self.loaded:
            self.update_from_files()

    '''
    def transforms_from(self, object_class, object_class2=None):

        object_class = validators.destringify(object_class)
        object_class2 = validators.destringify(object_class2)
        ret = [t for t in self.objects if issubclass(object_class, t.from_)]
        if object_class2:
            ret = [t for t in ret if issubclass(object_class2, t.to_)]
        return ret

    def transforms_to(self, object_class, object_class2=None):
        object_class = validators.destringify(object_class)
        object_class2 = validators.destringify(object_class2)
        ret = [t for t in self.objects if issubclass(object_class, t.from_)]
        if object_class2:
            ret = [t for t in ret if issubclass(object_class2, t.from_)]
        return ret

    def transform(self,
                  object_class1,
                  dict_object1,
                  object_class2,
                  create_object=True):
        """ Transforms an object of object_class1 1 to an object_class2

        Looks into the registry for a transform between 2 objects
        :param object_class1: class of object to transform from
        :type object_class1: ngomodel.validators.Class
        :param dict_object1: data of object
        :type dict_object1: ngomodel.validators.Dict
        :param object_class2: class of object to transform to
        :type object_class2: ngomodel.validators.Class
        :param create_object: create object or dictionary
        :rtype: ngomodel.validators.Instance
        """
        object_class1 = validators.destringify(object_class1)
        object_class2 = validators.destringify(object_class2)
        for t in self.transforms_from(object_class1, object_class2):
            try:
                d2 = t.transform_from(dict_object1)
                return object_class2(**d2) if create_object else d2
            except Exception as er:
                self.logger.exception(er)
        for t in self.transforms_to(object_class1, object_class2):
            try:
                d2 = t.transform_to(dict_object1)
                return object_class2(**d2) if create_object else d2
            except Exception as er:
                self.logger.exception(er)
        raise Exception(
            _('no transform found for object %r and %r' % (object_class1,
                                                           object_class2)))
    '''

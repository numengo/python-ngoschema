# *- coding: utf-8 -*-
"""
Utilities and classes to deal with model transformations

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from future.utils import with_metaclass

from . import jinja2
from . import utils
from ngoschema import ProtocolBase
from .schema_metaclass import SchemaMetaclass

# loader to register module with a transforms folder where to look for model transformations
transforms_module_loader = utils.GenericModuleFileLoader('transforms')


def _process_transform(string):
    if utils.is_pattern(string):
        return jinja2.TemplatedString(string)
    else:
        return utils.import_from_string(string)


class ObjectTransform(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to do simple model to model transformation
    """

    __schema__ = "http://numengo.org/draft-05/schema/object-transform"

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)
        try:
            self._from = utils.import_from_string(str(self['from']))
        except Exception as er:
            self._from = None
        try:
            self._to = utils.import_from_string(str(self['to']))
        except Exception as er:
            self._to = None

        complexTransformFrom = kwargs.get("complexTransformFrom", {})
        self._complexTransformFrom = {
            k: _process_transform(v)
            for k, v in complexTransformFrom.items()
        }

        complexTransformTo = kwargs.get("complexTransformTo", {})
        self._complexTransformTo = {
            k: _process_transform(v)
            for k, v in complexTransformTo.items()
        }

    def transform_from(self, from_, many=False, **opts):
        """
        Create a dict/object from another one using the translation dictionaries
        defined in ObjectTransform, applying the fieldsEquivalence translation
        table , and the complexTransformFrom translation dictionary

        :param from_: object/dict to transform
        :type from_: object
        :param opts: dictionary of options, object_class=None
        :rtype: object
        """
        if many:
            datas = list(from_) if utils.is_sequence(from_) else from_.values()
            return [self.transform_from(d, **opts) for d in datas]

        from_ = from_.as_dict() if hasattr(from_, "as_dict") else from_
        to_ = {}
        from_to = {v.for_json(): k for k, v in self.fieldsEquivalence.items()}
        for k, v in from_.items():
            if k in from_to:
                k2 = from_to[k]
                to_[k2] = v
        for k2, tf in self._complexTransformFrom.items():
            try:
                if isinstance(tf, jinja2.TemplatedString):
                    to_[k2] = tf({"to": to_, "from": from_})
                else:
                    to_[k2] = tf(**from_)
            except Exception:
                pass

        # converting types than can be easily converted by evaluation
        # for ex: convert a string containing a list to an actual list
        if self._to and hasattr(self._to, "as_dict"):
            for k, v in to_.items():
                try:
                    if self._to.__propinfo__[k]["type"] != "string":
                        to_[k] = eval(v)
                except Exception:
                    pass

            #if "object_class" not in opts:
            #    opts["object_class"] = self._to

        return utils.process_collection(to_, **opts)

    def transform_to(self, to_, many=False, **opts):
        """
        Create a dict/object from another one using the translation dictionaries
        defined in ObjectTransform, applying the fieldsEquivalence translation
        table (inverted), and the complexTransformTo translation dictionary

        :param from_: object/dict to transform
        :type from_: object
        :param opts: dictionary of options, object_class=None
        :rtype: object
        """
        if many:
            datas = list(to_) if utils.is_sequence(to_) else to_.values()
            return [self.transform_to(d, **opts) for d in datas]

        to_ = to_.as_dict() if hasattr(to_, "as_dict") else to_
        from_ = {}
        to_from = {k: v.for_json() for k, v in self.fieldsEquivalence.items()}
        for k, v in to_.items():
            if k in to_from:
                k2 = to_from[k]
                from_[k2] = v
        for k2, tf in self._complexTransformTo.items():
            try:
                if isinstance(tf, jinja2.TemplatedString):
                    from_[k2] = tf({"to": to_, "from": from_})
                else:
                    from_[k2] = tf(**to_)
            except Exception:
                pass

        # converting types than can be easily converted by evaluation
        if self._from and hasattr(self._from, "as_dict"):
            for k, v in from_.items():
                try:
                    if self._from.__propinfo__[k]["type"] != "string":
                        from_[k] = eval(v)
                except Exception:
                    pass

            #if "object_class" not in opts:
            #    opts["object_class"] = self._from

        return utils.process_collection(from_, **opts)

    def transform(self, from_, many=False, **opts):
        if hasattr(from_, "as_dict"):
            if isinstance(from_, self._from):
                return self.transform_from(from_, many, **opts)
            if isinstance(from_, self._to):
                return self.transform_to(from_, many, **opts)
        if 'object_class' in opts:
            oc = opts['object_class']
            if issubclass(oc, self._to):
                return self.transform_from(from_, many, **opts)
            if issubclass(oc, self._from):
                return self.transform_to(from_, many, **opts)
        raise ValueError('cannot determine which transformation to do.')

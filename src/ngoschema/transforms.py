# *- coding: utf-8 -*-
"""
Utilities and classes to deal with model transformations

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
from future.utils import with_metaclass

from . import utils
from . import jinja2
from ._schemas import SchemaMetaclass
from ._classbuilder import ProtocolBase

_ = gettext.gettext

def _process_transform(string):
    if utils.is_pattern(string):
        return jinja2.templatedString(string)
    else:
        return utils.import_from_string(string)

class ObjectTransform(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to do simple model to model transformation
    """
    schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/ObjectTransform"

    def set_complexTransformFrom(self, dictio):
        self._properties['complexTransformFrom'] = dictio
        self._complexTransformFrom = {k: _process_transform(v)
                                       for k, v in dictio.items() }

    def set_complexTransformTo(self, dictio):
        self._properties['complexTransformTo'] = dictio
        self._complexTransformTo = {k: _process_transform(v)
                                       for k, v in dictio.items() }

    def transform_from(self, from_, **opts):
        """
        Create a dict/object from another one using the translation dictionaries
        defined in ObjectTransform, applying the fieldsEquivalence translation
        table , and the complexTransformFrom translation dictionary

        :param from_: object/dict to transform
        :type from_: object
        :param opts: dictionary of options, objectClass=None
        :rtype: object
        """
        from_ = from_.as_dict() if hasattr(from_,'has_dict') else from_
        to_ = {}
        from_to = self.fieldsEquivalence
        for k, v in from_.items():
            if k in from_to:
                k2 = from_to[k]
                to_[k2] = v
        for k2, tf in self._complexTransformFrom.items():
            to_[k2] = tf(**from_)
        return utils.process_collection(to_, **opts)

    def transform_to(self, to_, **opts):
        """
        Create a dict/object from another one using the translation dictionaries
        defined in ObjectTransform, applying the fieldsEquivalence translation
        table (inverted), and the complexTransformTo translation dictionary

        :param from_: object/dict to transform
        :type from_: object
        :param opts: dictionary of options, objectClass=None
        :rtype: object
        """
        to_ = to_.as_dict() if hasattr(to_,'has_dict') else to_
        from_ = {}
        to_from = {v: k for k, v in self.fieldsEquivalence}
        for k, v in to_.items():
            if k in to_from:
                k2 = to_from[k]
                from_[k2] = v
        for k2, tf in self._complexTransformTo.items():
            from_[k2] = tf(**to_)
        return utils.process_collection(from_, **opts)

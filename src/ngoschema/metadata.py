# *- coding: utf-8 -*-
"""
Base class for metadata (inherited by all components normally)

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from future.utils import with_metaclass
from ngoschema.keyed_object import NamedObject

from .schema_metaclass import SchemaMetaclass


class Metadata(with_metaclass(SchemaMetaclass, NamedObject)):
    """
    Class to deal with metadata and parents/children relationships
    """
    __schema__ = "http://numengo.org/draft-05/schema#/definitions/Metadata"

    def __init__(self, *args, **kwargs):
        NamedObject.__init__(self, *args, **kwargs)

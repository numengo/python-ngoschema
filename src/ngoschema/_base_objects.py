# *- coding: utf-8 -*-
""" base objects defined in numengo core metaschema

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import collections
import gettext
import pathlib
from builtins import object
from builtins import str

import python_jsonschema_objects.util as pjo_util
from future.builtins import object
from future.utils import with_metaclass
from past.builtins import basestring

from ._schemas import SchemaMetaclass, SchemaBase

_ = gettext.gettext




#class File(with_metaclass(SchemaMetaclass, object)):

class File(SchemaBase):
    schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/File"

    def __init__(self, path=".", **kw):
        SchemaBase.__init__(self,**kw)



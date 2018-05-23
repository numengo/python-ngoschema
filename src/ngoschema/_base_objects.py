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

import import
import python_jsonschema_objects.util as pjo_util
from future.builtins import object
from future.utils import with_metaclass
from past.builtins import basestring


from python_jsonschema_objects.classbuilder import ProtocolBase


_ = gettext.gettext




class Path(with_metaclass(SchemaMetaclass, object)):
    schemaUri = "http://numengo.org/draft-03/schema#/definitions/Path"

    def __init__(self, path=".", **kw):
        return pathlib.Path(path, kw)


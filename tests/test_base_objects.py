# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import pathlib
import jsonschema
import logging
import os
import gettext
import pytest

from future.utils import with_metaclass
from future.builtins import object
from builtins import str

from python_jsonschema_objects.literals import LiteralValue
from ngoschema._classbuilder import ProtocolBase, ClassBuilder, make_property
from ngoschema._schemas import SchemaMetaclass, SchemaBase

_ = gettext.gettext


class File(SchemaBase):
    schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/File"

    def __init__(self, path=".", **kw):
        SchemaBase.__init__(self,**kw)


def test_file():
    f = File(name="filename")
    print(f.as_dict())

if __name__ == '__main__':
    test_file()

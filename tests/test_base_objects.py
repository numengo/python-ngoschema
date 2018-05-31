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

import python_jsonschema_objects as pjo
from python_jsonschema_objects.literals import LiteralValue
from ngoschema._classbuilder import ProtocolBase, ClassBuilder, make_property
from ngoschema._schemas import SchemaMetaclass, SchemaBase, ObjectManager

_ = gettext.gettext

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('python_jsonschema_objects.classbuilder').setLevel(logging.INFO)

def test_file():
    #class File(SchemaBase):
    class File(with_metaclass(SchemaMetaclass, SchemaBase)):
        schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/File"

        def __init__(self, path=".", **kw):
            SchemaBase.__init__(self,**kw)

        def foo(self,i=1):
            """
            Test parameter validity check

            :param i: an integer
            :type i: int
            """
            return i+1

    class FileManager(with_metaclass(SchemaMetaclass, ObjectManager)):
        objectClass = File

    f = File(name="filename")
    print(f.as_dict())
    #with pytest.raises(pjo.ValidationError):
    #    f.foo("string")
    fm = FileManager()
    pass

if __name__ == '__main__':
    test_file() 

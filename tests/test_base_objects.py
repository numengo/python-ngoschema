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
from ngoschema._schemas import SchemaMetaclass, SchemaBase

_ = gettext.gettext

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('python_jsonschema_objects.classbuilder').setLevel(logging.INFO)

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


def test_file():
    f = File(name="filename")
    with pytest.raises(pjo.ValidationError):
        f.foo("string")
    print(f.as_dict())

if __name__ == '__main__':
    test_file()

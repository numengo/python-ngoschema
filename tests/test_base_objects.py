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
from ngoschema._schemas import SchemaMetaclass

_ = gettext.gettext


#class Path(with_metaclass(SchemaMetaclass, ProtocolBase, pathlib.Path)):

class Path(with_metaclass(SchemaMetaclass, LiteralValue, pathlib.Path)):
    schemaUri = "http://numengo.org/draft-03/schema#/definitions/Path"
    _flavour = pathlib._windows_flavour if os.name == 'nt' else pathlib._posix_flavour

    def validate(self):
        return True

    #def __init__(self, path=".", **kw):
    #    self._path = pathlib.Path(path)
    def __str__(self):
        return pathlib.Path.__str__(self)

    def isDir(self):
        return self.is_dir()

    def isFilepath(self):
        return self.exists() and not self.is_dir()

    def isExisting(self):
        return self.exists()

def test_path():
    #from ngoschema._base_objects import Path
    p = Path(r'D:\CODES\python-jsonschema-objects\python_jsonschema_objects')
    p2 = pathlib.Path(r'D:\CODES\python-jsonschema-objects\python_jsonschema_objects')
    print p.isDir()
    print p.isFilepath()
    print p.isExisting()
    print (p.as_dict())
    print (isinstance(p,pathlib.Path))
    print ('%s'%p)
    print ('%r'%p)

if __name__ == '__main__':
    test_path()

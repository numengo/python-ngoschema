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
from pprint import pprint

from future.utils import with_metaclass
from future.builtins import object
from builtins import str

from ngoschema._classbuilder import ProtocolBase
from ngoschema.schema_metaclass import SchemaMetaclass
from ngoschema.deserializers import YamlDeserializer
from ngoschema.deserializers import JsonDeserializer

_ = gettext.gettext

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('python_jsonschema_objects.classbuilder').setLevel(logging.INFO)

dirpath = os.path.dirname(os.path.realpath(__file__))

def test_transform():
    from ngoschema.transforms import ObjectTransform
    from ngoschema._base_objects import Project

    class Cookiecutter(with_metaclass(SchemaMetaclass, ProtocolBase)):
        schemaPath = os.path.join(dirpath,'schemas','cookiecutter.json')

    js = pathlib.Path(dirpath,'objects','cc_ngoschema.json')
    cc_js = JsonDeserializer().load(js, objectClass=Cookiecutter)

    mtm_fp = pathlib.Path(dirpath,'transforms','cookiecutter2project.mtm')
    mtm = JsonDeserializer().load(mtm_fp, objectClass=ObjectTransform)

    proj = mtm.transform_from(cc_js, objectClass=Project)
    # field equivalence transform
    assert proj.authorEmail == cc_js.email
    # complex transform with jinja template
    assert len(proj.keywords) == len(cc_js.keywords.for_json().split(','))
    # missing complex transform with external function


if __name__ == '__main__':
    test_transform() 

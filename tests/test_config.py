# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import pathlib
import jsonschema
import logging
import os.path
import gettext
import pytest
from pprint import pprint

from future.utils import with_metaclass
from future.builtins import object
from builtins import str

from ngoschema.config import ConfigLoader
from ngoschema.schema_metaclass import SchemaMetaclass
from ngoschema.deserializers import YamlDeserializer
from ngoschema.deserializers import JsonDeserializer
from ngoschema._for_test_only import Project

_ = gettext.gettext

import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("python_jsonschema_objects.classbuilder").setLevel(logging.INFO)

dirpath = os.path.dirname(os.path.realpath(__file__))


def test_config():

    cfgfile = os.path.join(dirpath, "objects", "config.ini")

    cm = ConfigLoader(singleton=True)
    cm.add_config(cfgfile)

    assert cm.section("Section:subsection")["OnlyInSection"] == "yes"
    assert cm.section("Section:subsection")["InSubsection"] == "yes"

    prj = Project()
    assert prj.authorName == "John Doe"


if __name__ == "__main__":
    test_config()

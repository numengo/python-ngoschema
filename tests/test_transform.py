# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import logging
import os
import pathlib

from future.utils import with_metaclass

from ngoschema.classbuilder import ProtocolBase
from ngoschema.deserializers import JsonDeserializer
from ngoschema.schema_metaclass import SchemaMetaclass

_ = gettext.gettext

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("python_jsonschema_objects.classbuilder").setLevel(
    logging.INFO)

dirpath = os.path.dirname(os.path.realpath(__file__))


def test_transform():
    from ngoschema.object_transform import ObjectTransform

    class Cookiecutter(with_metaclass(SchemaMetaclass, ProtocolBase)):
        schemaPath = os.path.join(dirpath, "schemas", "cookiecutter.json")

    class Project(with_metaclass(SchemaMetaclass, ProtocolBase)):
        schemaPath = os.path.join(dirpath, "schemas", "project.json")

    js = pathlib.Path(dirpath, "objects", "cc_ngoschema.json")
    cc_js = JsonDeserializer().load(js, objectClass=Cookiecutter)

    mtm_fp = pathlib.Path(dirpath, "transforms", "cookiecutter2project.mtm")
    mtm = JsonDeserializer().load(mtm_fp, objectClass=ObjectTransform)

    proj = mtm.transform_from(cc_js, objectClass=Project)
    # field equivalence transform
    assert proj.authorEmail == cc_js.email


if __name__ == "__main__":
    test_transform()

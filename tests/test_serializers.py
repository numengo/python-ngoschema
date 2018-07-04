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
from ngoschema.deserializers import YamlDeserializer
from ngoschema.schema_metaclass import SchemaMetaclass
from ngoschema.serializers import JsonSerializer
from ngoschema.serializers import YamlSerializer

_ = gettext.gettext

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("python_jsonschema_objects.classbuilder").setLevel(
    logging.INFO)

dirpath = os.path.dirname(os.path.realpath(__file__))


class Cookiecutter(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaPath = os.path.join(dirpath, "schemas", "cookiecutter.json")


def test_json2yaml():

    # json -> yaml
    js = pathlib.Path(dirpath, "objects", "cc_ngoschema.json")
    cc_js = JsonDeserializer.load(js, object_class=Cookiecutter)

    yml = js.with_name("cc_ngoschema_serialized.yaml")
    YamlSerializer().dump(
        {
            "default_context": cc_js.as_dict()
        }, yml, overwrite=True)
    cc_yml = YamlDeserializer.load(yml)
    cc_yml = cc_yml["default_context"]
    cc_yml = Cookiecutter(**cc_yml)
    assert cc_yml == cc_js


def test_yaml2json():
    # json -> yaml
    yml = pathlib.Path(dirpath, "objects", "cc_ngoschema.yaml")
    cc_yml = YamlDeserializer.load(yml)
    cc_yml = cc_yml["default_context"]
    cc_yml = Cookiecutter(**cc_yml)

    js = yml.with_name("cc_ngoschema_serialized.json")
    JsonSerializer().dump(cc_yml, js, overwrite=True)
    cc_js = JsonDeserializer.load(js, object_class=Cookiecutter)
    assert cc_yml == cc_js


if __name__ == "__main__":
    test_json2yaml()
    test_yaml2json()

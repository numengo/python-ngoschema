# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os.path

from ngoschema.classbuilder import objects_config_loader
from ngoschema.config import ConfigLoader
from ngoschema.object_factories import ObjectLoader

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("python_jsonschema_objects.classbuilder").setLevel(
    logging.INFO)

dirpath = os.path.dirname(os.path.realpath(__file__))
cfgfile = os.path.join(dirpath, "objects", "config.ini")


def test_config():
    cm = ConfigLoader()
    cm.add_config(cfgfile)
    assert cm.section("Section:subsection")["OnlyInSection"] == "yes"
    assert cm.section("Section:subsection")["InSubsection"] == "yes"


def test_object_config_loader():
    objects_config_loader.add_config(cfgfile)
    prj = ObjectLoader()
    prj.set_configfiles_defaults()
    assert prj.primaryKey == "NotTheDefaultOne"


if __name__ == "__main__":
    test_config()
    test_object_config_loader()

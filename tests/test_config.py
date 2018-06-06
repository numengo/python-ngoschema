# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import logging
import os.path

from ngoschema._for_test_only import Project
from ngoschema.config import ConfigLoader

_ = gettext.gettext

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("python_jsonschema_objects.classbuilder").setLevel(
    logging.INFO)

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

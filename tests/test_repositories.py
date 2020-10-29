# -*- coding: utf-8 -*-
"""
Unit tests for utilities

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import print_function
from __future__ import unicode_literals

import logging
logging.basicConfig(level=logging.INFO)

from ngoschema.repositories import JsonFileRepository, YamlFileRepository
from ngoschema.models.documents import Document
#from ngomf.component import ComponentDefinition
from ngoci.models.project import Project

def test_json_handler():
    d1 = Document(filepath="/Users/cedric/Devel/python/python-ngomf/ngomf/models/Ngo/MoistAir/PhaseChange/MACND00.json")
    h1  = JsonFileRepository(instanceClass='ngosim.models.component.ComponentDefinition', document=d1)
    c1 = h1.load()

    d2 = Document(filepath="/Users/cedric/Devel/python/python-ngoci/tests/fixtures/projects.ngoprj")
    h2  = YamlFileRepository(instanceClass=Project, document=d2, many=True)
    c2s = h2.load()
    print(len(c2s))

if __name__ == "__main__":
    test_json_handler()

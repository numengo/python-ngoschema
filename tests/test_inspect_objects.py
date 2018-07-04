# -*- coding: utf-8 -*-
""" Unit tests for inspection utilities

test_inspect.py - created on 22/05/2018
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  """

from __future__ import print_function
from __future__ import unicode_literals

from ngoschema.deserializers import Deserializer
from ngoschema.inspect_objects import ClassInspector
from ngoschema.inspect_objects import FunctionInspector
from ngoschema.schemas_loader import load_module_schemas


def test_FunctionInspector():
    fi = FunctionInspector(load_module_schemas)
    assert fi.parameters[0].name == "module"
    assert fi.parameters[1].name == "schemas_store"
    assert fi.parameters[0].doc
    assert fi.returns
    assert len(fi.parameters) == 2
    assert not fi.keywords
    assert not fi.varargs
    assert not fi.decorators


def test_ClassInspector():
    ci = ClassInspector(Deserializer)
    assert ci.methods["load"].shortDescription
    assert ci.methods["load"].parameters[0].name == "path"
    assert not ci.methods["load"].parameters[0].default
    assert ci.methods["load"].parameters[0].doc
    assert ci.methods["load"].keywords == 'opts'


if __name__ == "__main__":
    test_FunctionInspector()
    test_ClassInspector()

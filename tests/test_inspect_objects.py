# -*- coding: utf-8 -*-
""" Unit tests for inspection utilities

test_inspect.py - created on 22/05/2018
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  """

from __future__ import print_function
from __future__ import unicode_literals

from ngoschema import load_module_schemas


def test_FunctionInspector():
    from ngoinsp.inspectors.inspect_objects import FunctionInspector
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
    from ngoinsp.inspectors.inspect_objects import ClassInspector
    from ngoschema import ProtocolBase

    ci = ClassInspector(ProtocolBase)
    assert ci.methods["set_configfiles_defaults"].shortDescription
    assert ci.methods["set_configfiles_defaults"].parameters[0].name == "overwrite"
    assert not ci.methods["set_configfiles_defaults"].parameters[0].default
    assert ci.methods["set_configfiles_defaults"].parameters[0].doc


if __name__ == "__main__":
    test_FunctionInspector()
    test_ClassInspector()

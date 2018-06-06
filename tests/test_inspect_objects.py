# -*- coding: utf-8 -*-
""" Unit tests for inspection utilities

test_inspect.py - created on 22/05/2018
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  """

from __future__ import print_function
from __future__ import unicode_literals

from ngofile import LoadedModules
from ngofile import list_files

from ngoschema.inspect_objects import ClassInspector
from ngoschema.inspect_objects import FunctionInspector


def test_FunctionInspector():
    fi = FunctionInspector(list_files)
    assert fi.parameters[0].name == "src"
    assert fi.parameters[1].name == "includes"
    assert not fi.parameters[3].default
    assert fi.parameters[3].doc
    assert fi.parameters[3].name == "recursive"
    assert fi.returns
    assert len(fi.parameters) == 7
    assert not fi.keywords
    assert not fi.varargs
    assert not fi.decorators


def test_ClassInspector():
    ci = ClassInspector(LoadedModules)
    assert ci.methodsAll["exists"].parameters[0]
    assert ci.methods["list_files"].shortDescription
    assert ci.methods["list_files"].parameters[2].name == "recursive"
    assert not ci.methods["list_files"].parameters[2].default
    assert ci.methods["list_files"].parameters[2].doc is None
    assert ci.mro[0].methods["list_files"].parameters[2].doc


if __name__ == "__main__":
    test_FunctionInspector()
    test_ClassInspector()
    print("")

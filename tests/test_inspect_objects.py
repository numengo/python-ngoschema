# -*- coding: utf-8 -*-
""" Unit tests for inspection utilities

test_inspect.py - created on 22/05/2018
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  """

from __future__ import print_function
from __future__ import unicode_literals

from builtins import object
from builtins import str

import pytest
from ngofile import list_files, LoadedModules

from ngoschema.inspect_objects import FunctionInspector, ClassInspector
from ngoschema.doc_rest_parser import parse_docstring


def test_doc_parsing():
    
    ds = """
        Create a new file with a given template

        This is a long description of the function.
    
        :param filetype: type of file
        :type filetype: type1, type2, type3
        :param name: name of the file
        :type name: string

        :rtype: bool
        """
    doc = parse_docstring(ds)
    assert doc['params']['filetype']['doc'] == 'type of file'
    assert doc['params']['filetype']['type'] == 'type1, type2, type3'
    assert len(doc['params'])==2
    assert doc['returns'] == 'bool'


def test_FunctionInspector():
    fi = FunctionInspector(list_files)
    assert fi.parameters[0].name == 'src'
    assert fi.parameters[1].name == 'includes'
    assert fi.parameters[3].default == False
    assert fi.parameters[3].doc
    assert fi.parameters[3].name == 'recursive'
    assert fi.returns
    assert len(fi.parameters) == 7
    assert not fi.keywords
    assert not fi.varargs
    assert not fi.decorators


def test_ClassInspector():
    ci = ClassInspector(LoadedModules)
    assert ci.methodsAll['exists'].parameters[0]
    assert ci.methods['list_files'].shortDescription
    assert ci.methods['list_files'].parameters[2].name == 'recursive'
    assert ci.methods['list_files'].parameters[2].default == False
    assert ci.methods['list_files'].parameters[2].doc == None
    assert ci.mro[0].methods['list_files'].parameters[2].doc

if __name__ == "__main__":
    test_doc_parsing()
    test_FunctionInspector()
    test_ClassInspector()
    print("")

# -*- coding: utf-8 -*-
""" Unit tests for inspection utilities

test_inspect.py - created on 22/05/2018
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  """

from __future__ import print_function
from __future__ import unicode_literals


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
    from ngoinsp.inspectors.doc_rest_parser import parse_docstring
    doc = parse_docstring(ds)
    assert doc["params"]["filetype"]["doc"] == "type of file"
    assert doc["params"]["filetype"]["type"] == "type1, type2, type3"
    assert len(doc["params"]) == 2
    assert doc["returns"] == "bool"


def test_type_parsing():
    from ngoinsp.inspectors.doc_rest_parser import parse_type_string as pts
    t1 = pts("str")
    assert t1["type"] == "string"

    t2 = pts("[str,int]")
    assert t2["type"] == ["string", "integer"]

    t3 = pts("array, items:{type:str,format:regex}")
    assert t3["type"] == "array"
    assert t3["items"]["type"] == "string"
    assert t3["items"]["format"] == "regex"

    # replace = with :
    t4 = pts("dict, items={type=str}")
    assert t4["type"] == "object"
    assert t4["items"]["type"] == "string"

    t5 = pts("enum:[A,B,C]")
    assert t5["enum"] == ["A", "B", "C"]


if __name__ == "__main__":
    test_doc_parsing()
    test_type_parsing()

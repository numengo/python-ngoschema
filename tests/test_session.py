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

import collections
import pathlib
from builtins import str

import pytest
import six
from future.utils import text_to_native_str


from ngoschema import str_utils
from ngoschema import utils
from ngoschema.exceptions import InvalidValue


def test_resolve_import():
    function = utils.import_from_string("os.path.dirname")
    module = utils.import_from_string("past.builtins")
    klass = utils.import_from_string("decimal.Decimal")
    assert utils.fullname(klass) == "decimal.Decimal"
    with pytest.raises(InvalidValue) as e_info:
        utils.import_from_string("not.an.importable")

    method = utils.import_from_string(
        "jsonschema.validators.RefResolver.resolve")
    assert utils.fullname(
        method) == "jsonschema.validators.RefResolver.resolve"
    # tested on temporary file containing a nested class, import and fullname were working
    # nested_class = utils.import_from_string('ngoschema.example_nested_class.Human.Head')
    # assert utils.fullname(nested_class) == 'ngoschema.example_nested_class.Human.Head'


def test_utils():
    assert utils.is_sequence([1, 2])
    assert utils.is_sequence((1, 2))
    assert utils.is_sequence(collections.deque([1, 2]))
    assert not utils.is_sequence(set([1, 2]))

    assert utils.is_mapping({"a": 1})
    assert utils.is_mapping(collections.OrderedDict(a=1))
    assert not utils.is_mapping(1)
    assert not utils.is_mapping("a")

    assert utils.is_collection([1, 2])
    assert utils.is_collection(set([1, 2]))
    assert utils.is_collection((1, 2))
    assert utils.is_collection(collections.deque([1, 2]))
    assert utils.is_collection({"a": 1})
    assert utils.is_collection(collections.OrderedDict(a=1))
    assert not utils.is_collection(1)
    assert not utils.is_collection("a")

    newstring = str("foo")
    basestring_ = text_to_native_str("foo")
    unicodestr = str("foo")
    path = pathlib.Path("a/dummy/path")

    assert utils.is_basestring(basestring_) == six.PY2
    assert not utils.is_basestring(unicodestr)
    assert not utils.is_basestring(newstring)
    assert not utils.is_basestring(path)

    assert utils.is_string(basestring_)
    assert utils.is_string(unicodestr)
    assert utils.is_string(newstring)
    assert not utils.is_string(path)

    assert utils.is_pattern("{{ typical pattern }}")
    assert not utils.is_pattern("not a pattern")

    assert utils.is_expr("`a+b")
    assert not utils.is_expr("{{ typical pattern }}")


def test_string_utils():
    assert (str_utils.multiple_replace("boa kills, is it a boa", {
        "boa": "python",
        "kills": "rocks"
    }) == "python rocks, is it a python")

    assert str_utils.split_string("one,two|three",
                                  ",|") == ["one", "two", "three"]

def test_jinja_tokens():
    from ngoschema.jinja2 import get_variables
    vars = get_variables("{{ this.type }}-{{ this.name|lower|replace(' ','-') }}")
    print(vars)

if __name__ == "__main__":
    test_jinja_tokens()
    #break
    #test_resolve_import()
    #test_utils()
    #test_string_utils()

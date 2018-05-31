# -*- coding: utf-8 -*-
"""
Unit tests for utilities

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
created on 2017/11/15 08:44:32
"""
from __future__ import print_function
from __future__ import unicode_literals

from builtins import object
from builtins import str

from future.utils import text_to_native_str
from past.builtins import basestring

import six
import pytest
import pathlib
import collections

from ngoschema import utils
from ngoschema import str_utils
from ngoschema.exceptions import InvalidValue

def test_resolve_import():
    function = utils.import_from_string('os.path.dirname')
    module = utils.import_from_string('past.builtins')
    klass = utils.import_from_string('decimal.Decimal')
    assert utils.fullname(klass) == 'decimal.Decimal'
    with pytest.raises(InvalidValue) as e_info:
        utils.import_from_string('not.an.importable')

    method = utils.import_from_string('jsonschema.validators.RefResolver.resolve')
    assert utils.fullname(method) == 'jsonschema.validators.RefResolver.resolve'
    # tested on temporary file containing a nested class, import and fullname were working
    #nested_class = utils.import_from_string('ngoschema.example_nested_class.Human.Head')
    #assert utils.fullname(nested_class) == 'ngoschema.example_nested_class.Human.Head'


def test_utils():
    assert utils.is_sequence([1,2])
    assert utils.is_sequence((1,2))
    assert utils.is_sequence(collections.deque([1, 2]))
    assert utils.is_sequence(set([1,2]))==False

    assert utils.is_mapping({'a':1})
    assert utils.is_mapping(collections.OrderedDict(a=1))
    assert utils.is_mapping(1)==False
    assert utils.is_mapping('a')==False

    assert utils.is_collection([1,2])
    assert utils.is_collection(set([1,2]))
    assert utils.is_collection((1,2))
    assert utils.is_collection(collections.deque([1, 2]))
    assert utils.is_collection({'a':1})
    assert utils.is_collection(collections.OrderedDict(a=1))
    assert utils.is_collection(1)==False
    assert utils.is_collection('a')==False

    newstring = str('foo')
    basestring = text_to_native_str('foo')
    unicodestr = str('foo')
    path = pathlib.Path('a/dummy/path')

    assert utils.is_basestring([basestring, unicodestr, newstring,
                   path]) == [six.PY2, False, False, False]
    assert utils.is_string([basestring, unicodestr, newstring,
               path]) == [True, True, True, False]

    assert utils.is_pattern('{{ typical pattern }}')
    assert utils.is_pattern('not a pattern') == False

    assert utils.is_expr('`a+b')
    assert utils.is_expr('{{ typical pattern }}') == False


def test_string_utils():
    assert str_utils.multiple_replace('boa kills, is it a boa',
          {'boa':'python','kills':'rocks'}) == 'python rocks, is it a python'

    assert str_utils.split_string('one,two|three',',|')==['one','two','three'] 


if __name__ == "__main__":
    test_resolve_import()
    test_utils()
    test_string_utils()

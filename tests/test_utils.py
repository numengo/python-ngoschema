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

import pytest
import pathlib
import collections

from ngoschema import _utils
from ngoschema import _string_utils
from ngoschema.exceptions import InvalidValue


def test_utils():
    function = _utils.import_from_string('os.path.dirname')
    module = _utils.import_from_string('past.builtins')
    klass = _utils.import_from_string('decimal.Decimal')
    with pytest.raises(InvalidValue) as e_info:
        _utils.import_from_string('not.an.importable')

    assert _utils.is_sequence([1,2])
    assert _utils.is_sequence((1,2))
    assert _utils.is_sequence(collections.deque([1, 2]))
    assert _utils.is_sequence(set([1,2]))==False

    assert _utils.is_mapping({'a':1})
    assert _utils.is_mapping(collections.OrderedDict(a=1))
    assert _utils.is_mapping(1)==False
    assert _utils.is_mapping('a')==False

    assert _utils.is_collection([1,2])
    assert _utils.is_collection(set([1,2]))
    assert _utils.is_collection((1,2))
    assert _utils.is_collection(collections.deque([1, 2]))
    assert _utils.is_collection({'a':1})
    assert _utils.is_collection(collections.OrderedDict(a=1))
    assert _utils.is_collection(1)==False
    assert _utils.is_collection('a')==False

def test_string_utils():
    assert _string_utils.multiple_replace('boa kills, is it a boa',
          {'boa':'python','kills':'rocks'}) == 'python rocks, is it a python'

    assert _string_utils.split_string('one,two|three',',|')==['one','two','three'] 

def test_string_identifiers():
    assert _string_utils.str_is_int(' 10 ')
    assert _string_utils.str_is_int(' -10 ')
    assert _string_utils.str_is_int(' -10.0 ')==False
    assert _string_utils.str_is_int('not an int')==False

    assert _string_utils.str_is_bool('true')
    assert _string_utils.str_is_bool('True')
    assert _string_utils.str_is_bool('false')
    assert _string_utils.str_is_bool('FALSE')
    assert _string_utils.str_is_bool('not a bool')==False

    assert _string_utils.str_is_float(' 10 ')
    assert _string_utils.str_is_float(' -10 ')
    assert _string_utils.str_is_float(' -10.0 ')
    assert _string_utils.str_is_float('not a float')==False

    assert _string_utils.str_is_path(r'C:\dummmy\path')
    assert _string_utils.str_is_path('dummmy/path')
    assert _string_utils.str_is_path('dummmy/path/with/file.name')
    assert _string_utils.str_is_path('dummmy/path/with/a space/file.name')

    assert _string_utils.str_is_filename('file.name')
    assert _string_utils.str_is_filename('file.na.me')
    assert _string_utils.str_is_filename('.hidden')
    assert _string_utils.str_is_filename('dummmy/path/with/a space/file.name')==False

    assert _string_utils.str_looks_like_importable('module')
    assert _string_utils.str_looks_like_importable('module.submodule')
    assert _string_utils.str_looks_like_importable('module.sub module') == False

def test_string_testers():
    newstring = str('foo')
    basestring = text_to_native_str('foo')
    unicodestr = str('foo')
    path = pathlib.Path('a/dummy/path')

    assert _string_utils.is_basestring([basestring, unicodestr, newstring,
                          path]) == [True, False, False, False]
    assert _string_utils.is_string([basestring, unicodestr, newstring,
                      path]) == [True, True, True, False]

    assert _string_utils.is_pattern('{{ typical pattern }}')
    assert _string_utils.is_pattern('not a pattern') == False

    assert _string_utils.is_expr('`a+b')
    assert _string_utils.is_expr('{{ typical pattern }}') == False

if __name__ == "__main__":
    test_utils()
    test_string_utils()
    test_string_identifiers()
    test_string_testers()

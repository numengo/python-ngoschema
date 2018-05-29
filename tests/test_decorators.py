# -*- coding: utf-8 -*-
""" Unit tests for decorators of NgoProject

test_decorators.py - created on 2017/11/15 08:44:32
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  """
from __future__ import unicode_literals

import logging
from builtins import object
from builtins import str

import pytest

from ngoschema.decorators import *
from ngoschema.exceptions import *
from ngoschema.validators import *
from python_jsonschema_objects.validators import ValidationError


@take_arrays()
def time2(d):
    """multiply by 2"""
    return 2 * d


@take_arrays(0, 1)
def add(a, b):
    """add 2 components
    :param a: 1st
    :param b: 2nd
    """
    return a + b


def test_decorators():
    assert time2(1) == 2
    assert time2([1, 2]) == [2, 4]
    assert add(1, 2) == 3
    assert add([1, 2], [2, 3]) == [3, 5]
    assert add([1, 2], 3) == [4, 5]
    with pytest.raises(Exception):
        add(3, [1, 2])
    with pytest.raises(InvalidValue):
        add([1, 2], [1, 2, 3])

    print(help(time2))
    print(help(add))


    class MyException(Exception):
        pass

    class A(object):
        logger = logging.getLogger('TEST')

        @log_init
        def __init__(self):
            pass

        def __repr__(self):  # similar to the one in ClassWithSchema
            ret = '<%s' % self.__class__.__name__
            return ret + '>'

        def __str__(self):
            return self.__repr__()

        @log_exceptions
        def raise_exc(self):
            raise MyException('YO')

        @log_exceptions
        @assert_arg(1, SCH_INT)
        def foo(self, integer):
            return 1 + integer

        @log_exceptions
        @assert_arg(1, SCH_INT)
        def bar(self, integer=1):
            return 1 + integer

        @log_exceptions
        @assert_arg('integer', SCH_INT)
        def bar2(self, integer=1):
            """
            Test docstring
            """
            return 1 + integer

        @log_exceptions
        @assert_prop('notExistingProp')
        @assert_arg('integer', SCH_INT)
        def bar3(self, integer=1):
            """
            bar 3 documentation
            """
            return 1 + integer


    logging.basicConfig(level=logging.DEBUG)
    a = A()
    print(help(a.bar2))
    print(help(a.bar3))
    with pytest.raises(MyException) as e_info:
        a.raise_exc()
    with pytest.raises(ValidationError) as e_info:
        a.foo('reziu')
    with pytest.raises(ValidationError) as e_info:
        a.bar(integer='reziu')
    with pytest.raises(ValidationError) as e_info:
        a.bar2(integer='reziu')
    with pytest.raises(AttributeError) as e_info:
        a.bar3(integer=1)



if __name__ == "__main__":
     test_decorators()
    #pytest.main(__file__)

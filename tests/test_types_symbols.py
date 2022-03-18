# -*- coding: utf-8 -*-
""" Unit tests for inspection utilities

test_inspect.py - created on 22/05/2018
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  """

from __future__ import print_function
from __future__ import unicode_literals



def function_example(a, b=1, *args):
    """
    My dummy function
    :param a: string
    :return: integer
    """
    return b


def test_function():
    from ngoinsp.inspectors import inspect_class, inspect_function
    fi = inspect_function(function_example)
    assert fi['arguments'][0]['name'] == 'a'
    assert fi['arguments'][1]['name'] == 'b'
    assert fi['arguments'][0]['description']
    assert fi['returns']
    assert len(fi['arguments']) == 2
    assert fi['varargs']['name'] == 'args'
    assert not fi['keywords']
    assert not fi['decorators']


class Foo:
    a = 1

    def bar(self, b=1):
        return self.a + b


class Foo2(Foo):
    b = 1

    @staticmethod
    def bar_static(b):
        return b

    @classmethod
    def bar_cls(cls):
        return cls.b


def test_class():
    from ngoinsp.inspectors import inspect_class, inspect_function
    ci = inspect_class(Foo)
    assert ci['methods']['bar']
    ci = inspect_class(Foo2)
    assert ci['methods']['bar_static']['is_staticmethod']
    assert ci['methods']['bar_cls']['is_classmethod']
    assert 'bar' in ci['methods_inherited']


if __name__ == "__main__":
    test_function()
    test_class()

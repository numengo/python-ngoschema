# *- coding: utf-8 -*-
"""
Misc utilities

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import gettext
import importlib
import inspect
import logging
import re
from builtins import object
from builtins import str

import six
from past.builtins import basestring

from .decorators import take_arrays
from .exceptions import InvalidValue
from ._qualname import qualname

_ = gettext.gettext


@take_arrays(0)
def is_basestring(value):
    """
    Test if value is a basestring
    """
    return isinstance(value, basestring) and not isinstance(value, str)


@take_arrays(0)
def is_string(value):
    """
    Test if value is a string
    """
    return isinstance(value, (str, basestring))


@take_arrays(0)
def is_pattern(value):
    """
    Test if value is a pattern, ie contains {{ }} formatted content 
    """
    return is_string(value) and '{{' in value


@take_arrays(0)
def is_expr(value):
    """
    Test if value is an expression and starts with `
    """
    return is_string(value) and value.strip().startswith('`')


@take_arrays(0)
def fullname(obj):
    if is_module(obj):
        return str(obj).split("'")[1]
    qn = getattr(obj,'__qualname__',None) or qualname(obj)
    mn = obj.__module__
    if mn is None or mn == str.__class__.__module__: # avoid builtin
        return qn
    return mn + '.' + qn
 


@take_arrays(0)
def import_from_string(value):
    """
    Imports a symbol from a string
    """
    poss = [m.start() for m in re.finditer('\.', '%s.' % value)]
    # going backwards
    for pos in reversed(poss):
        try:
            m = value[0:pos]
            ret = importlib.import_module(m)
            for a in value[pos + 1:].split('.'):
                if not a:
                    continue
                ret = getattr(ret, a, None)
                if not ret:
                    raise InvalidValue(
                        _('%s is not an importable object' % value))
            return ret
        except Exception as er:
            continue
    raise InvalidValue(_('%s is not an importable object' % value))


@take_arrays(0)
def is_module(value):
    """
    Test if value is a module
    """
    if is_string(value):
        try:
            value = import_from_string(value)
        except Exception as er:
            return False
    return inspect.ismodule(value)


@take_arrays(0)
def is_class(value):
    """
    Test if value is a class
    """
    if is_string(value):
        try:
            value = import_from_string(value)
        except Exception as er:
            return False
    return inspect.isclass(value)


@take_arrays(0)
def is_method(value):
    """
    Test if value is a method
    """
    if is_string(value):
        value = destringify.destringify(value)
    if inspect.isclass(value):
        return hasattr(value,'__call__')
    return inspect.ismethod(value) or inspect.ismethoddescriptor(value)


@take_arrays(0)
def is_function(value):
    """
    Test if value is a function
    """
    if is_string(value):
        try:
            value = import_from_string(value)
        except Exception as er:
            return False
    if inspect.isclass(value):
        return hasattr(value,'__call__')
    return inspect.isfunction(value)


@take_arrays(0)
def is_imported(value):
    """
    Test if a symbol is importable/imported
    """
    if is_string(value):
        try:
            value = import_from_string(value)
        except Exception as er:
            return False
    return is_class(value) or is_method(value) or is_module(
        value) or is_function(value)


@take_arrays(0)
def is_instance(value):
    """
    Test if value is an instance of a class
    """
    if getattr(value, '__class__'):
        return isinstance(value, value.__class__)
    return False


def is_mapping(value):
    """
    Test if value is a mapping (dict, ordered dict, ...)
    """
    if isinstance(value, collections.Mapping):
        return True
    return False


def is_sequence(value):
    """
    Test if value is a sequence (list, tuple, deque)
    """
    if isinstance(value,
                  collections.Sequence) and not isinstance(value, basestring):
        return True
    if isinstance(value, collections.deque):
        return True
    return False


def is_collection(value):
    """
    Test if value is a list, set, tuple or dict
    """
    if is_mapping(value):
        return True
    if is_sequence(value):
        return True
    if isinstance(value, collections.Set):
        return True
    return False


def apply_through_collection(coll, func):
    """
    Generic method to go through a complex collection
    and apply a transformation function on elements
    """
    if is_mapping(coll):
        for k, v in coll.items():
            coll[k] = func(k, v)
            apply_through_collection(v, func)
    elif is_sequence(coll):
        for i, v in enumerate(coll):
            coll[i] = func(i, v)
            apply_through_collection(v, func)


def obj_or_str(val):
    if is_string(val):
        return val, import_from_string(val)
    elif is_class(val):
        return fullname(val), val
    else:
        raise InvalidValue(_('%r is not an object class' % val))

def obj_or_str_arr(array):
    s_a = o_a = []
    for e in array:
        s, o = obj_or_str(e)
        s_a.append(s)
        o_a.append(o)
    return s_a, o_a

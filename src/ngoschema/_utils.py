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

from ._decorators import take_arrays
from .exceptions import InvalidValue

_ = gettext.gettext


def _is_string(value):
    return isinstance(value, (str, basestring))


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
    if _is_string(value):
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
    if _is_string(value):
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
    if _is_string(value):
        value = destringify.destringify(value)
    return inspect.ismethod(value) or inspect.ismethoddescriptor(value)


@take_arrays(0)
def is_function(value):
    """
    Test if value is a function
    """
    if _is_string(value):
        try:
            value = import_from_string(value)
        except Exception as er:
            return False
    return inspect.isfunction(value)


@take_arrays(0)
def is_imported(value):
    """
    Test if a symbol is importable/imported
    """
    if _is_string(value):
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

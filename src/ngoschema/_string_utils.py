# *- coding: utf-8 -*-
"""
String utilities

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import importlib
import inspect
import logging
import pathlib
import pprint
import re
from builtins import object
from builtins import str
from decimal import Decimal

from future.utils import text_to_native_str
from past.builtins import basestring

from ._decorators import take_arrays
from .exceptions import InvalidValue

_ = gettext.gettext


def _multiple_replacer(replace_dict):
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join(
        [re.escape(k) for k, v in list(replace_dict.items())]), re.M)
    return lambda string: pattern.sub(replacement_function, string)


def multiple_replace(string, key_values):
    """
    Replace efficiently multiple elements in a string according to a dictionary

    :param key_values: dictionary containing replacements
    :type key_values: dict
    :rtype: str
    """
    return _multiple_replacer(key_values)(string)


class CaseInsensitiveDict(dict):
    """
    Dictionary with keys insensitive to case
    """

    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, basestring) else key

    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(
            self.__class__._k(key))

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(
            self.__class__._k(key), value)

    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(
            self.__class__._k(key))

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(
            self.__class__._k(key))

    def has_key(self, key):
        return super(CaseInsensitiveDict, self).has_key(self.__class__._k(key))

    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(
            self.__class__._k(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(
            self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(
            self.__class__._k(key), *args, **kwargs)

    def update(self, E={}, **F):
        super(CaseInsensitiveDict, self).update(self.__class__(E))
        super(CaseInsensitiveDict, self).update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)


@take_arrays(0)
def split_string(string, delimiters=" ", strip=True):
    """
    Split string with using several delimiters

    :param delimiters: string containing all delimiters
    :type delimiters: string
    :param strip: strip whitespaces around returned elements
    :rtype: list
    """
    if delimiters:
        specials = "[\^$.|?*+(){}"
        dels = ['\%s' % d if d in specials else d for d in delimiters]
        regex = '|'.join([d for d in dels])
        return [w.strip() if strip else w for w in re.split(regex, string)]
    return [string]


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
    return isinstance(value, str) or isinstance(value, basestring)


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
def str_is_int(value):
    try:
        int(value)
        return True
    except:
        return False


@take_arrays(0)
def str_is_bool(value):
    return value.strip().lower() in ['true', 'false']


@take_arrays(0)
def str_is_float(value):
    try:
        float(value)
        return True
    except:
        return False


@take_arrays(0)
def str_to_float(value):
    """
    Clean a string and return a decimal.Decimal instance
    or a float if Decimal raises an exception.
    """
    value2 = regex_clean_float.sub('', value)
    try:
        return Decimal(value2)
    except Exception as er:
        pass
    try:
        return float(value2)
    except Exception as er:
        pass
    raise InvalidValue(_('impossible to create float from %s' % value))


regex_path_excl = re.compile('({{)+[#\?@]+(\/\/)+')
# https://regex101.com/r/MRsca7/3
regex_path = re.compile(
    '^(?:\w:)?(?:[^:*?\"<>|\r\n]+)?[\\\/](?:[^\\\/:?\"<>|\r\n]*)$')


@take_arrays(0)
def str_is_path(value):
    ret = regex_path.match(value)
    return ret or value.strip() in ['.', '..']


regex_filename = re.compile(
    '^(?:[^\\\/\s:?*\"<>|\r\n]*)\.(?:[^\\\/:?{}*\s\"<>|\r\n]+)$')


@take_arrays(0)
def str_is_filename(value):
    ret = regex_filename.match(value)
    return ret or value.strip() in ['.', '..']


regex_importable = re.compile('^[a-zA-Z_]+\w*\.*[\w\.]*\w+$')


@take_arrays(0)
def str_looks_like_importable(value):
    """ match an importable python object """
    return bool(regex_importable.match(value.strip()))

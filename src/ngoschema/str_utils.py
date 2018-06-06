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
import re

from past.builtins import basestring

from .decorators import take_arrays

_ = gettext.gettext


def _multiple_replacer(replace_dict):
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile(
        "|".join([re.escape(k) for k, v in list(replace_dict.items())]), re.M)
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
        dels = ["\%s" % d if d in specials else d for d in delimiters]
        regex = "|".join([d for d in dels])
        return [w.strip() if strip else w for w in re.split(regex, string)]
    return [string]

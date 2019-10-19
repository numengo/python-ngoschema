# *- coding: utf-8 -*-
"""
String utilities

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from builtins import str

from past.builtins import basestring
from ngoschema.decorators import take_arrays


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


def get_unicode(str_or_unicode, encoding='utf-8'):
    if isinstance(str_or_unicode, (str, basestring)):
        return str_or_unicode
    return str(str_or_unicode, encoding, errors='ignore')

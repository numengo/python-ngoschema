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
import json
import pathlib
from builtins import str
import pprint
import collections
from itertools import islice

from ngoschema import utils

from .utils import is_mapping, is_sequence, is_collection, is_string
from past.builtins import basestring
from ngoschema.decorators import take_arrays
from .. import settings


class PrettyShortPrinter(pprint.PrettyPrinter):
    _dispatch = pprint.PrettyPrinter._dispatch.copy()

    def __init__(self, max_el=None, max_str_len=None, **kwargs):
        from ngoschema import settings
        self._maxEl = max_el or settings.PPRINT_MAX_EL
        self._maxStrLen = max_str_len or settings.PPRINT_MAX_STRL
        self._maxCollLen = self._maxEl * self._maxStrLen
        pprint.PrettyPrinter.__init__(self, **kwargs)

    def _pprint_dict(self, object, stream, indent, allowance, context, level):
        write = stream.write
        write('{')
        if self._indent_per_level > 1:
            write((self._indent_per_level - 1) * ' ')
        length = len(object)
        items = sorted(islice(object.items(), 0, self._maxEl), key=pprint._safe_tuple)
        self._format_dict_items(items, stream, indent, allowance + 1, context, level)
        if length>=self._maxEl:
            self._format('+%i...' % (length-self._maxEl), stream, indent, allowance+1, context, level)
        write('}')

    _dispatch[dict.__repr__] = _pprint_dict
    _dispatch[collections.OrderedDict.__repr__] = _pprint_dict

    def _pprint_list(self, object, stream, indent, allowance, context, level):
        stream.write('[')
        self._format_items(object[:self._maxEl], stream, indent, allowance + 1,
                           context, level)
        if len(object)>=self._maxEl:
            self._format('+%i...' % (len(object)-self._maxEl), stream, indent, allowance+1, context, level)
        stream.write(']')

    _dispatch[list.__repr__] = _pprint_list

    def _pprint_str(self, object, stream, indent, allowance, context, level):
        if not len(object):
            stream.write(repr(object))
            return
        if len(object)>=self._maxStrLen:
            object = str(object)[:self._maxStrLen] + '+%i...' % (len(object)-self._maxStrLen)
        return pprint.PrettyPrinter._pprint_str(self, object, stream, indent, allowance, context, level)

    _dispatch[str.__repr__] = _pprint_str

    def _format(self, object, stream, indent, allowance, context, level):
        objid = id(object)
        if objid in context:
            stream.write(pprint._recursion(object))
            self._recursive = True
            self._readable = False
            return
        if hasattr(object, '__properties'):
            # we use our str representation as a safe repr
            rep = str(object)
            if hasattr(object, 'isLiteralClass'):
                if len(rep) >= self._maxStrLen:
                    rep = rep[:self._maxStrLen] + '+%i...' % (len(rep)-self._maxStrLen)
        elif is_collection(object):
            max_coll_len = self._maxCollLen
            if self._depth is not None:
                max_coll_len = (1 + self._depth - level) * self._maxCollLen
            if is_mapping(object):
                rep = self._repr({k: v for k, v in islice(object.items(), 0, self._maxEl)}, context, level)
                if len(object) >= self._maxEl:
                    rep = rreplace(rep, '}', '+%i...}' % (len(object)-self._maxEl))
                if len(rep) >= max_coll_len:
                    rep = rep[:max_coll_len] + '...}'
            else:
                rep = self._repr([v for v in object[0:self._maxEl]], context, level)
                if len(object) >= self._maxEl:
                    rep = rreplace(rep, ']', '+%i...]' % (len(object)-self._maxEl))
                if len(rep) >= max_coll_len:
                    rep = rep[:max_coll_len] + '...]'
        elif is_string(object) and len(object) >= self._maxStrLen:
            object = object[:self._maxStrLen] + f'+{len(object) - self._maxStrLen}...'
            rep = self._repr(object, context, level)
        else:
            rep = self._repr(object, context, level)
        max_width = self._width - indent - allowance
        if len(rep) > max_width:
            p = self._dispatch.get(type(object).__repr__, None)
            if p is not None:
                context[objid] = 1
                p(self, object, stream, indent, allowance, context, level + 1)
                del context[objid]
                return
            elif isinstance(object, dict):
                context[objid] = 1
                self._pprint_dict(object, stream, indent, allowance,
                                  context, level + 1)
                del context[objid]
                return
        stream.write(rep)


_pprinter = PrettyShortPrinter(indent=0, depth=2, width=10000)
log_format = _pprinter.pformat


class lazy_format(object):
    __slots__ = ('fmt', 'args', 'to_format', 'kwargs')

    def __init__(self, fmt, *args, to_format=[], **kwargs):
        self.fmt = fmt
        self.args = list(args)
        self.kwargs = kwargs
        self.to_format = to_format

    def __str__(self):
        for a in self.to_format:
            if utils.is_integer(a):
                self.args[a] = log_format(list(self.args)[a])
            else:
                self.kwargs[a] = log_format(self.kwargs[a])
        return self.fmt.format(*self.args, **self.kwargs)


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


def rreplace(s, old, new, occurrence=1):
    """right replace function"""
    li = s.rsplit(old, occurrence)
    return new.join(li)


def file_link_format(fp):
    return pathlib.Path(fp).resolve().as_uri()


def shorten(s, max_size=settings.PPRINT_MAX_STRL, str_fun=str):
    s = str_fun(s)
    if len(s) > max_size:
        return s[:max_size] + '...'
    return s


def inline(s):
    return '\\n'.join(s.split('\n'))

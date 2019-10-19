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
from builtins import str
import collections

import six
from past.builtins import basestring
from python_jsonschema_objects import util as pjo_util
from .decorators import take_arrays
from . import utils

class ProtocolJSONEncoder(pjo_util.ProtocolJSONEncoder):

    def __init__(self,
                 no_defaults=True,
                 remove_refs=True,
                 attr_prefix='',
                 cdata_key='#text',
                 **kwargs):
        self.no_defaults = no_defaults
        self.remove_refs = remove_refs
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        pjo_util.ProtocolJSONEncoder.__init__(self, **kwargs)

    def default(self, obj):
        from python_jsonschema_objects import classbuilder
        from python_jsonschema_objects import wrapper_types

        if isinstance(obj, classbuilder.LiteralValue):
            return obj._value
        if isinstance(obj, wrapper_types.ArrayWrapper):
            if not self.remove_refs:
                return [self.default(item) for item in obj]
            ret = []
            for item in obj:
                if isinstance(item, classbuilder.ProtocolBase) and '$id' in item:
                    ret.append({'$ref': item.get('$id')})
                else:
                    ret.append(self.default(item))
            return ret
        if isinstance(obj, classbuilder.ProtocolBase):
            ns =  getattr(obj, '__not_serialized__', [])
            reqs =  getattr(obj, '__required__', [])
            defvs =  getattr(obj, '__has_default__', {})
            props = collections.OrderedDict()
            to_put_first = []
            for raw, trans in six.iteritems(obj.__prop_names_flatten__):
                if raw in ns:
                    continue
                prop = getattr(obj, trans)
                if not prop:
                    continue
                if self.no_defaults and raw not in reqs:
                    defv = defvs.get(trans)
                    if getattr(prop, '_pattern', '') == defv or prop == defv:
                        continue
                pname = raw
                if getattr(prop, "isLiteralClass", False):
                    pname = f'{self.attr_prefix}{raw}' # raw or trans???
                if self.remove_refs and isinstance(prop, classbuilder.ProtocolBase):
                    props[pname] = {'$ref': prop.get('$id')} if '$id' in prop else self.default(prop)
                else:
                    if raw == self.cdata_key:
                        props[pname] = str(prop)
                    else:
                        props[pname] = self.default(prop)
                # put translated properties first
                if raw != trans:
                    to_put_first.append(pname)

            for raw, prop in six.iteritems(obj._extended_properties):
                if prop is not None:
                    props[raw] = self.default(prop)
            # place special names first
            for k in to_put_first:
                props.move_to_end(k, last=False)
            return props
        else:
            return json.JSONEncoder.default(self, obj)

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

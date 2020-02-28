# *- coding: utf-8 -*-
"""
Json Encoder

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals
import collections
import json

import six
from datetime import date, datetime, time, timedelta
from pathlib import Path
from python_jsonschema_objects import util as pjo_util


class ProtocolJSONEncoder(pjo_util.ProtocolJSONEncoder):
    no_defaults = True
    remove_refs = True
    attr_prefix = ''
    excludes = []
    only = []

    def __init__(self,
                 no_defaults=None,
                 remove_refs=None,
                 attr_prefix=None,
                 excludes=None,
                 only=None,
                 **kwargs):
        from .. import settings
        self.no_defaults = no_defaults or self.no_defaults
        self.remove_refs = remove_refs or self.remove_refs
        self.attr_prefix = attr_prefix or self.attr_prefix
        self.excludes = excludes or self.excludes
        self.only = only or self.only
        pjo_util.ProtocolJSONEncoder.__init__(self, **kwargs)

    def default(self, obj):
        from python_jsonschema_objects import classbuilder
        from python_jsonschema_objects import wrapper_types
        from ..models.entity import Entity
        from ..literals import LiteralValue
        from ..validators.pjo import format_date, format_datetime, format_time, format_path

        if isinstance(obj, classbuilder.LiteralValue):
            return obj.for_json()
        if isinstance(obj, wrapper_types.ArrayWrapper):
            if not self.remove_refs:
                return [self.default(item) for item in obj]
            ret = []
            for item in obj:
                if isinstance(item, Entity) and item.identity_keys:
                    ret.append(item.identity_keys)
                else:
                    ret.append(self.default(item))
            return ret
        if isinstance(obj, classbuilder.ProtocolBase):
            ns = getattr(obj, '__not_serialized__', [])
            reqs = getattr(obj, '__required__', [])
            defvs = getattr(obj, '__has_default__', {})
            props = collections.OrderedDict()
            to_put_first = []

            # declared properties
            for raw, trans in obj.__prop_names_flatten__.items():
                # excluded at schema level
                if raw in ns:
                    continue
                # excluded at encoder lever
                if set([raw, trans]).intersection(self.excludes):
                    continue
                if self.only and not set([raw, trans]).intersection(self.only):
                    continue

                prop = getattr(obj, trans, None)

                # property name is the raw one, prefixed for literal attributes
                pname = raw
                if  isinstance(prop, LiteralValue):
                    pname = f'{self.attr_prefix}{raw}'
                # put translated properties first
                if raw != trans:
                    to_put_first.append(pname)

                if prop is None:
                    if raw in reqs:
                        props[pname] = None
                    continue

                # remove defaults
                if raw in defvs and self.no_defaults and raw not in reqs:
                    defv = defvs.get(raw)
                    if getattr(prop, '_pattern', '') == defv or prop == defv:
                        continue

                if self.remove_refs and isinstance(prop, Entity) and prop.identity_keys:
                    props[pname] = prop.identity_keys
                else:
                    props[pname] = self.default(prop)

            # lazy data
            for pname in obj._lazy_data.keys():
                props[pname] = obj._get_prop_value(pname)

            # extended properties
            for raw, prop in six.iteritems(obj._extended_properties):
                # property name is the raw one, prefixed for literal attributes
                pname = raw
                if getattr(prop, "isLiteralClass", False):
                    pname = f'{self.attr_prefix}{raw}'
                props[pname] = self.default(prop)

            # place special names first
            for k in to_put_first:
                if k in props:
                    props.move_to_end(k, last=False)

            return props

        # additional types
        if isinstance(obj, date):
            return format_date(obj)
        if isinstance(obj, datetime):
            return format_datetime(obj)
        if isinstance(obj, time):
            return format_time(obj)
        if isinstance(obj, Path):
            return format_path(obj)

        return json.JSONEncoder.default(self, obj)


def set_json_defaults(kwargs=None):
    kwargs = kwargs or{}
    kwargs.setdefault('indent', 2)
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('separators', None)
    kwargs.setdefault('default', None)
    return kwargs


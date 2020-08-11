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


class ProtocolJSONEncoder(json.JSONEncoder):

    def __init__(self,
                 no_defaults=True,
                 no_read_only=True,
                 use_entity_ref=True,
                 attr_prefix='',
                 excludes=[],
                 only=[],
                 **kwargs):
        from .. import settings
        self.no_defaults = no_defaults
        self.no_read_only = no_read_only
        self.use_entity_ref = use_entity_ref
        self.attr_prefix = attr_prefix
        self.excludes = excludes
        self.only = only
        json.JSONEncoder.__init__(self, **kwargs)

    def default(self, obj):
        from ..types import Type, Literal, Array, ArrayProtocol, ObjectProtocol, TypeChecker
        for t in (ObjectProtocol, ArrayProtocol):
            if isinstance(obj, t):
                return t.do_serialize(obj, excludes=self.excludes,
                                        only=self.only,
                                        no_read_only=self.no_read_only,
                                        no_defaults=self.no_defaults,
                                        attr_prefix=self.attr_prefix,
                                        use_entity_ref=self.use_entity_ref)
        else:
            tn, ty = TypeChecker.detect_type(obj)
            return ty().serialize(obj)
        return json.JSONEncoder.default(self, obj)

    def default_(self, obj):
        from python_jsonschema_objects import classbuilder
        from python_jsonschema_objects import wrapper_types
        from ..models.entity import Entity
        from ..types import Type, Literal, Array, ArrayProtocol, ObjectProtocol
        #from ..literals import LiteralValue
        #from ..utils import is_string, is_literal
        from ..validators.pjo import format_date, format_datetime, format_time, format_path

        if Literal.check(obj):
            return obj
        if Array.check(obj):
            if not self.use_entity_ref:
                return [self.default(item) for item in obj]
            ret = []
            for item in obj:
                if isinstance(item, Entity) and item.identity_keys:
                    ret.append(item.identity_keys)
                else:
                    ret.append(self.default(item))
            return ret
        if isinstance(obj, (ObjectProtocol, ArrayProtocol)):
            return obj.do_serialize(excludes=self.excludes, only=self.only, )
            ns = getattr(obj, '_not_serialized', [])
            reqs = getattr(obj, '_required', [])
            ro = getattr(obj, '_read_only', {})
            defvs = getattr(obj, '_has_default', {})
            props = collections.OrderedDict()
            to_put_first = []

            # declared properties
            for (raw, trans), prop in zip(obj.__prop_names_ordered__.items(), obj._properties.values()):
                # excluded at schema level
                if raw in ns:
                    continue
                if self.no_read_only and raw in ro:
                    continue
                # excluded at encoder lever
                if set([raw, trans]).intersection(self.excludes):
                    continue
                if self.only and not set([raw, trans]).intersection(self.only):
                    continue

                # property name is the raw one, prefixed for literal attributes
                pname = raw
                if isinstance(prop, LiteralValue):
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
                    if prop._expr_pattern == defv or prop == defv:
                        continue

                if self.use_entity_ref and isinstance(prop, Entity) and prop.identity_keys:
                    props[pname] = prop.identity_keys
                else:
                    props[pname] = self.default(prop)

            # extended properties
            for raw, prop in obj._extended_properties.items():
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
    kwargs = kwargs or {}
    kwargs.setdefault('indent', 2)
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('separators', None)
    kwargs.setdefault('default', None)
    return kwargs


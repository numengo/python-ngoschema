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
        from ..protocols import ArrayProtocol, ObjectProtocol
        from ..managers import TypeBuilder
        for t in (ObjectProtocol, ArrayProtocol):
            if isinstance(obj, t):
                return t.do_serialize(obj, excludes=self.excludes,
                                        only=self.only,
                                        no_read_only=self.no_read_only,
                                        no_defaults=self.no_defaults,
                                        attr_prefix=self.attr_prefix,
                                        use_entity_ref=self.use_entity_ref)
        else:
            tn, ty = TypeBuilder.detect_type(obj)
            return ty().serialize(obj)


def set_json_defaults(kwargs=None):
    kwargs = kwargs or {}
    kwargs.setdefault('indent', 2)
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('separators', None)
    kwargs.setdefault('default', None)
    return kwargs


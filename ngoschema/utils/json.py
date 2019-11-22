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
from python_jsonschema_objects import util as pjo_util


class ProtocolJSONEncoder(pjo_util.ProtocolJSONEncoder):

    def __init__(self,
                 no_defaults=True,
                 remove_refs=True,
                 attr_prefix='',
                 cdata_key=None,
                 **kwargs):
        from .. import settings
        self.no_defaults = no_defaults
        self.remove_refs = remove_refs
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key or settings.DEFAULT_CDATA_KEY
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
            ns = getattr(obj, '__not_serialized__', [])
            reqs = getattr(obj, '__required__', [])
            defvs = getattr(obj, '__has_default__', {})
            props = collections.OrderedDict()
            to_put_first = []
            for raw, trans in six.iteritems(obj.__prop_names_flatten__):
                if raw in ns:
                    continue
                prop = getattr(obj, trans)
                if prop is None:
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


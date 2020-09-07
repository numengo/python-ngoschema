# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol, ArrayProtocol, TypeProtocol
from ...managers import NamespaceManager, default_ns_manager
from ...types import String as String_t, Boolean as Boolean_t, Object as Object_t
from ...types import symbols
from ...decorators import memoized_property, depend_on_prop
from ..metadata import NamedObject


class Type(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/Type'

    def _check(self, value, **opts):
        if not ObjectProtocol._check(self, value, **opts):
            # transform a boolean input
            if Boolean_t.check(value, convert=True):
                return True  # True or False are valid types
            if String_t.check(value):
                return True  # $ref
            return False
        return True

    def _convert(self, value, **opts):
        data = value
        if Object_t.check(data):
            for k, v in list(data.items()):
                raw, trans = self._properties_raw_trans(k)
                t = self.items_type(raw)
                if t.is_array() and Object_t.check(v):
                    del data[k] # remove previous entry in case it s an alias (eg $defs)
                    vs = []
                    for i, (n, d) in enumerate(v.items()):
                        d = {'booleanValue': d} if Boolean_t.check(d) else dict(d)
                        d['name'] = n
                        vs.append(d)
                    data[raw] = vs
        # transform a boolean input
        elif Boolean_t.check(data, convert=True):
            data = {'booleanValue': Boolean_t.convert(data)}
        elif String_t.check(data):
            data = {'$ref': data}
        return Object_t._convert(self, data, **opts)

    def __init__(self, *args, **kwargs):
        #data = args[0] if args else kwargs
        #kwargs = kwargs if args else {}
        # check for items which are declared as arrays but given as named mappings
        ObjectProtocol.__init__(self, *args, **kwargs)
        if self.defaultValue:
            self.hasDefault = True

    def _json_schema(self, cls=None, excludes=[], only=[], **opts):
        if self.ref:
            return {'$ref': self.serialize_item('$ref', context=self._context)}
        elif self.booleanValue is not None:
            return self.booleanValue
        else:
            cls = cls or self.__class__
            cps = set(cls._properties).difference(cls._not_validated).difference(cls._not_serialized)\
                .difference(excludes).difference(['name', 'hasDefault', '_type'])\
                .union(['type', 'default', 'rawLiterals'])
            cps = list(cps.intersection(only)) if only else list(cps)
            ret = self.do_serialize(only=cps, no_defaults=True, **opts)
            #ret = OrderedDict(cls.serialize(self, only=cps, no_defaults=True, **opts))
            ret.setdefault('type', self.type)
            if self.hasDefault:
                dft = self.defaultValue
                if hasattr(dft, 'do_serialize'):
                    dft = dft.do_serialize()
                ret['default'] = dft
            ret.move_to_end('type', False)
            if 'title' in ret:
                ret.move_to_end('title', False)
            return ret

    @memoized_property
    def json_schema(self):
        return self._json_schema()


class Primitive(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/Primitive'


class NamedType(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/NamedType'


class Boolean(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/boolean/$defs/Boolean'


class Number(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/numerics/$defs/Number'


class Integer(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/numerics/$defs/Integer'



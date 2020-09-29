# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ...decorators import memoized_property, log_exceptions
from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ...types import Array as Array_t, Symbol as Symbol_t
from .types import Type, NamedType
from ..metadata import NamedObject


class Array(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/collections/$defs/Array'

    def __init__(self, *args, **kwargs):
        Type.__init__(self, *args, **kwargs)

    def set_items(self, items):
        if items:
            items = items if Array_t.check(items) else [items]
            items = [i if isinstance(i, Type) else Type(i, context=self._context) for i in items]
            self['items'] = items if len(items) > 1 else items[0]
            self._set_data_validated('items', items)


class Object(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/collections/$defs/Object'


class Definition(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/collections/$defs/Definition'

    def json_schema(self, **opts):
        ret = Object.json_schema(self, **opts)
        a = ret.pop('attributes', {})
        if a:
            ret.update(a)
        return ret


class Descriptor(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/protocols/$defs/descriptors/$defs/Descriptor'

    def json_schema(self):
        return True


class PropertyDescriptor(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/protocols/$defs/descriptors/$defs/PropertyDescriptor'

    @log_exceptions
    def json_schema(self):
        return self.ptype.json_schema()

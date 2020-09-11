# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ...types.array import Array as Array_t
from .types import Type
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

    def set_context(self, context=None, *extra_contexts):
        NamedObject.set_context(self, context, *extra_contexts)

    def to_json_schema(self, ns):
        sch = self._json_schema()
        for tag in ['properties', 'patternProperties', 'definitions', 'attributes']:
            a = sch.get(tag)
            if a:
                sch[tag] = {d.pop('name'): d for d in a}
            else:
                sch.pop(tag, None)
        # remove private
        for k in list(sch.get('properties', {})):
            if k.startswith('__'):
                del sch['properties'][k]
        if not sch.get('properties'):
            sch.pop('properties', None)
        if 'definitions' in sch:
            sch['$defs'] = sch.pop('definitions')
        return sch


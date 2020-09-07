# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from ...protocols import SchemaMetaclass, with_metaclass


class Array(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/collections/$defs/Array'


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


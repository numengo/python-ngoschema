# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ...decorators import memoized_property, log_exceptions
from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ...types import Array as Array_t, Symbol as Symbol_t
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

    @log_exceptions
    def json_schema(self):
        ret = self._json_schema(cls=Object, excludes=['properties', 'additionalProperties', 'patternProperties'])
        if self.additionalProperties is not None:
            ret['additionalProperties'] = self.additionalProperties.json_schema()
        if self.patternProperties:
            ret['patternProperties'] = {p.name: p.json_schema() for p in self.patternProperties}
        if self.properties:
            ret['properties'] = {p.name: p.json_schema() for p in self.properties}
        if self.required:
            ret['required'] = self.required.do_serialize()
        return ret


class Definition(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/collections/$defs/Definition'

    def set_context(self, context=None, *extra_contexts):
        NamedObject.set_context(self, context, *extra_contexts)

    def json_schema(self):
        ret = OrderedDict()
        if self.extends:
            ret['extends'] = self.extends
        for a in self.attributes:
            ret[a.name] = a.json_schema()
        if self.dependencies:
            ret['dependencies'] = {k: Array_t().convert(v) for k, v in self.dependencies.do_serialize().items()}
        if self.readOnly:
            ret['readOnly'] = self.readOnly.do_serialize()
        if self.notValidated:
            ret['notValidated'] = self.notValidated.do_serialize()
        if self.notSerialized:
            ret['notSerialized'] = self.notSerialized.do_serialize()
        ret.update(Object.json_schema(self))
        if self.definitions:
            ret.setdefault('$defs', {})
            for d in self.definitions:
                ret['$defs'][d.name] = d.json_schema()
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

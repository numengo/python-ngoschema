# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ...protocols import SchemaMetaclass, with_metaclass, TypeProtocol
from .collections import Object


class Symbol(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/Symbol'

    @staticmethod
    def inspect(value):
        from ...inspect.inspect_symbols import inspect_symbol
        return Symbol(inspect_symbol(value))


class Variable(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/Variable'


class VariableValue(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/VariableValue'


class Argument(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Argument'

    def _convert(self, value, **opts):
        from ...inspect.doc_rest_parser import parse_docstring
        data = Variable._convert(self, value, **opts)
        doctype = data.pop('doctype', None)
        if doctype:
            data.update({k: v for k, v in parse_docstring(doctype).items() if v})
        return Object._convert(self, data, **opts)


class Function(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Function'

    @staticmethod
    def inspect(value):
        from ...inspect.inspect_symbols import inspect_function
        return Function(inspect_function(value))


class FunctionCall(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/FunctionCall'

    @staticmethod
    def inspect(value):
        from ...inspect.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


class Class(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/symbols/$defs/Class'
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/classes/$defs/Class'

    @staticmethod
    def inspect(value):
        from ...inspect.inspect_symbols import inspect_class
        return Class(inspect_class(value))

    @property
    def attributesInherited(self):
        ret = {p.name: p for p in self.attributes}
        for m in self.mro:
            ret.update(m.attributesInherited)
        return ret

    @property
    def propertiesInherited(self):
        ret = {p.name: p for p in self.properties}
        for m in self.mro:
            ret.update(m.propertiesInherited)
        return ret

    @property
    def methodsInherited(self):
        try:
            ret = {p.name: p for p in self.methods}
            for m in self.mro:
                ret.update(m.methodsInherited)
            return ret
        except Exception as er:
            raise er

    def to_json_schema(self, ns):
        return self._json_schema()

    def id(self, ns):
        return getattr(self.symbol, '_id', None) or ns.get_cname_id(f'{self.module.__name__}.{self.symbol.__name__}')


class Module(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/symbols/$defs/Module'
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/modules/$defs/Module'

    @staticmethod
    def inspect(value):
        from ...inspect.inspect_symbols import inspect_module
        return Module(inspect_module(value))

    def to_json_schema(self, ns):
        return self._json_schema()
        # TODO delete below
        sch = TypeProtocol.json_schema(self)
        return sch
        sch = {'$id': self.id(ns), 'type': 'object'}
        if self.description:
            sch['description'] = self.description
        if self.longDescription:
            sch['longDescription'] = self.longDescription
        sch['$defs'] = {c.name: c.to_json_schema(ns) for c in self.classes if not c.name.startswith('__')}
        for v in sch['$defs'].values():
            v.pop('$id', None)
        sch['functions'] = {c.name: c.to_json_schema(ns) for c in self.functions}
        return sch

    def schema_id(self, ns):
        return ns.get_cname_id(f'{self.symbol.__name__}')

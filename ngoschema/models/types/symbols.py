# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ...decorators import memoized_property
from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from .collections import Object


class Symbol(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/Symbol'

    def set_context(self, context=None, *extra_contexts):
        from ...managers.namespace_manager import NamespaceManager, default_ns_manager
        ObjectProtocol.set_context(self, context, *extra_contexts)
        self._ns_mgr = next((m for m in self._context.maps if isinstance(m, NamespaceManager)), default_ns_manager)

    @staticmethod
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_symbol
        data = inspect_symbol(value)
        return Symbol(data, **opts)

    def to_json_schema(self):
        return self.do_serialize(excludes=['name'], no_defaults=True) or True


class Value(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/Value'

    @memoized_property
    def json_schema(self):
        ret = self._json_schema(excludes=['value'])
        return ret


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

    @memoized_property
    def json_schema(self):
        ret = self._json_schema()
        if 'varargs' in ret:
            ret.move_to_end('varargs')
        if 'kwargs' in ret:
            ret.move_to_end('kwargs')
        return ret


class Function(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Function'

    @staticmethod
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_function
        data = inspect_function(value)
        return Function(data, **opts)

    @memoized_property
    def json_schema(self):
        ret = self._json_schema(excludes=['decorators', 'imports', 'symbol', 'module'])
        ret.pop('type', None)
        ret['arguments'] = [{'name': a.name} for a in self.arguments]
        for d, a in zip(ret['arguments'], self.arguments):
            d.update(a.json_schema)
        if self.returns:
            ret['returns'] = self.returns.json_schema
        return ret


class FunctionCall(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/FunctionCall'

    @staticmethod
    def inspect(value):
        from ...inspect.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


class Class(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/classes/$defs/Class'

    @staticmethod
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_class
        data = inspect_class(value)
        return Class(data, **opts)

    @property
    def attributesInherited(self):
        ret = {}
        for m in self.mro:
            ret.update(m.attributesInherited)
        ret.update({p.name: p for p in self.attributes})
        return ret

    @property
    def descriptorsInherited(self):
        ret = {}
        for m in self.mro:
            ret.update(m.descriptorsInherited)
        ret.update({p.name: p for p in self.descriptors})
        return ret

    @property
    def methodsInherited(self):
        try:
            ret = {}
            for m in self.mro:
                ret.update(m.methodsInherited)
            ret.update({p.name: p for p in self.methods})
            return ret
        except Exception as er:
            raise er

    @memoized_property
    def json_schema(self):
        #sch = {'$id': self.schema_id(), 'type': 'object'}
        sch = {'type': 'object'}
        if self.description:
            sch['description'] = self.description
        if self.longDescription:
            sch['longDescription'] = self.longDescription
        if self.abstract:
            sch['abstract'] = True
        if self.mro:
            sch['extends'] = [m.schema_id() for m in self.mro]

        sch['properties'] = properties = {}
        if self.init:
            properties.update({a.name: a.json_schema or True for a in self.init.arguments})
        properties.update({n: p.json_schema or True for n, p in self.attributesInherited.items() if not n.startswith('__')})
        properties.update({n: p.json_schema or True for n, p in self.descriptorsInherited.items() if not n.startswith('__')})
        if not sch['properties']:
            del sch['properties']

        # not sure methods should be jsonschema / TODO make a corresponding .openapi method returning schema and available methods
        #sch['methods'] = {n: p.json_schema or {'arguments': []} for n, p in self.methodsInherited.items() if not n.startswith('__')}

        return sch

    def schema_id(self):
        return getattr(self.symbol, '_id', None) or self._ns_mgr.get_cname_id(f'{self.module.__name__}.{self.symbol.__name__}')


class Module(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/modules/$defs/Module'

    @staticmethod
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_module
        data = inspect_module(value)
        return Module(data, **opts)

    @memoized_property
    def json_schema(self):
        sch = {'type': 'object'}
        if self.description:
            sch['description'] = self.description
        if self.longDescription:
            sch['longDescription'] = self.longDescription
        sch['$defs'] = {c.name: c.json_schema for c in self.classes if not c.name.startswith('__')}
        #sch['functions'] = {c.name: c.json_schema or True for c in self.functions}
        for m in self.modules:
            if m.__name__.startswith(self.symbol.__name__):
                mm = Module.inspect(m, context=self._context)
                sch['$defs'][mm.name.split('.')[-1]] = mm.json_schema
        return sch

    def schema_id(self):
        return self._ns_mgr.get_cname_id(f'{self.symbol.__name__}')

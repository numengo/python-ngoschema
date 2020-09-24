# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from functools import lru_cache

from ...decorators import memoized_property, log_exceptions
from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ...types.symbols import Function as Function_t, Class as Class_t, Module as Module_t, Symbol as Symbol_t
from .collections import Object


class Symbol(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/Symbol'

    def set_context(self, context=None, *extra_contexts):
        from ...managers.namespace_manager import NamespaceManager, default_ns_manager
        ObjectProtocol.set_context(self, context, *extra_contexts)
        self._ns_mgr = next((m for m in self._context.maps if isinstance(m, NamespaceManager)), default_ns_manager)

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_symbol
        data = inspect_symbol(value)
        return Symbol(data, **opts)

    def to_json_schema(self):
        return self.do_serialize(excludes=['name'], no_defaults=True) or True


class Value(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/Value'

    def json_schema(self):
        ret = self._json_schema(excludes=['value'])
        return ret


class Variable(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/Variable'


class VariableValue(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/VariableValue'

    def json_schema(self):
        return self.valueLiteral


class Argument(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Argument'

    def _convert(self, value, **opts):
        from ...inspect.doc_rest_parser import parse_docstring
        data = Variable._convert(self, value, **opts)
        doctype = data.pop('doctype', None)
        if doctype:
            data.update({k: v for k, v in parse_docstring(doctype).items() if v})
        return Object._convert(self, data, **opts)

    def json_schema(self):
        ret = self._json_schema()
        if 'varargs' in ret:
            ret.move_to_end('varargs')
        if 'kwargs' in ret:
            ret.move_to_end('kwargs')
        return ret


class Function(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Function'
    _lazy_loading = True

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_function
        data = inspect_function(value)
        return Function(data, **opts)

    @log_exceptions
    def json_schema(self):
        ret = self._json_schema(excludes=['decorators', 'imports', 'symbol', 'module'])
        ret.pop('type', None)
        ret['arguments'] = [{'name': a.name} for a in self.arguments]
        for d, a in zip(ret['arguments'], self.arguments):
            d.update(a.json_schema())
        if self.returns:
            ret['returns'] = self.returns.json_schema()
        return ret


class FunctionCall(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/FunctionCall'

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value):
        from ...inspect.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


class Method(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/classes/$defs/Method'
    _lazy_loading = True


class Class(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/classes/$defs/Class'
    _lazy_loading = True

    @memoized_property
    def mroClasses(self):
        return [Class.inspect(m) for m in self.mro]

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_class
        data = inspect_class(value)
        return Class(data, **opts)

    @memoized_property
    def attributesInherited(self):
        ret = {}
        for m in self.mroClasses:
            ret.update(m.attributesInherited)
        ret.update({p.name: p for p in self.attributes})
        return ret

    @memoized_property
    def descriptorsInherited(self):
        ret = {}
        for m in self.mroClasses:
            ret.update(m.descriptorsInherited)
        ret.update({p.name: p for p in self.descriptors})
        return ret

    @memoized_property
    def methodsInherited(self):
        try:
            ret = {}
            for m in self.mroClasses:
                ret.update(m.methodsInherited)
            ret.update({p.name: p for p in self.methods})
            return ret
        except Exception as er:
            raise er

    @log_exceptions
    def json_schema(self, with_protected=False):
        sch = {'type': 'object'}
        if self.description:
            sch['description'] = self.description
        if self.longDescription:
            sch['longDescription'] = self.longDescription
        if self.abstract:
            sch['abstract'] = True
        if self.mroClasses:
            mro = [m for m in self.mro if isinstance(m.symbol, ObjectProtocol) or m.symbol.__module__ in self._ns_mgr]
            sch['extends'] = [m.schema_id() for m in mro]
            if not with_protected:
                for e in list(sch['extends']):
                    if e.rsplit('/', 1)[1][0] == '_':
                        sch['extends'].remove(e)
        if not isinstance(self.symbol, ObjectProtocol):
            sch['wraps'] = Symbol_t.serialize(self.symbol)
        sch.update({a.name: a.json_schema() or True for a in self.attributes if not a.name.startswith('__')})
        sch['properties'] = properties = {}
        if self.init:
            properties.update({a.name: a.json_schema() or True for a in self.init.arguments})
        #properties.update({n: p.json_schema() or True for n, p in self.descriptorsInherited.items() if not n.startswith('__')})
        properties.update({d.name: d.json_schema() or True for d in self.descriptors if not d.name.startswith('__')})
        if not with_protected:
            to_remove = [k for k in sch['properties'].keys() if k[0] == '_']
            for k in to_remove:
                del sch['properties'][k]
        if not sch['properties']:
            del sch['properties']
        if 'required' in sch:
            sch['properties']['required'] = {'default': sch.pop('required')}

        # not sure methods should be jsonschema / TODO make a corresponding .openapi method returning schema and available methods
        #sch['methods'] = {n: p.json_schema or {'arguments': []} for n, p in self.methodsInherited.items() if not n.startswith('__')}

        return sch

    def schema_id(self):
        return getattr(self.symbol, '_id', None) or self._ns_mgr.get_cname_id(f'{self.module.__name__}.{self.symbol.__name__}')


class Module(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/modules/$defs/Module'

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value, **opts):
        from ...inspect.inspect_symbols import inspect_module
        data = inspect_module(value)
        return Module(data, **opts)

    def json_schema(self, with_protected=False):
        sch = {'type': 'object'}
        if not isinstance(self.symbol, ObjectProtocol):
            sch['wraps'] = Symbol_t.serialize(self.symbol)
        if self.description:
            sch['description'] = self.description
        if self.longDescription:
            sch['longDescription'] = self.longDescription
        sch['$defs'] = {c.name: c.json_schema(with_protected=with_protected)
                        for c in self.classes if not c.name.startswith('__')}
        if not with_protected:
            to_remove = [k for k in sch['$defs'].keys() if k[0] == '_']
            for k in to_remove:
                del sch['$defs'][k]
        #sch['functions'] = {c.name: c.json_schema() or True for c in self.functions}
        for m in self.modules:
            if m.__name__.startswith(self.symbol.__name__):
                mm = Module.inspect(m, context=self._context)
                sch['$defs'][mm.name.split('.')[-1]] = mm.json_schema(with_protected=with_protected)
        if not sch['$defs']:
            del sch['$defs']
        return sch

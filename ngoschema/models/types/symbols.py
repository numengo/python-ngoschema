# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict, MutableMapping
from functools import lru_cache

from ...utils import ReadOnlyChainMap as ChainMap
from ...decorators import memoized_property, log_exceptions
from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ...types.symbols import Function as Function_t, Class as Class_t, Module as Module_t, Symbol as Symbol_t
from .types import Type
from .collections import Object
from .variables import Variable, VariableValue


class Symbol(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/Symbol'

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value, **opts):
        from ngoinsp.inspectors.inspect_symbols import inspect_symbol
        data = inspect_symbol(value)
        return Symbol(data, **opts)


class Callable(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/Callable'
    _lazy_loading = True


class Argument(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Argument'

    def _convert(self, value, **opts):
        from ngoinsp.inspectors.doc_rest_parser import parse_docstring
        data = Variable._convert(self, value, **opts)
        doctype = data.pop('doctype', None)
        if doctype:
            data.update({k: v for k, v in parse_docstring(doctype).items() if v})
        return Object._convert(self, data, **opts)

    def json_schema(self):
        ret = Type.json_schema(self)
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
        from ngoinsp.inspectors.inspect_symbols import inspect_function
        data = inspect_function(value)
        return Function(data, **opts)

    @log_exceptions
    def json_schema(self):
        ret = Type.json_schema(self, excludes=['decorators', 'imports', 'symbol', 'module'])
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
        from ngoinsp.inspectors.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


class Descriptor(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/protocols/$defs/descriptors/$defs/Descriptor'
    _lazy_loading = True

    def __new__(cls, *args, **kwargs):
        data = args[0] if args else kwargs
        if 'ptype' in data:
            cls = PropertyDescriptor
        new = super(ObjectProtocol, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def json_schema(self):
        return True


class PropertyDescriptor(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/protocols/$defs/descriptors/$defs/PropertyDescriptor'
    _lazy_loading = True

    def json_schema(self):
        return self.ptype.json_schema() if hasattr(self, 'ptype') else True


class Method(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/classes/$defs/Method'
    _lazy_loading = True


class Class(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/classes/$defs/Class'
    _lazy_loading = True

    @memoized_property
    def _mro_classes(self):
        return [Class.inspect(m, context=self._context) for m in self.mro]

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value, with_functions=True, **opts):
        from ngoinsp.inspectors.inspect_symbols import inspect_class
        data = inspect_class(value, with_functions=with_functions)
        return Class(data, **opts)

    @memoized_property
    def _attributes(self):
        return {p.name: p for p in self.attributes}

    @memoized_property
    def _attributes_inherited(self):
        return ChainMap(self._attributes, *[m._attributes_inherited for m in self.mroClasses])

    @memoized_property
    def _descriptors(self):
        return {p.name: p for p in self.descriptors}

    @memoized_property
    def _descriptors_inherited(self):
        return ChainMap(self._descriptors, *[m._descriptors_inherited for m in self.mroClasses])

    @memoized_property
    def _methods(self):
        return {p.name: p for p in self.methods}

    @memoized_property
    def _methods_inherited(self):
        return ChainMap(self._methods, *[m._methods_inherited for m in self.mroClasses])

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
            mro = [m for m in self.mroClasses if isinstance(m.symbol, ObjectProtocol) or m.symbol.__module__ in self._ns_mgr]
            sch['extends'] = [m.schema_id() for m in mro]
            if not with_protected:
                for e in list(sch['extends']):
                    if e.rsplit('/', 1)[1][0] == '_':
                        sch['extends'].remove(e)
        if not isinstance(self.symbol, ObjectProtocol):
            sch['wraps'] = Symbol_t.serialize(self.symbol)
        sch.update({a.name: a.json_schema() or True for a in self.attributes if not a.name.startswith('__')})
        required = [k for k, d in self.descriptors_dict.items() if getattr(d, 'required', False)]
        if required:
            sch['required'] = required
        sch['properties'] = properties = {}
        for d in self.descriptors:
            sch['properties'][d.name] = d.json_schema()
        if self.init:
            for a in self.init.arguments:
                an = a.name
                if an in properties:
                    p = properties[an]
                    if isinstance(p, MutableMapping):
                        p.update(Type.json_schema(a))
                else:
                    properties[an] = Type.json_schema(a)
                properties[an] = properties[an] or True
        #properties.update({n: p.json_schema() or True for n, p in self.descriptors_dict.items() if not n.startswith('__')})
        #properties.update({d.name: d.json_schema() or True for d in self.descriptors if not d.name.startswith('__')})
        if not with_protected:
            to_remove = [k for k in sch['properties'].keys() if k[0] == '_']
            for k in to_remove:
                del sch['properties'][k]
        if not sch['properties']:
            del sch['properties']
        if 'required' in sch:
            sch['properties']['required'] = {'default': sch.pop('required')}
        return sch

    def schema_id(self):
        return getattr(self.symbol, '_id', None) or self._ns_mgr.get_cname_id(f'{self.module.__name__}.{self.symbol.__name__}')


class Module(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/modules/$defs/Module'

    @staticmethod
    @lru_cache(maxsize=128)
    def inspect(value, with_functions=True, **opts):
        from ngoinsp.inspectors.inspect_symbols import inspect_module
        data = inspect_module(value, with_functions=with_functions)
        return Module(data, **opts)

    def json_schema(self, with_modules=False, with_functions=False, with_protected=False):
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
        if not with_functions and 'functions' in sch['$defs']:
            del sch['$defs']['functions']
        if with_modules:
            for m in self.modules:
                if m.__name__.startswith(self.symbol.__name__):
                    mn = mm.name.split('.')[-1]
                    if not mn[0] == '_' or with_protected:
                        mm = Module.inspect(m, with_functions=False, context=self._context)
                        sch['$defs'][mn] = mm.json_schema(with_protected=with_protected,
                                                          with_functions=with_functions)
        if not sch['$defs']:
            del sch['$defs']
        return sch

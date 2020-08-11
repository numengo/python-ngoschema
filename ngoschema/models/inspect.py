# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from ..types import ObjectMetaclass, with_metaclass
from ..types.symbols import *


class Symbol(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/Symbol'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_importable
        return Importable(inspect_importable(value))


class VariableType(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/VariableType'

    @property
    def schema(self):
        t = self.type
        sch = {'type': t}
        if self.dimension != -1:
            sch['maxLength'] = self.dimension
        if self.items:
            sch['items'] = self.items.do_serialize(no_defaults=True)
        return sch


class Variable(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/Variable'


class VariableValue(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/VariableValue'


class Argument(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/functions/$defs/Argument'

    @classmethod
    def convert(cls, value, **opts):
        from ..inspect.doc_rest_parser import parse_docstring
        data = Variable.convert(value, **opts)
        doctype = data.pop('doctype', None)
        if doctype:
            data.update({k: v for k, v in parse_docstring(doctype).items() if v})
        return Object.convert(cls, data, **opts)


class Function(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/functions/$defs/Function'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_function
        return Function(inspect_function(value))

    def to_json_schema(self, ns):
        return self.do_serialize(no_defaults=True)


class FunctionCall(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/functions/$defs/FunctionCall'


    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


#class Class(with_metaclass(ObjectMetaclass, Importable)):
class Class(with_metaclass(ObjectMetaclass, Symbol)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/classes/$defs/Class'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_class
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
        sch = {'$id': self.schema_id(ns), 'type': 'object'}
        if self.description:
            sch['description'] = self.description
        if self.longDescription:
            sch['longDescription'] = self.longDescription
        if self.abstract:
            sch['abstract'] = True
        if self.mro:
            sch['extends'] = [m.schema_id(ns) for m in self.mro]
        sch['properties'] = {n: p.do_serialize(no_defaults=True) for n, p in self.propertiesInherited.items() if not n.startswith('__')}
        for k, v in sch['properties'].items():
            v.setdefault('type', 'string')
        sch['attributes'] = {n: p.do_serialize(no_defaults=True) for n, p in self.attributesInherited.items() if not n.startswith('__')}
        for k, v in sch['attributes'].items():
            v.setdefault('type', 'string')
        sch['methods'] = {n: p.do_serialize(no_defaults=True) for n, p in self.methodsInherited.items() if not n.startswith('__')}
        for k in ['properties', 'attributes', 'methods']:
            if not sch[k]:
                del sch[k]
        return sch

    def schema_id(self, ns):
        return getattr(self.symbol, '_schema_id', None) or ns.get_cname_id(f'{self.module.__name__}.{self.symbol.__name__}')


#class Definition(with_metaclass(ObjectMetaclass, Importable)):
class Definition(with_metaclass(ObjectMetaclass, Symbol)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/definitions/$defs/Definition'


#class Module(with_metaclass(ObjectMetaclass, Importable)):
class Module(with_metaclass(ObjectMetaclass, Symbol)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/modules/$defs/Module'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_module
        return Module(inspect_module(value))

    def to_json_schema(self, ns):
        sch = {'$id': self.schema_id(ns), 'type': 'object'}
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

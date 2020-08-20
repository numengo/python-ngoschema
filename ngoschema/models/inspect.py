# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from ..types import ObjectMetaclass, with_metaclass, ObjectProtocol, NamespaceManager
from ..types.symbols import *
from ..decorators import memoized_property, depend_on_prop


class Symbol(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/Symbol'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_importable
        return Importable(inspect_importable(value))


class Ref(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/types/$defs/Ref'

    def _make_context(self, context=None, *extra_contexts):
        ObjectProtocol._make_context(self, context, *extra_contexts)
        self._ns_mgr = next((m for m in self._context.maps_flattened if isinstance(m, NamespaceManager)), None)

    @depend_on_prop('$ref')
    def get_cname(self):
        ref = self._validated_data['$ref']
        if ref:
            return self._ns_mgr.get_id_cname(ref) if getattr(self, '_ns_mgr') else None
        return getattr(self, 'name', None)


class VariableType(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/types/$defs/VariableType'

    def _json_schema(self, cls=None):
        cls = cls or self.__class__
        if self.ref:
            return {'$ref': self.ref}
        elif self.booleanValue is not None:
            return self.booleanValue
        else:
            ret = {'type': self.type}
            if self.hasDefaultValue or self.defaultValueLiteral is not None:
                ret['default'] = self.defaultValueLiteral
            cps = list(cls._properties)
            extra = cls.serialize(self, only=cps, excludes=_vartyp_props, no_defaults=True)
            ret.update(extra)
        return ret

    @memoized_property
    def json_schema(self):
        return self._json_schema()


_vartyp_props = list(VariableType._properties)


class Variable(with_metaclass(ObjectMetaclass, VariableType)):
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


class FunctionCall(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/functions/$defs/FunctionCall'


    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


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
        sch = self._json_schema()
        return sch

    def schema_id(self, ns):
        return getattr(self.symbol, '_schema_id', None) or ns.get_cname_id(f'{self.module.__name__}.{self.symbol.__name__}')


class Definition(with_metaclass(ObjectMetaclass, Symbol)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/definitions/$defs/Definition'


class Module(with_metaclass(ObjectMetaclass, Symbol)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/modules/$defs/Module'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_module
        return Module(inspect_module(value))

    def to_json_schema(self, ns):
        sch = self._json_schema()
        return sch
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

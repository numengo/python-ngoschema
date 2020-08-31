# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ..protocols import ObjectMetaclass, with_metaclass, ObjectProtocol, ArrayProtocol
from ..managers import NamespaceManager, default_ns_manager
from ..types import String, Boolean, Object
from ..types import symbols
from ..decorators import memoized_property, depend_on_prop
from .metadata import NamedObject


class Symbol(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/Symbol'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_symbol
        return Symbol(inspect_symbol(value))


class Id(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/Id'
    _lazy_loading = False

    def _make_context(self, context=None, *extra_contexts):
        ObjectProtocol._make_context(self, context, *extra_contexts)
        self._ns_mgr = next((m for m in self._context.maps if isinstance(m, NamespaceManager)), None)
        self._ns_mgr = self._ns_mgr or default_ns_manager

    def set_ref(self, value):
        if value and '#' not in value:
            self._data['uri'] = value + '#'

    @depend_on_prop('uri')
    def get_canonicalName(self):
        ref = self._data_validated['uri']
        if ref:
            return self._ns_mgr.get_id_cname(ref) if getattr(self, '_ns_mgr') else None
        return getattr(self, 'name', None)


class VariableType(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/Type'

    def __init__(self, *args, **kwargs):
        data = args[0] if args else kwargs
        kwargs = kwargs if args else {}
        # check for items which are declared as arrays but given as named mappings
        if Object.check(data):
            for k, v in list(data.items()):
                raw, trans = self._properties_raw_trans(k)
                t = self.items_type(raw)
                if t.is_array() and Object.check(v):
                    del data[k] # remove previous entry in case it s an alias (eg $defs)
                    vs = []
                    for i, (n, d) in enumerate(v.items()):
                        d = {'booleanValue': d} if Boolean.check(d) else dict(d)
                        d['name'] = n
                        vs.append(d)
                    data[raw] = vs
        if String.check(data):
            data
        # transform a boolean input
        if Boolean.check(data):
            data = {'booleanValue': data}
        ObjectProtocol.__init__(self, **data, **kwargs)
        if self.defaultValue:
            self.hasDefault = True

    def _json_schema(self, cls=None, excludes=[], only=[], **opts):
        cls = cls or self.__class__
        if self.ref:
            return {'$ref': self.ref}
        elif self.booleanValue is not None:
            return self.booleanValue
        else:
            #ret = {'type': self.type}
            #if self.hasDefault:
            #    t = TypeChecker.get(self.type)
            #    ret['default'] = t.convert(self.defaultValue, convert=True, raw_literals=True)
            cps = set(cls._properties).difference(cls._not_validated).difference(cls._not_serialized)\
                     .difference(excludes).difference(['name', 'hasDefault', '_type']).union(['type', 'default', 'rawLiterals'])
            if only:
                cps = list(cps.intersection(only))
            else:
                cps = list(cps)
            ret = OrderedDict(cls.do_serialize(self, only=cps, no_defaults=True, **opts))
            ret.setdefault('type', self.type)
            if self.hasDefault:
                dft = self.defaultValue
                if hasattr(dft, 'do_serialize'):
                    dft = dft.do_serialize()
                ret['default'] = dft
            #if '_type' in ret:
            #    ret['type'] = ret.pop('_type')
            ret.move_to_end('type', False)
            if 'title' in ret:
                ret.move_to_end('title', False)
            return ret

    @memoized_property
    def json_schema(self):
        return self._json_schema()


_vartyp_props = list(VariableType._properties)


class Variable(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/Variable'


class VariableValue(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/variables/$defs/VariableValue'


class Argument(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Argument'

    def convert(self, value, **opts):
        from ..inspect.doc_rest_parser import parse_docstring
        data = Variable.convert(value, **opts)
        doctype = data.pop('doctype', None)
        if doctype:
            data.update({k: v for k, v in parse_docstring(doctype).items() if v})
        return Object.convert(self, data, **opts)


class Function(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/Function'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_function
        return Function(inspect_function(value))


class FunctionCall(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/functions/$defs/FunctionCall'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


class Definition(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/Definition'

    def _make_context(self, context=None, *extra_contexts):
        NamedObject._make_context(self, context, *extra_contexts)

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


class Class(with_metaclass(ObjectMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/classes/$defs/Class'

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

    def id(self, ns):
        return getattr(self.symbol, '_id', None) or ns.get_cname_id(f'{self.module.__name__}.{self.symbol.__name__}')


class Module(with_metaclass(ObjectMetaclass, Symbol)):
    _id = 'https://numengo.org/ngoschema#/$defs/symbols/$defs/modules/$defs/Module'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_module
        return Module(inspect_module(value))

    def to_json_schema(self, ns):
        sch = self._json_schema()
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

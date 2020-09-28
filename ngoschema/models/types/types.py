# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ...utils import ReadOnlyChainMap as ChainMap
from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol, ArrayProtocol, TypeProtocol
from ...managers import TypeBuilder
from ...types import String as String_t, Boolean as Boolean_t, Object as Object_t
from ...types import symbols
from ...relationships import ForeignKey
from ...resolver import resolve_uri
from ...decorators import memoized_property, depend_on_prop, log_exceptions
from ..metadata import NamedObject, IdentifiedObject, Annotation


class Type(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/Type'

    def _check(self, value, **opts):
        if not ObjectProtocol._check(self, value, **opts):
            # transform a boolean input
            if Boolean_t.check(value, convert=True):
                return True  # True or False are valid types
            if String_t.check(value):
                return True  # $ref
            return False
        return True

    def _convert(self, value, **opts):
        if Object_t.check(value):
            data = value.copy()
            data.pop('$schema', None)
            for k, v in list(data.items()):
                raw, trans = self._properties_raw_trans(k)
                t = self.item_type(raw)
                if t.is_array() and Object_t.check(v):
                    del data[k]  # remove previous entry in case it s an alias (eg $defs)
                    vs = []
                    for i, (n, d) in enumerate(v.items()):
                        d = {'booleanValue': d} if Boolean_t.check(d) else dict(d)
                        d['name'] = n
                        vs.append(d)
                    data[raw] = vs
        # transform a boolean input
        elif Boolean_t.check(value, convert=True):
            data = {'booleanValue': Boolean_t.convert(value)}
        elif String_t.check(value):
            data = {'$ref': value}
        return Object_t._convert(self, data, **opts)

    def __init__(self, *args, **kwargs):
        ObjectProtocol.__init__(self, *args, **kwargs)
        if self.defaultValue is not None and self.defaultValue != []:
            self.hasDefault = True

    #@log_exceptions
    #def json_schema(self, type_model=None, excludes=[], only=[], **opts):
    #    if self.ref:
    #        return {'$ref': self.serialize_item('$ref', context=self._context)}
    #    elif self.booleanValue is not None:
    #        return self.booleanValue
    #    else:
    #        cls = type_model or self.__class__
    #        cps = set(cls._properties).difference(cls._not_validated).difference(cls._not_serialized)\
    #            .difference(excludes).difference(['name', 'hasDefault', '_type', 'required'])\
    #            .union(['type', 'default', 'rawLiterals'])
    #        cps = list(cps.intersection(only)) if only else list(cps)
    #        ret = OrderedDict()
    #        for n in cps:
    #            p = self.get(n, None)
    #            t = self.item_type(n)
    #            if p is not None and p != t.default():
    #                if hasattr(p, 'json_schema'):
    #                    hasattr(p, 'json_schema')
    #                    ret[n] = p.json_schema()
    #                else:
    #                    ret[n] = self.serialize_item(n, no_defaults=True, **opts)
    #        if self.hasDefault:
    #            dft = self.defaultValue
    #            if hasattr(dft, 'do_serialize'):
    #                dft = dft.do_serialize()
    #            ret['default'] = dft
    #        ret.move_to_end('type', False)
    #        if ret['type'] == 'None':
    #            del ret['type']
    #        if 'description' in ret:
    #            ret.move_to_end('description', False)
    #        if 'title' in ret:
    #            ret.move_to_end('title', False)
    #        return ret

    @log_exceptions
    def json_schema(self, type_model=None, plain=False, excludes=[], **opts):
        if self.ref:
            return {'$ref': self.serialize_item('$ref', context=self._context)}
        elif self.booleanValue is not None:
            return self.booleanValue
        else:
            tm = type_model or NamedType
            opts['no_defaults'] = True
            excludes = tm._not_validated.union(tm._not_serialized).union(excludes).union(['name'])
            ks = [k for k in tm._properties_chained.reversed_keys() if k not in excludes]
            ret = OrderedDict()
            for k in ks:
                v = self[k]
                if v:
                    t = self.item_type(k)
                    if t.has_default() and v == t.default():
                        continue
                    if t.is_array() and issubclass(t._items, NamedType):
                        ret[k] = OrderedDict()
                        for vv in v:
                            ret[k][vv.name] = vv.json_schema(plain=plain, **opts)
                    else:
                        ret[k] = v.json_schema(plain=plain, **opts) if isinstance(v, Type) else self.serialize_item(k, **opts)
            if not self['type'] and 'type' in ret:
                del ret['type']
            for k1, k2 in self._aliases.items():
                if k2 in ret:
                    ret[k1] = ret.pop(k2)
            if plain:
                if self.is_primitive() and self.type not in ['boolean', 'number', 'integer', 'string']:
                    ret['type'] = 'string'
                extends = ret.pop('extends', [])
                properties = OrderedDict()
                from ...managers import TypeBuilder, scope
                for e in reversed(extends):
                    et = Type(resolve_uri(scope(e, self['$id'])))
                    es = et.json_schema(plain=True, **opts)
                    properties.update(es.get('properties'), {})
                properties.update(ret.pop('properties', {}))
                if properties:
                    ret['properties'] = properties
            return ret

    def build_type(self):
        id = self['$id']
        schema = None if id and TypeBuilder.contains(id) else self.json_schema()
        return TypeBuilder.build(id, schema=schema)


class Primitive(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/Primitive'


class NamedType(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/NamedType'


class Boolean(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/boolean/$defs/Boolean'


class Number(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/numerics/$defs/Number'


class Integer(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/numerics/$defs/Integer'



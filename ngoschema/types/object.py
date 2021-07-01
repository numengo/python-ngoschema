# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict, defaultdict, Mapping, MutableMapping
import re
from operator import neg

from ..exceptions import InvalidValue
from ..decorators import log_exceptions
from ..utils import ReadOnlyChainMap as ChainMap, shorten
from ..managers.type_builder import register_type, type_builder, untype_schema
from ..protocols.serializer import Serializer
from .constants import _True, _False
from .type import Type
from .strings import Pattern
from .collection import CollectionDeserializer, CollectionSerializer, Collection


class ObjectDeserializer(CollectionDeserializer):
    _collType = OrderedDict

    _required = set()

    def __init__(self, required=None, **opts):
        CollectionDeserializer.__init__(self, **opts)
        self._required = self._required.union(required or [])

    @staticmethod
    def _call_order(self, value, dependencies=None, **opts):
        """Generate a call order according to schema dependencies and inputs detected in values."""
        from ..utils import topological_sort
        # order call according to dependencies
        for i in self._required:
            yield i
        unordered = set(value or {}).difference(self._required)
        # create dependency dictionary from class definition and values inputs
        dependencies = dependencies or {}
        if unordered:
            for level in topological_sort(dependencies):
                in_level = level.intersection(unordered)
                unordered.difference_update(in_level)
                for i in in_level:
                    yield i
            for i in unordered:
                yield i

    @staticmethod
    def _check(self, value, **opts):
        if not isinstance(value, Mapping):
            raise TypeError('%s is not of type mapping.' % value)
        #value = self._collType(value)
        return value

    @staticmethod
    def _convert(self, value, **opts):
        value = self._collType([(k, value.get(k)) for k in self._call_order(self, value, **opts)])
        return CollectionDeserializer._convert(self, value, **opts)

    @staticmethod
    def _validate(self, value, **opts):
        missing = self._required.difference(value)
        if missing:
            raise InvalidValue('%s is missing required keys %s.' % (shorten(value), list(missing)))
        return CollectionDeserializer._validate(self, value, **opts)


class ObjectSerializer(CollectionSerializer, ObjectDeserializer):
    _deserializer = ObjectDeserializer

    _readOnly = set()
    _noDefaults = True
    _noReadOnly = False

    def __init__(self, readOnly=None, attrPrefix='', noDefaults=True, noReadOnly=False, **opts):
        CollectionSerializer.__init__(self, **opts)
        self._readOnly = self._readOnly.union(readOnly or [])
        self._attrPrefix = attrPrefix
        self._noDefaults = noDefaults
        self._noReadOnly = noReadOnly

    @staticmethod
    def _print_order(self, value, excludes=[], only=[], **opts):
        """Generate a print order according to schema and inherited schemas properties order
        and additonal properties detected in values. """
        keys = set((value or {}).keys())
        all_ordered = list(keys.intersection(self._required))
        all_ordered += list(keys.difference(all_ordered))
        no_defaults = opts.get('no_defaults', self._noDefaults)
        no_readOnly = opts.get('no_readOnly', self._noReadOnly)
        if no_readOnly:
            excludes += list(self._readOnly)
        for k in all_ordered:
            if k in self._required:
                yield k
            elif ObjectSerializer._is_included(k, value, excludes=excludes, only=only, no_defaults=no_defaults):
                yield k

    @staticmethod
    def _serialize(self, value, **opts):
        value = CollectionSerializer._serialize(self, value, **opts)
        return self._collType([(k, value.get(k)) for k in self._print_order(self, value, **opts)])


@register_type('object')
class Object(Collection, ObjectSerializer):
    _pyType = OrderedDict
    _serializer = ObjectSerializer
    _deserializer = ObjectDeserializer
    _default = OrderedDict()

    _attrPrefix = ''
    _properties = OrderedDict()
    _propertiesPattern = set()
    _propertiesAdditional = _True()
    _propertiesWithDefault = set()

    @classmethod
    def is_object(cls):
        return True

    def __init__(self,
                 properties=None,
                 patternProperties=None,
                 additionalProperties=None,
                 **opts):
        # split the schema to isolate properties schema and object schema
        Collection.__init__(self, **opts)
        cls_name = f'{self.__class__.__name__}_{id(self)}'
        if properties:
            ps = OrderedDict(self._properties)
            properties = untype_schema(properties)
            ps.update(OrderedDict([(name, type_builder.build(f'{cls_name}/properties/{name}', sch))
                                   for name, sch in properties.items()]))
            self._properties = ps
        if patternProperties:
            pps = set(self.patternProperties)
            pps.update([(re.compile(k), type_builder.build(
                f'{cls_name}/patternProperties/{k}', v)) for k, v in patternProperties.items()])
            self._propertiesPattern = pps
        if additionalProperties is not None:
            self._propertiesAdditional = type_builder.build(f'{cls_name}/additionalProperties', additionalProperties)
        self._propertiesWithDefault = set(k for k, t in self._properties.items() if t.has_default())
        self._required.difference_update(self._propertiesWithDefault)
        self._items_type_cache = {}

    def __call__(self, value=None, **opts):
        value = value or opts  # to allow initialization by keywords
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        return Type.__call__(self, value, **opts)

    @staticmethod
    def _items_types(self, value, **opts):
        return [(k, self._items_type(self, k)) for k in list(value)]

    @staticmethod
    def _items_type(self, item):
        """Returns the type of a property by its name."""
        pt = self._items_type_cache.get(item)
        if pt:
            return pt
        pt = self._properties.get(item)
        if pt is not None:
            self._items_type_cache[item] = pt
            return pt
        for reg, t in self._propertiesPattern:
            if reg.search(item):
                self._items_type_cache[item] = t
                return t
        if self._propertiesAdditional:
            self._items_type_cache[item] = self._propertiesAdditional
            return self._propertiesAdditional
        raise KeyError(item)

    @staticmethod
    def _repr_schema(self):
        self._sch_repr = sch_repr = Type._repr_schema(self)
        sch_repr['type'] = 'object'
        if self._required:
            sch_repr['required'] = list(self._required)
        if self._readOnly:
            sch_repr['readOnly'] = list(self._readOnly)
        if self._properties:
            sch_repr['properties'] = {k: t.repr_schema() for k, t in self._properties.items()}
        if self._propertiesPattern:
            sch_repr['patternProperties'] = {k: t.repr_schema() for k, t in list(self._propertiesPattern)}
        if not self._propertiesAdditional:
            sch_repr['additionalProperties'] = False
        return sch_repr

    def default(self, value=None, **opts):
        ret = self._collType(value or self._default)
        for k in list(self._propertiesWithDefault):
            t = self._items_type(self, k)
            v = ret.get(k)
            ret[k] = t.default(**opts) if v is None else v
        #opts['items'] = False
        return self._serialize(self, ret, **opts)

    @staticmethod
    def _null(self, value, items=False, **opts):
        return self._collType([(k, None) for k in self._print_order(self, value, items=items, **opts)])

    @staticmethod
    def _deserialize(self, value, items=True, evaluate=True, raw_literals=False, **opts):
        value = self._collType(value or self._default)
        #value = ObjectDeserializer._deserialize(self, value, items=False, evaluate=evaluate, **opts)
        value.update({k: self._items_type(self, k).default(raw_literals=True, evaluate=evaluate, **opts)
                      for k in self._propertiesWithDefault if k not in value})
        value.update({k: None for k in self._properties.keys() if k not in value})
        value = self._collType([(k, value[k]) for k in self._call_order(self, value, items=items, **opts)])
        value = Collection._deserialize(self, value, items=items, evaluate=evaluate, raw_literals=raw_literals, **opts)
        return value

    @staticmethod
    def _validate(self, value, items=True, excludes=[], **opts):
        excludes = list(excludes) + ['required', 'properties', 'propertiesAdditional', 'additionalProperties']
        #value = self._deserializer._validate(self, value, excludes=excludes, **opts)
        for k in set(value).difference(self._properties):
           for reg, _ in self._propertiesPattern:
               if reg.search(k):
                   break
           else:
               if not self._propertiesAdditional:
                   raise InvalidValue('No additional properties allowed for %s' % value)
        opts['with_type'] = False
        value = Collection._validate(self, value, items=items, excludes=excludes, **opts)
        return value

    @staticmethod
    def _inputs(self, value, items=False, **opts):
        inputs = set(self._required)
        if value is None:
            if self.has_default():
                inputs = self._inputs(self, self.default(raw_literals=True), items=items, **opts)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    inputs.update(ChainMap(*[set([f'{k}.{i}' for i in t._inputs(t, value[k], **opts)]) for k in value.keys()]))
        return inputs

    @staticmethod
    def _print_order(self, value, **opts):
        no_defaults = opts.pop('no_defaults', self._noDefaults)
        context = opts.pop('context', self._context)
        for k in ObjectSerializer._print_order(self, value, no_defaults=no_defaults, **opts):
            if no_defaults:
                t = self._items_type(self, k)
                v = value[k]
                if t._has_default(t):
                    d = t.default(context=context, raw_literals=True)
                    d = t(d, context=context)
                    v = neg(v) if k in self._aliasesNegated else v
                    #if t.is_primitive():
                    #    #d = t.serialize(d, raw_literals=True)
                    #    #if Pattern.check(d) and v == t.evaluate(d, context=context):
                    #    #    continue
                    if v == d:
                        continue
            yield k

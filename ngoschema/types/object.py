# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict, defaultdict, Mapping, MutableMapping
import re
from operator import neg

from ..exceptions import InvalidValue
from ..decorators import log_exceptions
from ..utils import ReadOnlyChainMap as ChainMap
from ..managers.type_builder import register_type, TypeBuilder, untype_schema
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
        value = self._collType(value)
        return value

    #@staticmethod
    #def _deserialize(self, value, **opts):
    #    value = CollectionDeserializer._deserialize(self, value, **opts)
    #    for k in self._required:
    #        value.setdefault(k, None)
    #    return value

    @staticmethod
    def _convert(self, value, **opts):
        value = self._collType([(k, value.get(k)) for k in self._call_order(self, value, **opts)])
        return CollectionDeserializer._convert(self, value, **opts)

    @staticmethod
    def _validate(self, value, **opts):
        missing = self._required.difference(value)
        if missing:
            raise InvalidValue('%s is missing required keys %s.' % (value, list(missing)))
        return CollectionDeserializer._validate(self, value, **opts)


class ObjectSerializer(CollectionSerializer, ObjectDeserializer):
    _deserializer = ObjectDeserializer

    _readOnly = set()
    _noDefaults = True
    _noReadOnly = False

    def __init__(self, readOnly=None, attrPrefix='', noDefaults=True, noReadOnly=False, **opts):
        #ObjectDeserializer.__init__(self, required=required, **opts)
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
        no_read_only = opts.get('no_read_only', self._noReadOnly)
        if no_read_only:
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
    _patternProperties = set()
    _additionalProperties = _True()
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
        #ObjectSerializer.__init__(self, required=required, **opts)
        Collection.__init__(self, **opts)
        cls_name = f'{self.__class__.__name__}_{id(self)}'
        if properties:
            ps = OrderedDict(self._properties)
            properties = untype_schema(properties)
            ps.update(OrderedDict([(name, TypeBuilder.build(f'{cls_name}/properties/{name}', sch))
                                   for name, sch in properties.items()]))
            self._properties = ps
        if patternProperties:
            pps = set(self.patternProperties)
            pps.update([(re.compile(k), TypeBuilder.build(
                f'{cls_name}/patternProperties/{k}', v)) for k, v in patternProperties.items()])
            self._patternProperties = pps
        if additionalProperties is not None:
            self._additionalProperties = TypeBuilder.build(f'{cls_name}/additionalProperties', additionalProperties)
        self._propertiesWithDefault = set(k for k, t in self._properties.items() if t.has_default())
        self._required.difference_update(self._propertiesWithDefault)
        self._items_type_cache = {}

    def __call__(self, value=None, **opts):
        value = value or opts  # to allow initialization by keywords
        opts['context'] = self.create_context(**opts)
        return self._serialize(self, value, **opts)

    @staticmethod
    def _items_types(self, value, **opts):
        return [(k, self._items_type(self, k)) for k in list(value)]

    @staticmethod
    def _items_type(self, item):
        """Returns the type of a property by its name."""
        if self._items_type_cache is None:
            self._items_type_cache = {}
        pt = self._items_type_cache.get(item)
        if pt:
            return pt
        pt = self._properties.get(item)
        if pt is not None:
            self._items_type_cache[item] = pt
            return pt
        for reg, t in self._patternProperties:
            if reg.search(item):
                self._items_type_cache[item] = t
                return t
        if self._additionalProperties:
            self._items_type_cache[item] = self._additionalProperties
            return self._additionalProperties
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
        if self._patternProperties:
            sch_repr['patternProperties'] = {k: t.repr_schema() for k, t in list(self._patternProperties)}
        if not self._additionalProperties:
            sch_repr['additionalProperties'] = False
        return sch_repr

    def default(self, value=None, **opts):
        value = value or self._default
        ret = {k: None for k in value.keys()}
        for k, t in list(self._propertiesWithDefault):
            t = self._items_type(self, k)
            ret[k] = t.default(**opts) if t.has_default() else None
        opts['items'] = False
        return self._serialize(self, ret, **opts)

    #@staticmethod
    #def _check(self, value, items=True, **opts):
    #    value = self._deserializer._check(self, value, **opts)
    #    value = Collection._check(self, value, items=items, **opts)
    #    return value

    #@staticmethod
    #def _convert(self, value, items=True, **opts):
    #    value = ObjectDeserializer._convert(self, value, **opts)
    #    value = Collection._convert(self, value, items=items, **opts)
    #    return value

    @staticmethod
    def _deserialize(self, value, items=True, evaluate=True, raw_literals=False, **opts):
        value = self._collType(value or self._default)
        #value = ObjectDeserializer._deserialize(self, value, items=False, evaluate=evaluate, **opts)
        value.update({k: self._items_type(self, k).default(raw_literals=True, **opts)
                      for k in self._propertiesWithDefault if k not in value})
        value.update({k: None for k in self._properties.keys() if k not in value})
        value = self._collType([(k, value[k]) for k in self._call_order(self, value, items=items, **opts)])
        value = Collection._deserialize(self, value, items=items, evaluate=evaluate, raw_literals=raw_literals, **opts)
        return value

    #    for k in self._call_order(value, items=items, **opts):
    #        try:
    #            t = Object._items_type(self, k)
    #            v = value.get(k)
    #            # initialize default even if items is not selected
    #            if not items and v is None and (t.has_default() or k in self._required):
    #                v = t.default(raw_literals=True, **opts)
    #            value[k] = v if not items else t.deserialize(v, **opts)
    #        except Exception as er:
    #            raise
    #    return value

    #def _default(self, **opts):
    #    if self._default_cache is None:
    #        opts.setdefault('items', False)
    #        opts.setdefault('rawLiterals', False)
    #        self._default_cache = Object._convert(self, self._schema.get('default', {}), **opts)
    #    return self._default_cache

    #@classmethod
    #def default(cls, **opts):
    #    return Object._default(cls, **opts)

    #def _check(self, value, items=True, **opts):
    #    if not isinstance(value, Mapping):
    #        raise TypeError('%s is not of type mapping.' % value)
    #    return Collection._check(self, value, **opts)
    #    #keys = set(value)
    #    #if self._required.difference(keys).difference(self._propertiesWithDefault):
    #    #    return False
    #    #for k in keys.difference(self._properties):
    #    #    for reg, _ in self._patternProperties:
    #    #        if reg.search(k):
    #    #            break
    #    #    else:
    #    #        if not self._additionalProperties:
    #    #            return False
    #    #if items:
    #    #    for k, v in value.items():
    #    #        if not Object._items_type(self, k).check(v):
    #    #            return False
    #    #return True

    @staticmethod
    def _validate(self, value, items=True, excludes=[], **opts):
        excludes = list(excludes) + ['required', 'properties', 'propertiesAdditional', 'additionalProperties']
        #value = self._deserializer._validate(self, value, excludes=excludes, **opts)
        for k in set(value).difference(self._properties):
           for reg, _ in self._patternProperties:
               if reg.search(k):
                   break
           else:
               if not self._additionalProperties:
                   raise InvalidValue('No additional properties allowed for %s' % value)
        opts['with_type'] = False
        value = Collection._validate(self, value, items=items, excludes=excludes, **opts)
        return value

    #def _items_inputs(self, item, value, **opts):
    #    v = value[item]
    #    try:
    #        i = set() if not v else Object._items_type(self, item).inputs(v, **opts)
    #    except Exception as er:
    #        self._logger.error(f'{item} {str(v)[:40]}...: {str(er)}', exc_info=True)
    #        raise er
    #    return i.union(self._dependencies.get(item, []))

    #def _inputs(self, value, items=False, **opts):
    #    """
    #    Create object dependency tree according to class declared dependencies and expression inputs.
    #    Make all property names raw and keep only first level
    #    """
    #    inputs = set(self._required)
    #    if value is None:
    #        if self.has_default():
    #            return self.inputs(self.default(raw_literals=True), items=items, **opts)
    #    if items:
    #        inputs.update(ChainMap(*[set([f'{k}.{i}' for i in Object._items_inputs(self, k, value, **opts)])
    #                                 for k in value.keys()]))
    #    return inputs

    #@staticmethod
    #def _call_order(self, value, **opts):
    #    value = set(value).union(self._properties)
    #    return ObjectDeserializer._call_order(self, value, **opts)

    #    dependencies = defaultdict(set, **self._dependencies)
    #    if items:
    #        # make a local copy
    #        for k, v in value.items():
    #            t = self.items_type(k)
    #            if v is None and t.has_default():
    #                v = t.default(raw_literals=True, **opts)
    #            inputs = [i.split('.')[0] for i in t.inputs(v)] if v else []
    #            dependencies[k].update([i for i in inputs if i in self._properties])
    #    return Collection._call_order(self, value, dependencies=dependencies, **opts)
    #    return ObjectDeserializer._call_order(self, value, dependencies=dependencies, **opts)

    #def _serialize(self, value, deserialize=True, **opts):
    #    value = self._deserialize(value, **opts) if deserialize else value
    #    # separate excludes/only from opts as they apply to the first component and might be applied to its properties
    #    no_defaults = opts.get('no_defaults', self._noDefaults)
    #    attr_prefix = opts.get('attr_prefix', self._attrPrefix)
    #    ptypes = [(k, Object._items_type(self, k))
    #              for k in ObjectSerializer._print_order(self, value, **opts)]
    #    try:
    #        ret = OrderedDict([((attr_prefix if t.is_primitive() else '') + k,
    #                             t.serialize(value[k], **opts))
    #                             for k, t in ptypes])
    #    except Exception as er:
    #        self._logger.error(er, exc_info=True)
    #        raise er
    #    return ret if not no_defaults else OrderedDict([(k, v) for k, v in ret.items() if v is not None])

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
        context = self.create_context(**opts)
        for k in ObjectSerializer._print_order(self, value, no_defaults=no_defaults, **opts):
            if no_defaults:
                t = self._items_type(self, k)
                v = value[k]
                if t._has_default(t):
                    d = t.default(context=context, raw_literals=True)
                    v = neg(v) if k in self._aliasNegated else v
                    if v == d:
                        continue
                    if t.is_primitive():
                        d = t.serialize(d, raw_literals=True)
                        if Pattern.check(d) and v == t.evaluate(d, context=context):
                            continue
            yield k

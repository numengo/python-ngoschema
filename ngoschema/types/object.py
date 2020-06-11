# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict, defaultdict, Mapping
import re

from ..decorators import memoized_method
from ..utils import ReadOnlyChainMap as ChainMap
from .type import Type, TypeChecker
from .null import _True, _False
from .type import Type
from .array import Array
from .literals import Literal, Expr


@TypeChecker.register('object')
class Object(Type):
    _schema = {'type': 'object'}
    _py_type = OrderedDict
    _properties = OrderedDict()
    _pattern_properties = set()
    _additional_properties = _True()
    _dependencies = {}
    _extends = []
    #_outputs = {}
    _required = set()
    _read_only = set()
    _not_serialized = set()
    _has_default = set()
    _properties_translation = {}

    def __init__(self, **schema):
        # split the schema to isolate properties schema and object schema
        from .type_builder import TypeBuilder
        Type.__init__(self, **schema)
        mro_schemas = self._schema._maps
        schema = self._schema._maps[0]
        self._dependencies = defaultdict(set, **ChainMap(*[s.get('dependencies', {}) for s in mro_schemas]))
        self._extends = sum([s.get('extends', []) for s in mro_schemas], [])
        self._not_serialized = set().union(*[s.get('notSerialized', {}) for s in mro_schemas])
        self._required = set().union(*[s.get('required', {}) for s in mro_schemas])
        self._read_only = set().union(*[s.get('readOnly', {}) for s in mro_schemas])
        if self._extends:
            schema['extends'] = self._extends
        if self._dependencies:
            schema['dependencies'] = self._dependencies
        if self._not_serialized:
            schema['notSerialized'] = self._not_serialized
        if self._required:
            schema['required'] = self._required
        if self._read_only:
            schema['readOnly'] = self._read_only

        cls_name = self.__class__.__name__
        schema['properties'] = ChainMap(*[s.get('properties', {}) for s in mro_schemas])
        self._properties = OrderedDict([(name, Type.build(f'{cls_name}/properties/{name}', sch)())
                                         for name, sch in schema.get('properties', {}).items()])
        pattern_properties = ChainMap(*[s.get('patternProperties', {}) for s in mro_schemas])
        self._pattern_properties = set([(re.compile(k), Type.build(
            f'{cls_name}/patternProperties/{k}', v)()) for k, v in pattern_properties.items()])
        ap = schema.get('additionalProperties', True)
        if ap:
            self._additional_properties = _True() if ap is True else Type.build(f'{cls_name}/additionalProperties', ap)()
        else:
            self._additional_properties = _False()
        self._has_default = set(k for k, t in self._properties.items() if t.has_default())
        self._required.difference_update(self._has_default)

    def __call__(self, *args, validate=True, convert=True, context=None, **kwargs):
        assert len(args) <= 1
        opts = kwargs if len(args) == 1 else {}
        data = args[0] if args else kwargs
        context = Type._make_context(self, context, opts)
        data = Object._convert(self, data, context=context, convert=convert, **opts)
        if validate:
            self.validate(data)
        return data

    @classmethod
    def check(cls, value, **opts):
        return isinstance(value, Mapping)

    def convert(self, value, **opts):
        return Object._convert(self, value, **opts)

    def _convert(self, value, convert=True, **opts):
        #ret = Type._convert(Object, value, **opts)
        ret = OrderedDict((k, None) for k in Object.call_order(self, value, with_inputs=convert))
        for k in ret.keys():
            t = self._property_type(k)
            v = value.get(k)
            if v is None:
                for trans, raw in self._properties_translation.items():
                    if k == raw:
                        v = value.get(trans)
                        break
            if v is None and t.has_default():
                v = t.default()
            ret[k] = v if not convert else t(v, **opts)
        return ret

    def validate(self, value, excludes=[], as_dict=False, **opts):
        errors = {}
        try:
            if 'properties' not in excludes:
                for k in Object.call_order(self, value, with_inputs=True):
                    if k not in excludes and value.get(k) is not None:
                        errors.update(self._property_type(k).validate(value[k], excludes=[], as_dict=True))
            errors.update(Type.validate(self, value, excludes=excludes+['properties', 'patternProperties', 'additionalProperties'], as_dict=True, **opts))
        except Exception as er:
            raise er
        return errors if as_dict else self._format_error(value, errors)

    def serialize(self, value, attr_prefix='', **opts):
        no_defaults = opts.get('no_defaults', False)
        ptypes = [(k, self._property_type(k)) for k in Object.print_order(self, value)]
        ret = OrderedDict([((attr_prefix if t.is_literal() else '') + k,
                             t.serialize(value[k], attr_prefix=attr_prefix, **opts))
                             for k, t in ptypes])
        return ret if not no_defaults else OrderedDict([(k, v) for k, v in ret.items() if v is not None])

    @classmethod
    def inputs(cls, value, **opts):
        return Object._inputs(cls, value, **opts)

    def _inputs(self, value, key=None, with_inner=False, **opts):
        """
        Create object dependency tree according to class declared dependencies and expression inputs.
        Make all property names raw and keep only first level
        """
        value = value if value is not None else self.default()
        if key is not None:
            try:
                return self._property_type(key).inputs(value.get(key), **opts).union(self._dependencies.get(key, []))
            except Exception as er:
                self._logger.error('%s %s' % (key, value))
                raise er
        if with_inner:
            return ChainMap(*[set([f'{k}.{i}' for i in Object._inputs(self, value, k, with_inner=False, **opts)]) for k in value.keys()])
        return set()

    def call_order(self, value, with_inputs=True):
        """Generate a call order according to schema dependencies and inputs detected in values."""
        from .object_protocol import ObjectProtocol
        if isinstance(value, ObjectProtocol) and isinstance(value, self._py_type):
            for k in value.keys():
                yield k
        else:
            # order call according to dependencies
            unordered = set(value or {})
            to_untranslate = unordered.intersection(self._properties_translation)
            # replace translated keys
            unordered = unordered.union(self._properties)
            from ..utils import topological_sort
            # create dependency dictionary from class definition and values inputs
            deps = self._dependencies
            if with_inputs:
                # make a local copy
                deps = defaultdict(set, **self._dependencies)
                for k in unordered:
                    v = value.get(k)
                    if k in to_untranslate:
                        k = self._properties_translation.get(k)
                    t = self._property_type(k)
                    if v is None and t.has_default():
                        v = t.default()
                    inputs = [i.split('.')[0] for i in t.inputs(v)] if v else []
                    deps[k].update([i for i in inputs if i in self._properties])
            unordered = unordered.difference(to_untranslate).union([self._properties_translation.get(k) for k in to_untranslate])
            if unordered:
                for level in topological_sort(deps):
                    in_level = level.intersection(unordered)
                    unordered.difference_update(in_level)
                    for i in in_level:
                        yield i
                for i in unordered:
                    yield i

    def print_order(self, value, excludes=[], only=[], no_defaults=False, no_read_only=False, **opts):
        """Generate a print order according to schema and inherited schemas properties order
        and additonal properties detected in values.

        Various options allow to filter results:
        :param excludes: keys to exclude
        :param only: list of the only keys to return
        :param no_defaults: removes values equal to their default
        """
        keys = set(value.keys())
        all_ordered = [k for k in self._properties.keys() if k in keys]
        all_ordered += list(keys.difference(all_ordered))
        ns = self._not_serialized
        ro = self._read_only
        rq = self._required
        for k in all_ordered:
            if k in ns.union(excludes):
                continue
            if no_read_only and k in ro:
                continue
            if only and k not in only:
                continue
            if k in rq:
                yield k
            if k not in value:
                continue
            if no_defaults:
                v = value.get(k)
                if v is None:
                    continue
                t = self._property_type(k)
                if t.has_default() and v == t.default():
                    continue
            yield k

    #@classmethod
    #def has_default(cls):
    #    return True

    def default(self):
        dft = Type.default(self)
        ret = OrderedDict((k, None) for k in Object.call_order(self, dft))
        for k in ret.keys():
            v = dft.get(k)
            if v is None:
                t = self._property_type(k)
                v = t.default() if t.has_default() else None
            ret[k] = v
        return ret

    def _property_type(self, name):
        """Returns the type of a property by its name."""
        pt = self._properties.get(name)
        if pt is not None:
            return pt
        for reg, t in self._pattern_properties:
            if reg.search(name):
                return t
        if self._additional_properties:
            return self._additional_properties
        raise KeyError(name)

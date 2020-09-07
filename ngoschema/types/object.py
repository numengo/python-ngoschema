# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict, defaultdict, Mapping
import re
from operator import neg

from ..exceptions import InvalidValue
from ..decorators import log_exceptions
from ..utils import ReadOnlyChainMap as ChainMap
from .type import Type, TypeProtocol
from ..managers.type_builder import register_type, TypeBuilder
from .constants import _True, _False
from .array import Array
from .strings import Pattern


@register_type('object')
class Object(Type):
    _py_type = OrderedDict
    _coll_type = OrderedDict
    _properties = OrderedDict()
    _properties_pattern = set()
    _properties_allowed = set()
    _properties_additional = _True
    _required = set()
    _read_only = set()
    _not_serialized = set()
    _not_validated = set()
    _properties_with_default = set()
    _properties_translation = {}
    _aliases = {}
    _aliases_negated = {}

    def __init__(self, **schema):
        # split the schema to isolate properties schema and object schema
        Type.__init__(self, **schema)
        mro_schemas = self._schema_chained._maps
        schema = self._schema_chained._maps[0]
        self._dependencies = defaultdict(set)
        for k, v in ChainMap(*[s.get('dependencies', {}) for s in mro_schemas]).items():
            self._dependencies[k].update(set(v))
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
        # by modifying the first schema of the chained schema, we need to regenerate _schema (computed in Type.__init__)
        self._schema = dict(self._schema_chained)

        cls_name = f'{self.__class__.__name__}_{id(self)}'
        schema['properties'] = ChainMap(*[s.get('properties', {}) for s in mro_schemas])
        self._properties_chained = schema['properties']
        self._properties = OrderedDict([(name, TypeBuilder.build(f'{cls_name}/properties/{name}', sch))
                                         for name, sch in schema.get('properties', {}).items()])
        pattern_properties = ChainMap(*[s.get('patternProperties', {}) for s in mro_schemas])
        self._properties_pattern = set([(re.compile(k), TypeBuilder.build(
            f'{cls_name}/patternProperties/{k}', v)) for k, v in pattern_properties.items()])
        self._properties_additional = TypeBuilder.build(f'{cls_name}/additionalProperties', schema.get('additionalProperties', True))
        self._properties_allowed = set(self._properties_chained)
        self._properties_with_default = set(k for k, t in self._properties.items() if t.has_default())
        self._required.difference_update(self._properties_with_default)

    @classmethod
    def is_object(cls):
        return True

    def _repr_schema(self):
        if self._sch_repr is None:
            self._sch_repr = sch_repr = TypeProtocol._repr_schema(self)
            sch_repr['type'] = 'object'
            sch_repr['properties'] = {}
            for k in Object.print_order(self, self._schema.get('properties', {}), no_read_only=True):
                sch_repr['properties'][k] = self._schema['properties'].get('type')
            if self._schema.get('additionalProperties', False):
                sch_repr['additionalProperties'] = True
        return self._sch_repr

    def _evaluate(self, *args, **kwargs):
        kwargs.pop('$schema', None)
        value = args[0] if args else kwargs
        opts = kwargs if args else {}
        opts.setdefault('items', True)
        return Type._evaluate(self, value, **opts)

    def _default(self, **opts):
        if self._default_cache is None:
            opts.setdefault('items', False)
            opts.setdefault('raw_literals', False)
            self._default_cache = Object._convert(self, self._schema.get('default', {}), **opts)
        return self._default_cache

    def _check(self, value, **opts):
        if not isinstance(value, Mapping):
            return False
        keys = set(value.keys())
        if self._required.difference(keys):
            return False
        for k in keys.difference(self._properties_allowed):
            for reg, _ in self._properties_pattern:
                if reg.search(k):
                    break
            else:
                if not self._properties_additional:
                    return False
        return True

    def _convert(self, value, items=False, **opts):
        avs = {k2: value[k1] for k1, k2 in self._aliases.items() if k1 in value}
        navs = {k2: - value[k1] for k1, k2 in self._aliases_negated.items() if k1 in value}
        ret = OrderedDict((k, None) for k in Object._call_order(self, value, with_inputs=items, **opts))
        raw_literals = opts.pop('raw_literals', False)
        for k in ret.keys():
            try:
                t = Object.items_type(self, k)
                v = value.get(k, avs.get(k, navs.get(k)))
                # initialize default even if items is not selected
                if not items and v is None and (t.has_default() or k in self._required):
                    v = t.default(raw_literals=True, **opts)
                ret[k] = v if not items else t.evaluate(v, raw_literals=raw_literals, **opts)
            except Exception as er:
                raise
        return self._coll_type(ret)

    def _do_validate(self, value, items=True, excludes=[], as_dict=False, **opts):
        errors = {}
        try:
            if items:
                for k in Object._call_order(self, value, with_inputs=True):
                    if k not in self._not_validated and k not in excludes and value.get(k) is not None:
                        t = Object.items_type(self, k)
                        errors.update(t.validate(value[k], **opts, as_dict=True))
            errors.update(TypeProtocol._do_validate(self, value, excludes=excludes+['properties', 'patternProperties', 'additionalProperties'], as_dict=True, **opts))
        except Exception as er:
            raise er
        return errors if as_dict else self._format_error(value, errors)

    def _serialize(self, value, attr_prefix='', **opts):
        # separate excludes/only from opts as they apply to the first component and might be applied to its properties
        no_defaults = opts.get('no_defaults', False)
        opts.setdefault('context', getattr(value, '_context', self._context))  # should we even use the value context?
        ptypes = [(k, Object.items_type(self, k)) for k in Object._print_order(self, value, **opts)]
        try:
            ret = OrderedDict([((attr_prefix if t.is_primitive() else '') + k,
                                 t.serialize(value[k], attr_prefix=attr_prefix, **opts))
                                 for k, t in ptypes])
        except Exception as er:
            raise er
        return ret if not no_defaults else OrderedDict([(k, v) for k, v in ret.items() if v is not None])

    def _inputs(self, value, item=None, with_inner=False, **opts):
        """
        Create object dependency tree according to class declared dependencies and expression inputs.
        Make all property names raw and keep only first level
        """
        if value is None:
            if self.has_default():
                return self._inputs(self.default(raw_literals=True), item, with_inner, **opts)
            return set()
        if item is not None:
            v = value[item]
            try:
                i = set() if not v else Object.items_type(self, item).inputs(v, **opts)
            except Exception as er:
                self._logger.error(f'{item} {str(v)[:40]}...: {str(er)}', exc_info=True)
                raise er
            return i.union(self._dependencies.get(item, []))
        if with_inner:
            return ChainMap(*[set([f'{k}.{i}' for i in Object._inputs(self, value, k, with_inner=False, **opts)]) for k in value.keys()])
        return set()

    def _call_order(self, value, with_inputs=True, **opts):
        """Generate a call order according to schema dependencies and inputs detected in values."""
        from ngoschema.protocols import ObjectProtocol
        if isinstance(value, ObjectProtocol) and isinstance(value, self._py_type):
            for k in value.keys():
                yield k
        else:
            # order call according to dependencies
            unordered = set(value or {}).union(self._required)
            to_untranslate = unordered.intersection(self._properties_translation)
            to_unalias = unordered.intersection(set(self._aliases).union(self._aliases_negated))
            # replace translated keys
            unordered = unordered.difference(to_untranslate).difference(to_unalias).union(self._properties)
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
                    if k in to_unalias:
                        k = self._aliases.get(k)
                    t = Object.items_type(self, k)
                    if v is None and t.has_default():
                        v = t.default(**opts)
                    inputs = [i.split('.')[0] for i in t.inputs(v)] if v else []
                    deps[k].update([i for i in inputs if i in self._properties])
            unordered = unordered.union([self._properties_translation.get(k) for k in to_untranslate]).union([self._aliases.get(k) for k in to_unalias])
            if unordered:
                for level in topological_sort(deps):
                    in_level = level.intersection(unordered)
                    unordered.difference_update(in_level)
                    for i in in_level:
                        yield i
                for i in unordered:
                    yield i

    def _print_order(self, value, excludes=[], only=[], no_defaults=False, no_read_only=False, **opts):
        """Generate a print order according to schema and inherited schemas properties order
        and additonal properties detected in values.

        Various options allow to filter results:
        :param excludes: keys to exclude
        :param only: list of the only keys to return
        :param no_defaults: removes values equal to their default
        """
        keys = set((value or {}).keys())
        all_ordered = list(keys.intersection(self._required))
        all_ordered += [k for k in self._properties.keys() if k in keys and k not in self._required]
        all_ordered += list(self._aliases) + list(self._aliases_negated)
        all_ordered += list(keys.difference(all_ordered))
        rq = self._required.union(getattr(value, '_required', []))
        ns = self._not_serialized.union(getattr(value, '_not_serialized', []))
        ro = self._read_only.union(getattr(value, '_read_only', []))
        avs = {k2: value[k1] for k1, k2 in self._aliases.items() if k1 in all_ordered}
        navs = {k2: - value[k1] for k1, k2 in self._aliases_negated.items() if k1 in all_ordered}
        opts.setdefault('context', getattr(value, '_context', self._context))
        for k in all_ordered:
            if k in ns or k in excludes:
                continue
            if no_read_only and k in ro:
                continue
            if only and k not in only:
                continue
            v = value.get(k, avs.get(k, navs.get(k)))
            if no_defaults and k not in rq:
                if v is None:
                    continue
                if isinstance(v, Mapping) and not v:
                    continue
                t = self.items_type(k)
                if t.has_default():
                    d = t.default(**opts)
                    v = neg(v) if k in self._aliases_negated else v
                    if v == d:
                        continue
                    if Pattern.check(d) and v == t.evaluate(d, **opts):
                        continue
            yield k

    def items_type(self, name):
        """Returns the type of a property by its name."""
        name = self._aliases.get(name, name)
        name = self._aliases_negated.get(name, name)
        pt = self._properties.get(name)
        if pt is not None:
            return pt
        for reg, t in self._properties_pattern:
            if reg.search(name):
                return t
        if self._properties_additional:
            return self._properties_additional
        raise KeyError(name)


# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict, defaultdict, Mapping
import re
from operator import neg

from ..exceptions import InvalidValue
from ..decorators import log_exceptions
from ..utils import ReadOnlyChainMap as ChainMap
from .type import Type, TypeChecker
from .constants import _True, _False
from .type import Type
from .array import Array
from .literals import Pattern


@TypeChecker.register('object')
class Object(Type):
    _schema = {'type': 'object'}
    _py_type = OrderedDict
    _properties = OrderedDict()
    _properties_pattern = set()
    _properties_additional = _True()
    _dependencies = {}
    _extends = []
    _required = set()
    _read_only = set()
    _not_serialized = set()
    _not_validated = set()
    _has_default = set()
    _properties_translation = {}
    _aliases = {}
    _aliases_negated = {}
    _primary_keys = []

    def __init__(self, **schema):
        # split the schema to isolate properties schema and object schema
        from .type_builder import TypeBuilder
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

        cls_name = self.__class__.__name__
        schema['properties'] = ChainMap(*[s.get('properties', {}) for s in mro_schemas])
        self._properties = OrderedDict([(name, TypeBuilder.build(f'{cls_name}/properties/{name}', sch)())
                                         for name, sch in schema.get('properties', {}).items()])
        pattern_properties = ChainMap(*[s.get('patternProperties', {}) for s in mro_schemas])
        self._properties_pattern = set([(re.compile(k), Type.build(
            f'{cls_name}/patternProperties/{k}', v)()) for k, v in pattern_properties.items()])
        self._properties_additional = TypeBuilder.build(f'{cls_name}/additionalProperties', schema.get('additionalProperties', True))
        self._has_default = set(k for k, t in self._properties.items() if t.has_default())
        self._required.difference_update(self._has_default)

    def __call__(self, *args, validate=True, convert=True, check=False, context=None, **kwargs):
        assert len(args) <= 1
        opts = kwargs if len(args) == 1 else {}
        data = args[0] if args else kwargs
        if check and not self.check(data):
            raise InvalidValue('%s is not compatible with %s' % data, self)
        context = Type._make_context(self, context)
        data = Object._convert(self, data, context=context, convert=convert, **opts)
        if validate:
            self.validate(data)
        return data

    @staticmethod
    def _repr_schema(self):
        if self._sch_repr is None:
            self._sch_repr = OrderedDict()
            self._sch_repr['type'] = 'object'
            self._sch_repr['properties'] = {}
            for k in Object.print_order(self, self._schema.get('properties', {}), no_read_only=True):
                self._sch_repr['properties'][k] = self._schema['properties'].get('type')
            if self._schema.get('additionalProperties', False):
                self._sch_repr['additionalProperties'] = True
        return self._sch_repr

    @classmethod
    def is_object(cls):
        return True

    @classmethod
    def check(cls, value, **opts):
        return isinstance(value, Mapping)

    @classmethod
    def convert(cls, value, **opts):
        return Object._convert(cls, value, **opts)

    @staticmethod
    def _convert(self, value, convert=False, **opts):
        avs = {k2: value[k1] for k1, k2 in self._aliases.items() if k1 in value}
        navs = {k2: - value[k1] for k1, k2 in self._aliases_negated.items() if k1 in value}
        ret = OrderedDict((k, None) for k in Object.call_order(self, value, with_inputs=convert))
        for k in ret.keys():
            t = self._properties_type(k)
            v = value.get(k) or avs.get(k) or navs.get(k)
            if v is None and (t.has_default() or k in self._required):
                v = t.default()
            ret[k] = v if v is None or not convert else t(v, **opts)
        return ret

    def validate(self, value, excludes=[], as_dict=False, **opts):
        from ngoschema.types import ObjectProtocol, ArrayProtocol
        errors = {}
        try:
            if 'properties' not in excludes:
                for k in Object.call_order(self, value, with_inputs=True):
                    if k not in self._not_validated and k not in excludes and value.get(k) is not None:
                        t = self._properties_type(k)
                        v = value[k]
                        protocol = Type
                        if issubclass(t, ObjectProtocol):
                            protocol = ObjectProtocol
                        if issubclass(t, ArrayProtocol):
                            protocol = ArrayProtocol
                        errors.update(protocol.validate(t, value[k], excludes=[], as_dict=True))
            errors.update(Type.validate(self, value, excludes=excludes+['properties', 'patternProperties', 'additionalProperties'], as_dict=True, **opts))
        except Exception as er:
            raise er
        return errors if as_dict else self._format_error(value, errors)

    #@log_exceptions
    def serialize(self, value, excludes=[], only=[], attr_prefix='', **opts):
        # separate excludes/only from opts as they apply to the first component and might be applied to its properties
        no_defaults = opts.get('no_defaults', False)
        ptypes = [(k, self._properties_type(k)) for k in Object.print_order(self, value, excludes=excludes, only=only, **opts)]
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
        if value is None:
            if self.has_default():
                return self._inputs(self.default(), key, with_inner, **opts)
            return set()
        #value = value if value is not None else self.default()
        if key is not None:
            v = value.get(key)
            try:
                i = set() if not v else self._properties_type(key).inputs(v, **opts)
            except Exception as er:
                self._logger.error(f'{key} {str(value)[:40]}...: {str(er)}', exc_info=True)
                raise er
            return i.union(self._dependencies.get(key, []))
        if with_inner:
            return ChainMap(*[set([f'{k}.{i}' for i in Object._inputs(self, value, k, with_inner=False, **opts)]) for k in value.keys()])
        return set()

    def call_order(self, value, with_inputs=True, **opts):
        """Generate a call order according to schema dependencies and inputs detected in values."""
        from .object_protocol import ObjectProtocol
        if isinstance(value, ObjectProtocol) and isinstance(value, self._py_type):
            for k in value.keys():
                yield k
        else:
            # order call according to dependencies
            unordered = set(value or {})
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
                    t = self._properties_type(k)
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

    def print_order(self, value, excludes=[], only=[], no_defaults=False, no_read_only=False, **opts):
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
        avs = {k2: self[k1] for k1, k2 in self._aliases.items() if k1 in all_ordered}
        navs = {k2: - self[k1] for k1, k2 in self._aliases_negated.items() if k1 in all_ordered}
        for k in all_ordered:
            if k in ns or k in excludes:
                continue
            if no_read_only and k in ro:
                continue
            if only and k not in only:
                continue
            v = value.get(k) or avs.get(k) or navs.get(k)
            if no_defaults and k not in rq:
                if v is None:
                    continue
                if isinstance(v, Mapping) and not v:
                    continue
                t = self._properties_type(k)
                if t.has_default():
                    d = t.default()
                    v = neg(v) if k in self._aliases_negated else v
                    if v == d:
                        continue
                    if Pattern.check(d) and v == t.convert(d, **opts):
                        continue
            yield k

    #@log_exceptions
    def default(self, **opts):
        dft = Type.default(self, **opts)
        return dft
        #TODO remove the following
        ret = OrderedDict((k, None) for k in Object.call_order(self, dft))
        for k in ret.keys():
            v = dft.get(k)
            if v is None:
                t = self._properties_type(k)
                v = t.default(**opts) if t.has_default() else None
            ret[k] = v
        return self._py_type(ret) if self._py_type else ret

    def _properties_type(self, name):
        """Returns the type of a property by its name."""
        pt = self._properties.get(name)
        if pt is not None:
            return pt
        for reg, t in self._properties_pattern:
            if reg.search(name):
                return t
        if self._properties_additional:
            return self._properties_additional
        raise KeyError(name)

    def _alias_value(self, key, value):
        alias = self._aliases.get(key)
        if alias:
            return alias, value
        alias = self._aliases_negated.get(key)
        if alias:
            return alias, -value
        return key, value

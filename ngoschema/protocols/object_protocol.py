# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import MutableMapping, Mapping
from collections import OrderedDict, defaultdict
import re
from operator import neg
import copy
import sys
import six

from ..exceptions import InvalidValue
from ..decorators import assert_arg
from ..utils import ReadOnlyChainMap as ChainMap, shorten
from .. import decorators
from ..resolver import UriResolver, resolve_uri
from ..inspect.inspect_symbols import inspect_function
from ..types.strings import Expr, Pattern, String
from ..types.array import Array, Tuple
from ..types.object import Object
from ..types.symbols import Symbol, Function, Method
from ..resolver import scope
from ..managers.type_builder import DefaultValidator
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from .. import settings
from .type_protocol import TypeProtocol
from .collection_protocol import CollectionProtocol

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD
ADD_LOGGING = settings.DEFAULT_ADD_LOGGING
ASSERT_ARGS = settings.DEFAULT_ASSERT_ARGS
LOGGER_LEVEL = settings.DEFAULT_LOGGER_LEVEL
ATTRIBUTE_BY_NAME = settings.DEFAULT_ATTRIBUTE_BY_NAME
SCHEMA_DEF_KEYS = settings.SCHEMA_DEF_KEYS
PROP_PREF = {
    'get': settings.GETTER_PREFIX,
    'set': settings.SETTER_PREFIX,
    'del': settings.DELETER_PREFIX,
}


def split_cname(cname):
    # split cname into an array of identifiers
    # in case a relative cname is given, removes the first empty cname
    # all next empty id means 'parent'
    def split_part(part):
        parts = part.split('[')
        n, indices = parts[0], parts[1:]
        return [n] + [int(i.strip(']')) for i in indices]
    cns = sum([split_part(part) for part in cname.split('.')], [])
    return cns.pop(0) if cns and not cns[0] else cns


class PropertyDescriptor:

    def __init__(self, pname, ptype, fget=None, fset=None, fdel=None, desc=None):
        self.__doc__ = desc or pname
        self.pname = pname
        self.ptype = ptype
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, obj, owner=None):
        if obj is None and owner is not None:
            return self
        try:
            key = self.pname
            outdated = obj._is_outdated(key)
            if outdated or self.fget or self.fset:
                inputs = obj._items_inputs_evaluate(key)
                if self.fget:
                    obj._set_data(key, self.fget(obj))
                obj._set_data_validated(key, obj._items_evaluate(key, validate=not obj._lazy_loading and key not in obj._not_validated))
                obj._items_inputs[key] = inputs  # after set_validated_data as it touches inputs data
            value = obj._data_validated[key]
            if outdated and self.fset:
                self.fset(obj, value)

            return value
        except Exception as er:
            obj._logger.error(er, exc_info=True)
            raise

    def __set__(self, obj, value):
        try:
            key = self.pname
            if key in obj._read_only:
                raise AttributeError("'%s' is read only" % key)
            obj._set_data(key, value)
            if not obj._lazy_loading:
                obj._items_inputs[key] = obj._items_inputs_evaluate(key)
                obj._set_data_validated(key, obj._items_evaluate(key, validate=not obj._lazy_loading and key not in obj._not_validated))
                if self.fset:
                    self.fset(obj, obj._data_validated[key])
        except Exception as er:
            obj._logger.error(er, exc_info=True)
            raise

    def __delete__(self, obj):
        key = self.pname
        if key in self._required:
            raise AttributeError('%s is a required argument.' % key)
        if self.fdel:
            self.fdel(obj)
        del obj._data[key]
        del obj._data_validated[key]
        del obj._items_inputs[key]


class ObjectProtocol(CollectionProtocol, Object, MutableMapping):
    """
    ObjectProtocol is class defined by a json-schema and built by TypeBuilder.build_object_protocol.
    The schema is specified directly by a protected attribute _schema or by providing its id using a protected
    attribute _id to be resolved in loaded schemas.

    The class is built with an ordered dictionary of property types (which can be Literal or a subclass of
    ObjectProtocol or ArrayProtocol.

    An instance behave as a standard mapping, but its properties can also be accessed through a
    descriptor (renamed using clean_js_name in case it contains forbidden characters in python arguments).
    When _attribute_by_name is enabled, attributes can be accessed also by their names according to setting ATTRIBUTE_NAME_FIELD

    If lazy loading is enabled, data is only constructed and validated on first read access. If not, validation is done
    when setting the item.
    """
    _attribute_by_name = ATTRIBUTE_BY_NAME
    _data = {}
    _data_validated = {}
    _data_additional = {}
    _items_inputs = {}
    _extends = []
    _properties_translation = {}
    _primary_keys = []

    def __new__(cls, *args, **kwargs):
        from ..managers import TypeBuilder
        data = args[0] if args else kwargs
        s_id = data.get('$schema') if isinstance(data, Mapping) else None
        if s_id:
            # handle case $schema is given as a canonical name
            if '/' not in s_id:
                data['$schema'] = default_ns_manager.get_cname_id(s_id)
            if s_id != cls._id:
                cls = TypeBuilder.load(s_id)
        new = super(ObjectProtocol, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        kwargs.pop('$schema', None)
        CollectionProtocol.__init__(self, *args, **kwargs)
        for k in self._has_pk:
            self[k]

    def _make_context(self, context=None, *extra_contexts):
        TypeProtocol._make_context(self, context, self._data_validated, {'this': self}, self, *extra_contexts)

    def _items_evaluate(self, item, **opts):
        ctx = self._context
        v = self._data
        for n in item.split('.'):
            t = self.items_type(n)
            v = t(v[n], context=ctx, **opts)
            ctx = getattr(v, 'context', ctx)
        return v

    def _items_touch(self, item):
        CollectionProtocol._items_touch(self, item)
        for d, s in self._dependencies.items():
            if item in s:
                self._items_touch(d)

    def _touch(self):
        CollectionProtocol._touch(self)
        keys = list(self._data.keys())
        self._items_inputs = {k: {} for k in keys}
        self._data_validated = {k: None for k in keys}
        self._data_additional = {k: None for k in self._data_additional.keys()}
        self._dependencies = dict(self.__class__._dependencies)

    def __len__(self):
        return len(self._data_validated)

    def __iter__(self):
        return iter(self._data_validated.keys())

    @classmethod
    def _properties_raw_trans(cls, name):
        for trans, raw in cls._properties_translation.items():
            if name in (raw, trans):
                return raw, trans
        if name in cls._properties:
            return name, name
        alias = cls._aliases.get(name)
        if alias:
            return alias, name
        alias = cls._aliases_negated.get(name)
        if alias:
            return alias, name
        if cls._properties_additional:
            return name, clean_js_name(name)
        return None, None

    def __getattr__(self, name):
        # private and protected attributes at accessed directly
        if name.startswith('_'):
            return MutableMapping.__getattribute__(self, name)
        op = lambda x: neg(x) if name in self._aliases_negated else x
        name = self._aliases_negated.get(name, name)
        name = self._aliases.get(name, name)
        raw = self._properties_translation.get(name, name)
        desc = self._properties_descriptor.get(raw)
        if desc:
            return op(desc.__get__(self))
        if self._properties_additional and name in self._data:
            self._items_inputs[raw] = self._items_inputs_evaluate(name)
            self._data_additional[raw] = v = op(self[name])
            return v
        if self._attribute_by_name:
            try:
                return op(self.resolve_cname([name]))
            except Exception as er:
                self._logger.error(er, exc_info=True)
                raise
        if not self._properties_additional:
            # additional properties not allowed, raise exception
            raise AttributeError("'{0}' is not a valid property of {1}".format(
                                name, self.__class__.__name__))

    def resolve_cname_path(self, cname):
        from ..models.metadata import NamedObject
        # use generators because of 'null' which might lead to different paths
        def _resolve_cname_path(cn, cur, cur_cn, cur_path):
            # empty path, yield current path and doc
            if not cn:
                yield cur, cn, cur_path
            if Object.check(cur):
                cn2 = cur_cn + [(cur.get(ATTRIBUTE_NAME_FIELD) or '<anonymous>').rsplit(':')[-1]]
                if cn2 == cn[0:len(cn2)]:
                    if cn2 == cn:
                        yield cur, cn, cur_path
                    for k, v in cur.items():
                        if Object.check(v) or Array.check(v, with_string=False):
                            for _ in _resolve_cname_path(cn, v, cn2, cur_path + [k]):
                                yield _
            if Array.check(cur, with_string=False):
                for i, v in enumerate(cur):
                    for _ in _resolve_cname_path(cn, v, cur_cn, cur_path + [i]):
                        yield _

        cname = [self.name] if isinstance(self, NamedObject) else []
        cname += [e.split(':')[-1] for e in cname]
        cur = self
        cur_cn = []
        # first search without last element, as last one might not be a named object
        # but the name of an attribute
        for d, c, p in _resolve_cname_path(cname[:-1], cur, cur_cn, []):
            if cname[-1] in d or (d.get(ATTRIBUTE_NAME_FIELD) or '<anonymous>').rsplit(':')[-1] == cname[-1]:
                p.append(cname[-1])
                return p
            # we can continue the search from last point. we remove the last element of the
            # canonical name which is going to be read again
            for d2, c2, p2 in _resolve_cname_path(cname, d, c[:-1], p):
                return p2
        raise Exception("Unresolvable canonical name '%s' in '%s'" % (cname, cur))

    #@assert_arg(1, Tuple, strDelimiter='.')
    def resolve_cname(self, cname):
        cname = cname if Array.check(cname) else cname.split('.')
        cur, path = self, self.resolve_cname_path(cname)
        for p in path:
            cur = cur[p]
        return cur

    def __setattr__(self, name, value):
        # private and protected attributes at accessed directly
        if name.startswith('_'):
            return MutableMapping.__setattr__(self, name, value)
        try:
            self[name] = value
        except KeyError as er:
            self._logger.error(er, exc_info=True)
            raise AttributeError("'{0}' is not a valid property of {1}".format(
                                 name, self.__class__.__name__))

    def __getitem__(self, key):
        if not key:
            return self._parent
        op = lambda x: neg(x) if key in self._aliases_negated else x
        key = self._aliases_negated.get(key, key)
        key = self._aliases.get(key, key)
        raw, trans = self._properties_raw_trans(key)
        desc = self._properties_descriptor.get(raw)
        if desc:
            return op(desc.__get__(self))
        parts = split_cname(key)
        # case: canonical name such as a[0][1].b[0].c
        if len(parts) > 1:
            cur = self
            for p in parts:
                cur = cur[p]
                if cur is None:
                    return
            return op(cur)
        if key in self._data:
            if self._lazy_loading or self._is_outdated(key):
                self._items_inputs[key] = self._items_inputs_evaluate(key)
                self._set_data_validated(key, self._items_evaluate(key, validate=not self._lazy_loading and key not in self._not_validated))
            return op(self._data_validated[key])
        raise KeyError(key)

    def __setitem__(self, key, value):
        op = lambda x: neg(x) if key in self._aliases_negated else x
        raw, trans = self._properties_raw_trans(key)
        desc = self._properties_descriptor.get(raw)
        if desc:
            return desc.__set__(self, op(value))
        if not self._properties_additional:
            raise KeyError(key)
        v = op(value)
        self._set_data(key, v)
        self._data_additional[key] = v
        if not self._lazy_loading:
            self._set_data_validated(key, v)

    def __delitem__(self, key):
        for trans, raw in self._properties_translation.items():
            if key in (trans, raw):
                delattr(self, trans)
                break
        else:
            del self._data[key]
            del self._items_inputs[key]
            del self._data_validated[key]

    #def print_order(self, **opts):
    #    return Object.print_order(self, self._data, **opts)

    #def call_order(self, **opts):
    #    return Object.call_order(self, self._data, **opts)

    def _serialize(self, value, **opts):
        ret = Object._serialize(self, value, **opts)
        for alias, raw in self._aliases.items():
            if alias not in self._not_serialized:
                v = ret.get(raw)
                if v is not None:
                    ret[alias] = v
        for alias, raw in self._aliases_negated.items():
            if alias not in self._not_serialized:
                v = ret.get(raw)
                if v is not None:
                    ret[alias] = - v
        return ret

    def __repr__(self):
        if self._repr is None:
            m = settings.PPRINT_MAX_EL
            ks = list(self._print_order(self._data, no_defaults=True, no_read_only=True, with_inputs=False))
            hidden = max(0, len(ks) - m)
            a = ['%s=%s' % (k, shorten(self._data_validated[k] or self._data[k], str_fun=repr)) for k in ks[:m]]
            a += ['+%i...' % hidden] if hidden else []
            self._repr = '%s(%s)' % (self.qualname(), ', '.join(a))
        return self._repr

    def __str__(self):
        if self._str is None:
            m = settings.PPRINT_MAX_EL
            ks = list(self._print_order(self._data, no_defaults=False, no_read_only=False, with_inputs=False))
            hidden = max(0, len(ks) - m)
            a = ['%s: %s' % (k, shorten(self._data_validated[k] or self._data[k], str_fun=repr)) for k in ks[:m]]
            a += ['+%i...' % hidden] if hidden else []
            self._str = '{%s}' % (', '.join(a))
        return self._str

    @classmethod
    def items_type(cls, item):
        from .type_proxy import TypeProxy
        if cls._items_type_cache is None:
            cls._items_type_cache = {}
        t = cls._items_type_cache.get(item)
        if t is None:
            t = Object.items_type(cls, item)
            if t and isinstance(t, TypeProxy) and t.proxy_type:
                t = t.proxy_type
            cls._items_type_cache[item] = t
        return t

    @property
    def session(self):
        if not self._session and self._root and getattr(self._root, '_repo', None):
            self._session = self._root._repo.session
        return self._session

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from ..managers.type_builder import TypeBuilder, scope
        from ..protocols import TypeProxy
        attrs = attrs or {}
        cname = default_ns_manager.get_id_cname(id)
        clsname = attrs.pop('_clsname', None) or cname.split('.')[-1]

        # create/set logger
        logger = logging.getLogger(cname)
        level = logging.getLevelName(attrs.get('_log_level', LOGGER_LEVEL))
        logger.setLevel(level)

        if schema.get('$schema'):
            ms_uri = schema['$schema']
            metaschema = resolve_uri(ms_uri)
            resolver = UriResolver.create(uri=id, schema=schema)
            meta_validator = DefaultValidator(metaschema, resolver=resolver)
            meta_validator.validate(schema)

        bases_extended = [TypeBuilder.load(scope(e, id)) for e in schema.get('extends', [])]
        bases_extended = [e for e in bases_extended if not any(issubclass(b, e) for b in bases)]
        pbases = [b for b in bases if issubclass(b, ObjectProtocol) and not any(issubclass(e, b) for e in bases_extended)]
        bases = [b for b in bases if not any(issubclass(e, b) for e in bases_extended)]
        pbases = pbases + bases_extended

        not_ready_yet = tuple(b for b in pbases if isinstance(b, TypeProxy) and b.proxy_type is None)
        not_ready_yet_sch = tuple(TypeBuilder.expand(b._proxy_uri) for b in not_ready_yet)
        pbases = tuple(b for b in pbases if b not in not_ready_yet)
        if not pbases:
            bases += [ObjectProtocol]

        # create an aliases dictionary from all bases dependencies
        aliases = schema.get('aliases', {})
        negated_aliases = schema.get('negatedAliases', {})
        properties_translation = {}

        # building inner definitions
        defs = {dn: TypeBuilder.load(f'{id}/$defs/{dn}') for dn, defn in schema.get('$defs', {}).items()}

        # create a dependency dictionary from all bases dependencies
        dependencies = defaultdict(set)
        for k, v in schema.get('dependencies', {}).items():
            dependencies[k].update(set(v))
        for b in pbases:
            for k, v in b._dependencies.items():
                dependencies[k].update(set(v))
        for s in not_ready_yet_sch:
            for k, v in s.get('dependencies', {}).items():
                dependencies[k].update(set(v))

        # create the reversed one
        outputs = defaultdict(set)
        for k, v in dependencies.items():
            for s in v:
                outputs[s].update([k])

        primary_keys = schema.get('primaryKeys', [])
        if not primary_keys:
            for b in pbases:
                primary_keys += b._primary_keys
            primary_keys = [k for i, k in enumerate(primary_keys) if i == primary_keys.index(k)]

        extends = [b._id for b in pbases] + [b._proxy_uri for b in not_ready_yet]
        not_serialized = set().union(schema.get('notSerialized', []), *[b._not_serialized for b in pbases], *[s.get('notSerialized', []) for s in not_ready_yet_sch])
        not_validated = set().union(schema.get('notValidated', []), *[b._not_validated for b in pbases], *[s.get('notValidated', []) for s in not_ready_yet_sch])
        required = set().union(schema.get('required', []), *[b._required for b in pbases], *[s.get('required', []) for s in not_ready_yet_sch])
        read_only = set().union(schema.get('readOnly', []), *[b._read_only for b in pbases], *[s.get('readOnly', []) for s in not_ready_yet_sch])
        has_default = set().union(*[b._properties_with_default for b in pbases])

        # create type for properties
        properties = OrderedDict([(k, TypeBuilder.build(f'{id}/properties/{k}', v))
                                  for k, v in schema.get('properties', {}).items()])
        for i, s in zip(not_ready_yet, not_ready_yet_sch):
            for k, v in s.get('properties', {}).items():
                properties[k] = TypeBuilder.build(f'{id}/properties/{k}', v)
        all_properties = ChainMap(properties, *[b._properties for b in pbases])
        pattern_properties = set([(re.compile(k),
                                   TypeBuilder.build(f'{id}/patternProperties/{k}', v))
                                   for k, v in schema.get('patternProperties', {}).items()])
        additional_properties = TypeBuilder.build(f'{id}/additionalProperties', schema.get('additionalProperties', True))

        # add some magic on methods defined in class
        # exception handling, argument conversion/validation, dependencies, etc...
        add_logging = attrs.get('_add_logging', ADD_LOGGING)
        assert_args = attrs.get('_assert_args', ASSERT_ARGS)
        for k, v in attrs.items():
            if isinstance(v, TypeProtocol):
                schema[k] = v._schema
            if Function.check(v):
                f = v
                if add_logging:
                    if k == '__init__':
                        f = decorators.log_init(f)
                if assert_args and f.__doc__:
                    fi = inspect_function(f)
                    for pos, a in enumerate(fi['arguments']):
                        t = a.get('variableType')
                        if t:
                            sch = {'type': t, 'description': a.get('description')}
                            logger.debug(
                                "decorate <%s>.%s with argument %i validity check.",
                                clsname, k, pos)
                            f = decorators.assert_arg(pos, TypeProtocol, **sch)(f)
                # add exception logging
                if add_logging and not k.startswith("__"):
                    logger.debug("decorate <%s>.%s with exception logger", clsname, k)
                    f = decorators.log_exceptions(f)
                attrs[k] = f

        # go through attributes to find default values, accessors and additional dependencies
        # store additional data that will be used to rebuild the inner object type with property redefinitions
        def is_symbol(f):
            import types
            return isinstance(f, types.FunctionType) or isinstance(f, classmethod) or isinstance(f, types.MethodType)

        def is_mro_symbol(a):
            mro_attrs = [getattr(b, a, None) for b in bases + bases_extended + [ObjectProtocol]] + [attrs.get(a)]
            return any(is_symbol(a) for a in mro_attrs if a)

        extra_schema_properties = {}
        descriptor_funs = {}
        for pname, ptype in all_properties.items():
            ptrans = clean_js_name(pname)
            if pname != ptrans:
                properties_translation[ptrans] = pname
            # excluding definition keys from schema lookup
            attr = attrs.pop(ptrans, None)
            if attr and is_symbol(attr):
                attr = None
            if attr is None and pname not in SCHEMA_DEF_KEYS:
                attr = schema.get(pname)
            if attr is not None:
                if ptype.check(attr, convert=True):
                    v = ptype.serialize(ptype.convert(attr))
                    extra_schema_properties[pname] = dict(ptype._schema)
                    extra_schema_properties[pname]['default'] = v
                    has_default.add(pname)
                    read_only.add(pname)  # as defined in schema attributes or hardcoded
                else:
                    raise InvalidValue("Impossible to get a default value of type '%s' from class attributes '%s'" % (
                        ptype._schema.get("type"), pname))

            pfun = {}
            for prop in ['get', 'set', 'del']:
                fname = f'{PROP_PREF[prop]}{ptrans}'
                fun = attrs.get(fname)
                if not fun:
                    fun = [getattr(b, fname) for b in bases if hasattr(b, fname)]
                    fun = None if not fun else fun[0]
                if fun:
                    insp = inspect_function(fun)
                    for d in insp.get('decorators', []):
                        if 'depend_on_prop' == d['name']:
                            dependencies[pname].update(d['varargs']['valueLiteral'])
                pfun[prop] = fun
            if any(pfun.values()):
                descriptor_funs[pname] = pfun

        # add redefined properties to local properties and to schemas
        if extra_schema_properties:
            properties.update({k: TypeBuilder.build(f'{id}/properties/{k}', sch) for k, sch in extra_schema_properties.items()})
            schema.setdefault('properties', {})
            schema['properties'].update(extra_schema_properties)

        # create descriptors
        # go through local properties and create descriptors
        properties_descriptor = {}
        for pname, ptype in properties.items():
            if ptype.has_default():
                has_default.add(pname)
            pfun = descriptor_funs.pop(pname, {})
            properties_descriptor[pname] = PropertyDescriptor(
                pname,
                ptype,
                pfun.get('get'),
                pfun.get('set'),
                pfun.get('del'),
                ptype._schema.get('description'))
        # remaining descriptors are properties defined in other bases with local getter/setter/deleter definitions
        for pname, pfun in descriptor_funs.items():
            ptrans = clean_js_name(pname)
            for b in pbases:
                if hasattr(b, ptrans) and isinstance(b, PropertyDescriptor):
                    d = copy.copy(getattr(b.trans))
                    for k, v in pfun.items():
                        if v is not None:
                            setattr(d, f'f{k}', v)
                    properties_descriptor[pname] = d
                    break

        # set the attributes
        attrs['_primary_keys'] = primary_keys
        attrs['_properties_translation'] = dict(ChainMap(properties_translation, *[b._properties_translation for b in pbases]))
        attrs['_aliases'] = dict(ChainMap(aliases, *[b._aliases for b in pbases]))
        attrs['_aliases_negated'] = dict(ChainMap(negated_aliases, *[b._aliases_negated for b in pbases]))
        attrs['_extends'] = extends
        attrs['_properties_chained'] = all_properties
        attrs['_properties'] = dict(all_properties)
        attrs['_has_pk'] = tuple(k for k, p in all_properties.items() if len(getattr(p, '_primary_keys', [])))
        attrs['_properties_pattern'] = set().union(pattern_properties, *[b._properties_pattern for b in pbases])
        attrs['_properties_additional'] = additional_properties
        attrs['_properties_descriptor'] = dict(ChainMap(properties_descriptor, *[getattr(b, '_properties_descriptor', {})
                                                                                 for b in pbases]))
        attrs['_not_serialized'] = not_serialized
        attrs['_not_validated'] = not_validated
        attrs['_required'] = required
        attrs['_read_only'] = read_only
        attrs['_properties_allowed'] = set(attrs['_properties']).union(attrs['_aliases'])\
            .union(attrs['_aliases_negated']).union(attrs['_properties_translation']).difference(read_only)
        attrs['_properties_with_default'] = has_default
        attrs['_dependencies'] = dependencies
        attrs['_outputs'] = outputs
        attrs['_logger'] = logger
        attrs['_schema_chained'] = ChainMap(schema, *[getattr(b, '_schema', {}) for b in bases])
        attrs['_schema'] = dict(attrs['_schema_chained'])
        attrs['_items_type_cache'] = None
        attrs['_id'] = id
        attrs['_validator'] = DefaultValidator(schema, resolver=UriResolver.create(uri=id, schema=schema))
        attrs['_mro_type'] = pbases
        # add inner definitions
        for k, d in defs.items():
            attrs[k] = d
        # add properties
        for k, p in properties_descriptor.items():
            # only set descriptors which do not overwrite existing symbols
            if not is_mro_symbol(k):
                attrs.setdefault(clean_js_name(k), p)

        bases = tuple(bases + bases_extended)
        if not_ready_yet:
            logger.warning('removing bases not ready %s' % not_ready_yet)
            bases = tuple(b for b in bases if b not in not_ready_yet)

        cls = type(clsname, bases, attrs)
        cls._py_type = cls
        return cls


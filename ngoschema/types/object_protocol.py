# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import MutableMapping, defaultdict, OrderedDict
from collections import OrderedDict, defaultdict
import re
import copy

from ..exceptions import InvalidValue
from ..decorators import memoized_method, assert_arg
from ..utils import ReadOnlyChainMap as ChainMap
from .. import decorators
from ..resolver import UriResolver, resolve_uri
from ..inspect import inspect_function
from .literals import Literal, Expr, Pattern, String
from .array import Array, Tuple
from .object import Object
from .symbols import Function
from .type import Type, DefaultValidator
from .type_builder import TypeBuilder, scope
from .namespace import default_ns_manager, clean_js_name
from .. import settings, DEFAULT_CONTEXT


ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD
ADD_LOGGING = settings.DEFAULT_ADD_LOGGING
ASSERT_ARGS = settings.DEFAULT_ASSERT_ARGS
LOGGER_LEVEL = settings.DEFAULT_LOGGER_LEVEL
LAZY_LOADING = settings.DEFAULT_LAZY_LOADING
ATTRIBUTE_BY_NAME = settings.DEFAULT_ATTRIBUTE_BY_NAME
PROP_PREF = {
    'get': settings.GETTER_PREFIX,
    'set': settings.SETTER_PREFIX,
    'del': settings.DELETER_PREFIX,
}


def split_cname(cname):
    def split_part(part):
        parts = part.split('[')
        n, indices = parts[0], parts[1:]
        return [n] + [int(i.strip(']')) for i in indices]
    return sum([split_part(part) for part in cname.split('.')], [])


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
        key = self.pname
        if obj._is_outdated(key) or self.fget:
            try:
                inputs = obj._evaluate_inputs(key)
                if self.fget:
                    obj._set_data(key, self.fget(obj))
                obj._set_validated_data(key, obj._property_evaluate(key, obj._data.get(key)))
                obj._input_data[key] = inputs  # after set_validated_data as it touches inputs data
            except Exception as er:
                raise
        return obj._validated_data[key]

    def __set__(self, obj, value):
        key = self.pname
        if key in obj._read_only:
            raise AttributeError("'%s' is read only" % key)
        obj._set_data(key, value)
        if self.fset:
            self.fset(obj, obj._data[key])
        if not obj._lazy_loading:
            obj._input_data[key] = obj._evaluate_inputs(key)
            obj._set_validated_data(key, obj._property_evaluate(key, obj._data.get(key)))

    def __delete__(self, obj):
        key = self.pname
        if key in self._required:
            raise AttributeError('%s is a required argument.' % key)
        if self.fdel:
            self.fdel(obj)
        del obj._data[key]
        del obj._input_data[key]
        del obj._validated_data[key]


class ObjectProtocol(Object, MutableMapping):
    """
    ObjectProtocol is class defined by a json-schema and built by TypeBuilder.build_object_protocol.
    The schema is specified directly by a protected attribute _schema or by providing its id using a protected
    attribute _schema_id to be resolved in loaded schemas.

    The class is built with an ordered dictionary of property types (which can be Literal or a subclass of
    ObjectProtocol or ArrayProtocol.

    An instance behave as a standard mapping, but its properties can also be accessed through a
    descriptor (renamed using clean_js_name in case it contains forbidden characters in python arguments).
    When _attribute_by_name is enabled, attributes can be accessed also by their names according to setting ATTRIBUTE_NAME_FIELD

    If lazy loading is enabled, data is only constructed and validated on first read access. If not, validation is done
    when setting the item.
    """
    _lazy_loading = LAZY_LOADING
    _attribute_by_name = ATTRIBUTE_BY_NAME
    _data = {}
    _validated_data = {}
    _input_data = {}
    _literals = set()
    _properties_translation = {}
    #_properties = {'$id': String(), '$schema': String(format='uri-reference')}
    _properties = {}

    def __new__(cls, *args, **kwargs):
        data = args[0] if args else kwargs
        s_id = data.get('$schema')
        if s_id:
            # handle case $schema is given as a canonical name
            if '/' not in s_id:
                data['$schema'] = default_ns_manager.get_cname_id(s_id)
            if s_id != cls._schema_id:
                cls = TypeBuilder.load(s_id)
        new = super(ObjectProtocol, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def __init__(self, *args, validate=False, context=None, **kwargs):
        data = args[0] if args else kwargs
        self._lazy_loading = lz = not validate or self._lazy_loading
        #data.pop('$schema', None)
        if data is None:
            self._data = self.default().copy()
        else:
            self._data = Object.convert(self, data, convert=False)
        self._touch()
        self._make_context(context)
        if not lz:
            list(self.items())
        if validate:
            self.validate(self, excludes=['properties'] if lz else [])

    def _make_context(self, context=None, *extra_contexts):
        self._context = Type._make_context(self, context, *extra_contexts, self._validated_data, self)

    def _touch(self, key=None):
        if key:
            self._validated_data[key] = None
            self._input_data[key] = {}
            for d, s in self._dependencies.items():
                if key in s:
                    self._touch(d)
        else:
            keys = list(self._data.keys())
            #keys = list(Object.call_order(self, self._data, with_inputs=True))
            self._input_data = {k: {} for k in keys}
            self._validated_data = {k: None for k in keys}

    @property
    def _parent(self):
        return next((m for m in self._context.maps_flattened if isinstance(m, ObjectProtocol) and m is not self), None)

    @property
    def _root(self):
        return next((m for m in reversed(self._context.maps_flattened) if isinstance(m, ObjectProtocol) and m is not self), None)

    def __len__(self):
        return len(self._validated_data)

    def __iter__(self):
        return iter(self._validated_data.keys())

    @classmethod
    def _property_raw_trans(cls, name):
        for trans, raw in cls._properties_translation.items():
            if name in (raw, trans):
                return raw, trans
        if name in cls._properties:
            return name, name
        return None, None

    def _set_data(self, key, value):
        if Literal.check(value) and value != self._data.get(key):
            self._touch(key)
        self._data[key] = value

    def _evaluate_inputs(self, key):
        return {k: self[k] for k in Object._inputs(self, self._data, key, with_inner=False)}

    def _set_validated_data(self, key, value):
        if Literal.check(value):
            if value != self._validated_data.get(key):
                self._touch(key)
        else:
            self._data[key] = value
        self._validated_data[key] = value

    def _is_outdated(self, key):
        return (self._validated_data.get(key) is None and self._data.get(key) is not None
                ) or self._input_data[key] != self._evaluate_inputs(key)

    @classmethod
    def validate(cls, value, **opts):
        return Object.validate(cls, value, **opts)

    def do_validate(self, **opts):
        from .array_protocol import ArrayProtocol
        for k, v in self._validated_data.items():
            if self._is_outdated(k):
                v = self[k]
            if isinstance(v, (ObjectProtocol, ArrayProtocol)):
                v.do_validate(**opts)
            elif v is not None:
                self._property_type(k).validate(v, **opts)
        return self._validated_data

    @classmethod
    def serialize(cls, value, **opts):
        return Object.serialize(cls, value, **opts)

    def do_serialize(self, attr_prefix='', **opts):
        from .array_protocol import ArrayProtocol
        from ..models import Entity
        kt = ((k, self._property_type(k)) for k in Object.print_order(self, self._data, **opts))
        ktn = [(k, t, k if not t.is_literal() else f'{attr_prefix}{k}') for k, t in kt]
        ret = OrderedDict([(n, None) for k, t, n in ktn])
        for k, t, n in ktn:
            v = self._validated_data.get(k)
            if v is None and self._data.get(k) is not None:
                v = self[k]
                #v = self._data.get(k)
            if isinstance(v, (ObjectProtocol, ArrayProtocol)):
                ret[n] = v.do_serialize(attr_prefix=attr_prefix, **opts)
            elif v is not None:
                ret[n] = t.serialize(v, **opts)
        return ret

    def __getattr__(self, name):
        # private and protected attributes at accessed directly
        if name.startswith('_'):
            return MutableMapping.__getattribute__(self, name)
        raw = self._properties_translation.get(name, name)
        if raw in self._properties:
            return object.__getattribute__(self, name)
        if self._additional_properties and name in self._data:
            self._input_data[name] = self._evaluate_inputs(name)
            return self[name]
        if self._attribute_by_name:
            try:
                return self.resolve_cname([name])
            except Exception as er:
                pass
        raise AttributeError("'{0}' is not a valid property of {1}".format(
                             name, self.__class__.__name__))

    def resolve_cname_path(self, cname):
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

        name = self.name
        cname = [name] + [e.split(':')[-1] for e in cname]
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

    @assert_arg(1, Tuple, str_delimiter='.')
    def resolve_cname(self, cname):
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
            raise AttributeError("'{0}' is not a valid property of {1}".format(
                                 name, self.__class__.__name__))

    def __getitem__(self, key):
        raw, trans = self._property_raw_trans(key)
        if raw in self._properties:
            return object.__getattribute__(self, trans)
        parts = split_cname(key)
        # case: canonical name such as a[0][1].b[0].c
        if len(parts) > 1:
            cur = self
            for p in parts:
                cur = cur[p]
            return cur
        if key in self._data:
            if self._lazy_loading or self._is_outdated(key):
                self._input_data[key] = self._evaluate_inputs(key)
                self._set_validated_data(key, self._property_evaluate(key, self._data[key]))
            return self._validated_data[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        raw, trans = self._property_raw_trans(key)
        if raw in self._properties:
            return object.__setattr__(self, trans, value)
        if not self._additional_properties:
            raise KeyError(key)
        self._set_data(key, value)
        if not self._lazy_loading:
            self._input_data[key] = self._evaluate_inputs(key)
            self._set_validated_data(key, self._property_evaluate(key, self._data.get(key)))

    def __delitem__(self, key):
        for trans, raw in self._properties_translation.items():
            if key in (trans, raw):
                delattr(self, trans)
                break
        else:
            del self._data[key]
            del self._input_data[key]
            del self._validated_data[key]

    def __repr__(self):
        def format_str(k, value):
            if Object.check(value):
                return '%s{%i}' % (k, len([k for k, v in value.items() if v is not None]))
            if Array.check(value, with_string=False):
                return '%s[%i]' % (k, len(value))
            return '%s:%s' % (k, self._property_type(k).serialize(value))

        def trim(s):
            return (s[:settings.PPRINT_MAX_STRL] + '...') if len(s) >= settings.PPRINT_MAX_STRL else s

        return '<%s {%s}>' % (self.__class__.__name__,
                              ' '.join([trim(format_str(k, v)) for i, (k, v) in enumerate(self._data.items())
                                        if i < settings.PPRINT_MAX_EL and v is not None] + (
                                  ['...'] if len(self._data) >= settings.PPRINT_MAX_EL else [])))

    def __eq__(self, other):
        if not Object.check(other):
            return False
        if len(self) != len(other) or self.keys() != other.keys():
            return False
        for k in self:
            if self[k] != other[k]:
                return False
        return True

    @classmethod
    def convert(cls, value, **opts):
        return value if isinstance(value, cls) else Object._convert(cls, value, **opts)

    @classmethod
    def check(cls, value, **opts):
        return Object._check(cls, value, **opts)

    @classmethod
    def validate(cls, value, **opts):
        return Object.validate(cls, value, **opts)

    _property_type_cache = None
    @classmethod
    def _property_type(cls, name):
        if cls._property_type_cache is None:
            cls._property_type_cache = {}
        t = cls._property_type_cache.get(name)
        if t is None:
            t = Object._property_type(cls, name)
            cls._property_type_cache[name] = t
        return t

    def _property_evaluate(self, name, value, **opts):
        from .array_protocol import ArrayProtocol
        ptype = self._property_type(name)
        if isinstance(value, ptype) and not Expr.check(value) and not Pattern.check(value):
            lz_excludes = ['items', 'properties'] if getattr(ptype, '_lazy_loading', False) else []
            ptype.validate(value, excludes=opts.pop('excludes', []) + lz_excludes, **opts)
            if isinstance(value, (ObjectProtocol, ArrayProtocol)):
                ptype._make_context(self, self._context)
        else:
            value = ptype(value, context=self._context, **opts)
        return value

    _default = None
    @classmethod
    def default(cls):
        if cls._default is None:
            cls._default = Object.default(cls)
        return cls._default

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from .type_builder import TypeBuilder, scope
        attrs = attrs or {}
        cname = default_ns_manager.get_id_cname(id)
        clsname = attrs.pop('clsname', None) or cname.split('.')[-1]

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

        not_ready_yet = tuple(b for b in pbases if isinstance(b, TypeBuilder.TypeProxy) and b.ref_class is None)
        not_ready_yet_sch = tuple(TypeBuilder.expand(b._ref) for b in not_ready_yet)
        pbases = tuple(b for b in pbases if b not in not_ready_yet)
        if not pbases:
            #pbases = (ObjectProtocol, )
            bases += [ObjectProtocol]

        # building inner definitions
        defs = {dn: TypeBuilder.load(f'{id}/$defs/{dn}') for dn, defn in schema.get('$defs', {}).items()}

        # create a dependency dictionary from all bases dependencies
        dependencies = defaultdict(set, **schema.get('dependencies', {}))
        for b in pbases:
            for k, v in b._dependencies.items():
                dependencies[k].union(set(v))
        for s in not_ready_yet_sch:
            for k, v in s.get('dependencies', {}).items():
                dependencies[k].union(set(v))

        # create the reversed one
        outputs = defaultdict(set)
        for k, v in dependencies.items():
            for s in v:
                outputs[s].update(k)

        schema['extends'] = extends = [b._id for b in pbases] + [b._ref for b in not_ready_yet]
        schema['notSerialized'] = not_serialized = set().union(schema.get('notSerialized', []), *[b._not_serialized for b in pbases], *[s.get('notSerialized', []) for s in not_ready_yet_sch])
        schema['required'] = required = set().union(schema.get('required', []), *[b._required for b in pbases], *[s.get('required', []) for s in not_ready_yet_sch])
        schema['readOnly'] = read_only = set().union(schema.get('readOnly', []), *[b._read_only for b in pbases], *[s.get('readOnly', []) for s in not_ready_yet_sch])
        has_default = set().union(*[b._has_default for b in pbases])

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
        ap = schema.get('additionalProperties', True)
        additional_properties = False if not ap else TypeBuilder.build(f'{id}/additionalProperties',
                                                                           ap if Object.check(ap) else {})

        # add some magic on methods defined in class
        # exception handling, argument conversion/validation, dependencies, etc...
        add_logging = attrs.get('_add_logging', ADD_LOGGING)
        assert_args = attrs.get('_assert_args', ASSERT_ARGS)
        pattrs = {}
        for k, v in attrs.items():
            if isinstance(v, Type):
                schema[k] = v._schema
            if Function.check(v, convert=False):
                f = v
                if add_logging:
                    if k == '__init__':
                        f = decorators.log_init(f)
                if assert_args and f.__doc__:
                    fi = inspect_function(f)
                    for pos, a in enumerate(fi['arguments']):
                        t = a.get('variable_type')
                        if t:
                            sch = {'type': t, 'description': a.get('description')}
                            logger.debug(
                                "decorate <%s>.%s with argument %i validity check.",
                                clsname, k, pos)
                            f = decorators.assert_arg(pos, Type, **sch)(f)
                # add exception logging
                if add_logging and not k.startswith("__"):
                    logger.debug("decorate <%s>.%s with exception logger", clsname, k)
                    f = decorators.log_exceptions(f)
                pattrs[k] = f

        # go through attributes to find default values, accessors and additional dependencies
        # store additional data that will be used to rebuild the inner object type with property redefinitions
        properties_translation = {}
        extra_schema_properties = {}
        descriptors = {}
        for pname, ptype in all_properties.items():
            ptrans = clean_js_name(pname)
            if pname != ptrans:
                properties_translation[ptrans] = pname
            if ptrans in attrs:
                attr = attrs.pop(ptrans)
                if attr is not None:
                    if Literal.check(attr) or Object.check(attr) or Array.check(attr):
                        attr = ptype.convert(attr)
                        extra_schema_properties[pname] = dict(ptype._schema)
                        extra_schema_properties[pname]['default'] = ptype.serialize(attr)
                        has_default.add(pname)
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
                    for d in insp['decorators']:
                        if 'depend_on_prop' == d['name']:
                            dependencies[pname].update(d['varargs']['valueLiteral'])
                pfun[prop] = fun
            if any(pfun.values()):
                descriptors[pname] = pfun

        # add redefined properties to local properties and to schemas
        if extra_schema_properties:
            properties.update({k: TypeBuilder.build(f'{id}/properties/{k}', sch) for k, sch in extra_schema_properties.items()})
            schema.setdefault('properties', {})
            schema['properties'].update(extra_schema_properties)

        # create descriptors
        # go through local properties and create descriptors
        for pname, ptype in properties.items():
            if ptype.has_default():
                has_default.add(pname)
            ptrans = clean_js_name(pname)
            pfun = descriptors.pop(pname, {})
            pattrs[ptrans] = PropertyDescriptor(
                pname,
                ptype,
                pfun.get('get'),
                pfun.get('set'),
                pfun.get('del'),
                ptype._schema.get('description'))
        # remaining descriptors are properties defined in other bases with local getter/setter/deleter definitions
        for pname, pfun in descriptors.items():
            ptrans = clean_js_name(pname)
            for b in pbases:
                if hasattr(b, ptrans) and isinstance(b, PropertyDescriptor):
                    d = copy.copy(getattr(b.trans))
                    for k, v in pfun.items():
                        if v is not None:
                            setattr(d, f'f{k}', v)
                    attrs[ptrans] = d
                    break

        # set the attributes
        attrs['_properties_translation'] = properties_translation
        attrs['_extends'] = extends
        attrs['_properties'] = all_properties
        attrs['_pattern_properties'] = set().union(pattern_properties, *[b._pattern_properties for b in pbases])
        attrs['_additional_properties'] = additional_properties
        attrs['_not_serialized'] = not_serialized
        attrs['_required'] = required
        attrs['_has_default'] = has_default
        attrs['_read_only'] = read_only
        attrs['_dependencies'] = dependencies
        attrs['_outputs'] = outputs
        attrs['_logger'] = logger
        attrs['_schema'] = ChainMap(schema, *[getattr(b, '_schema', {}) for b in bases])
        attrs.setdefault('_lazy_loading', LAZY_LOADING)
        attrs.setdefault('_attribute_by_name', ATTRIBUTE_BY_NAME)
        attrs['_property_type_cache'] = None
        attrs['_schema_id'] = id
        attrs['_id'] = id
        attrs['_validator'] = DefaultValidator(schema, resolver=UriResolver.create(uri=id, schema=schema))
        # add inner definitions
        for k, d in defs.items():
            attrs[k] = d
        # add properties
        for k, p in pattrs.items():
            attrs[k] = p

        bases = tuple(bases_extended + bases)
        if not_ready_yet:
            logger.warning('removing bases not ready %s' % not_ready_yet)
            bases = tuple(b for b in bases if b not in not_ready_yet)

        cls = type(clsname, bases, attrs)
        cls._py_type = cls
        return cls

    @classmethod
    def extend_type(cls, *bases, **schema):
        if bases or schema:
            return ObjectProtocol.build(cls._id, schema, (cls, *bases))
        return cls

    @property
    def session(self):
        return self._root._repo.session

    #schema = PropertyDescriptor('$schema', _properties['$schema'])
    #id = PropertyDescriptor('$id', _properties['$id'])

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import six
import logging
import dpath.util
from collections.abc import MutableMapping, Mapping
from collections import OrderedDict, defaultdict
import re
from operator import neg
import copy
import gettext

from ..exceptions import InvalidValue
from ..utils import ReadOnlyChainMap as ChainMap, shorten, is_mapping
from .. import decorators
from ..resolvers.uri_resolver import UriResolver, resolve_uri
from ..datatypes.array import Array
from ..datatypes.type import Primitive
from ..datatypes.numerics import Integer
from ..datatypes.object import Object, ObjectSerializer, ObjectDeserializer
from ..datatypes.symbols import Function, Class
from ..datatypes.uri import Id, scope
from ..managers.type_builder import DefaultValidator
from ..managers.namespace_manager import default_ns_manager, clean_js_name
from ..contexts.object_protocol_context import ObjectProtocolContext
from .. import settings
from .serializer import Serializer
from .type_protocol import TypeProtocol
from .collection_protocol import CollectionProtocol

_ = gettext.gettext

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD
ADD_LOGGING = settings.DEFAULT_ADD_LOGGING
ASSERT_ARGS = settings.DEFAULT_ASSERT_ARGS
LOGGER_LEVEL = settings.DEFAULT_LOGGER_LEVEL
ATTRIBUTE_BY_NAME = settings.DEFAULT_COLLECTION_ATTRIBUTE_BY_NAME
SCHEMA_DEF_KEYS = settings.SCHEMA_DEF_KEYS
PROP_PREF = {
    'get': settings.GETTER_PREFIX,
    'set': settings.SETTER_PREFIX,
    'del': settings.DELETER_PREFIX,
}

_ngoinsp_loading_error_msg = False


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
            if self.fget and obj._dataValidated.get(key) is None:
                outdated = True
            #if outdated or self.fget: # or self.fset:
            if outdated:
                # calling once here and just called it in _is_outdated
                inputs = obj._items_inputs_evaluate(key)
                if self.fget:
                    obj._set_data(key, self.fget(obj))
                iopts = {'validate': False} if key in obj._notValidated else {}
                obj._set_dataValidated(key, obj._items_evaluate(key, **iopts))
                obj._itemsInputs[key] = inputs  # after set_validated_data as it touches inputs data
            value = obj._dataValidated[key]
            if outdated and self.fset:
                self.fset(obj, value)
            # value can change in setter (??really ???)
            return obj._dataValidated[key]
        except Exception as er:
            obj._logger.error(er, exc_info=True)
            raise
            #etype, value, trace = sys.exc_info()
            #raise six.reraise(AttributeError, value, trace)

    def __set__(self, obj, value):
        try:
            key = self.pname
            if key in obj._readOnly:
                raise AttributeError("'%s' is read only" % key)
            obj._set_data(key, value)
            if not obj._lazyLoading:
                obj._itemsInputs[key] = obj._items_inputs_evaluate(key)
                iopts = {'validate': False} if key in obj._notValidated else {}
                obj._set_dataValidated(key, obj._items_evaluate(key, **iopts))
                if self.fset:
                    self.fset(obj, obj._dataValidated[key])
        except Exception as er:
            obj._logger.error(er, exc_info=True)
            raise
            #etype, value, trace = sys.exc_info()
            #raise six.reraise(AttributeError, value, trace)

    def __delete__(self, obj):
        key = self.pname
        if key in obj._required:
            raise AttributeError('%s is a required argument.' % key)
        if self.fdel:
            self.fdel(obj)
        del obj._data[key]
        del obj._dataValidated[key]
        del obj._itemsInputs[key]
        # just added, not tested...
        if key in obj._dependencies:
            del obj._dependencies[key]
        for vs in obj._dependencies.values():
            if key in vs:
                vs.pop(vs.index(key))


class ObjectProtocol(ObjectProtocolContext, CollectionProtocol, Object, MutableMapping):
    _("""
    ObjectProtocol is class defined by a json-schema and built by TypeBuilder.build_object_protocol.
    The schema is specified directly by a protected attribute _schema or by providing its id using a protected
    attribute _id to be resolved in loaded schemas.

    The class is built with an ordered dictionary of property types (which can be Literal or a subclass of
    ObjectProtocol or ArrayProtocol.

    An instance behave as a standard mapping, but its properties can also be accessed through a
    descriptor (renamed using clean_js_name in case it contains forbidden characters in python arguments).
    When _attributeByName is enabled, attributes can be accessed also by their names according to setting ATTRIBUTE_NAME_FIELD

    If lazy loading is enabled, data is only constructed and validated on first read access. If not, validation is done
    when setting the item.
    """)
    _serializer = ObjectSerializer
    _deserializer = ObjectDeserializer
    _collection = Object
    _data = {}
    _dataValidated = {}
    _dataAdditional = {}
    _itemsInputs = {}
    _attributesOrig = set()

    _attributeByName = ATTRIBUTE_BY_NAME

    _extends = []
    _extendsProxy = []
    _abstract = False
    _pbases = []
    _pbasesProxy = []
    _methods = {}
    _methodsInherited = {}
    _methodsChained = {}
    _propertiesAllowed = set()
    _propertiesTranslation = {}
    _relationships = {}
    _inversesOf = {}
    _supersededBy = {}
    _aliases = {}
    _aliasesNegated = {}

    def __new__(cls, *args, **kwargs):
        from ..managers import type_builder
        data = args[0] if args else kwargs
        if isinstance(data, Mapping) and data.get('$schema'):
            s_id = Id.convert(scope(data.pop('$schema'), cls._id), **kwargs)
            if s_id != cls._id:
                cls = type_builder.load(s_id)
                return cls(*args, **kwargs)
        return super(ObjectProtocol, cls).__new__(cls)

    @staticmethod
    def _check(self, value, **opts):
        if not isinstance(value, Mapping):
            raise TypeError('%s if not of type mapping.' % value)
        value = self._collType(value)
        keys = set(value)
        for k1, k2 in ChainMap(self._propertiesTranslation, self._aliases, self._aliasesNegated).items():
            if k1 in keys:
                value[k2] = value.pop(k1)
        for k in self._notValidated:
            value.pop(k, None)
        return CollectionProtocol._check(self, value, **opts)

    @staticmethod
    def _convert(self, value, **opts):
        from ..managers.type_builder import type_builder
        #value = self._collType(value)
        if value.get('$schema'):
            s_id = Id.convert(scope(value.pop('$schema'), self._id), **opts)
            if s_id != self._id:
                self = type_builder.load(s_id)
        return CollectionProtocol._convert(self, value, **opts)

    @staticmethod
    def _call_order(self, value, items=True, **opts):
        # make a local copy which is transfered to the sorter
        dependencies = defaultdict(set, **self._dependencies)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    v = value.get(k)
                    if v is None and t.has_default():
                        v = t.default(raw_literals=True, **opts)
                    inputs = [i.split('.')[0] for i in t._inputs(t, v)] if v else []
                    if inputs:
                        dependencies[k].update([i for i in inputs if i in self._properties])
        return self._deserializer.call_order(value, dependencies=dependencies, **opts)

    @staticmethod
    def _deserialize(self, value, raw_literals=False, **opts):
        from ..managers.type_builder import type_builder
        if value is None:
            return value
        if isinstance(value, str):
            value = {'name': value}
        value = dict(value)
        # handle subclassing
        if value.get('$schema'):
            s_id = Id.convert(scope(value.pop('$schema'), self._id), **opts)
            if s_id != self._id:
                self = type_builder.load(s_id)
        # handle aliases/property translations
        for k in set(value).difference(self._properties).intersection(self._propertiesTranslation):
            # deals with conflicting properties with identical translated names
            value[self._propertiesTranslation[k]] = value.pop(k)
        value.update({k2: value.pop(k1) for k1, k2 in self._aliases.items() if k1 in value})
        value.update({k2: - value.pop(k1) for k1, k2 in self._aliasesNegated.items() if k1 in value})
        # use information from context
        if self._useContext:
            ctx = opts.get('context') or self._context
            for c in self._propertiesAllowed.intersection(ctx.keys()):
                value.setdefault(c, ctx[c])
        if not raw_literals:
            # handle canonical names
            cns = [k for k in value.keys() if isinstance(k, str) and '.' in k]
            for cn in cns:
                ps = [Integer.convert(c) if Integer.check(c, convert=True) else c for c in cn.split('.')]
                dpath.util.new(value, cn.split('.'), value.pop(cn))
                cur = value
                for i, p in enumerate(ps):
                    v = cur[p]
                    if Integer.check(p):
                        v = cur[p] = [None] * p + [v]
                    cur = v
        # required with default
        return self._collection._deserialize(self, value, **opts)

    @staticmethod
    def _has_default(self, value=None, **opts):
        value = self._default if value is None else value
        return bool(value) or self._schema.get('default') is not None

    @classmethod
    def default(cls, value=None, evaluate=False, **opts):
        dft = Object.default(cls, value, evaluate=evaluate, **opts)
        return cls(dft, **opts) if evaluate else dft

    def is_default(self, key):
        raw = self._properties_raw_trans(key)[0]
        if raw in self._propertiesWithDefault:
            t = self.items_type(raw)
            v = self[raw]
            if t._has_default(t):
                d = t.default(context=self._context, raw_literals=True)
                d = t(d, context=self._context)
                if v == d:
                    return True
        return False

    @staticmethod
    def _create_context(self, *extra_contexts, context=None, **local):
        return CollectionProtocol._create_context(self, {'this': self}, self._dataValidated, self, *extra_contexts,
                                                  context=context, **local)

    def _items_touch(self, item):
        CollectionProtocol._items_touch(self, item)
        for d, s in self._dependencies.items():
            if item in s:
                self._items_touch(d)

    def _touch(self):
        CollectionProtocol._touch(self)
        keys = list(self._data.keys())
        self._itemsInputs = {k: {} for k in keys}
        self._dataValidated = {k: None for k in keys}
        self._dataAdditional = {k: None for k in self._dataAdditional.keys()}
        self._dependencies = dict(self.__class__._dependencies)

    def __eq__(self, other, parents=tuple()):
        if other is None:
            return False
        if other is self:
            return True
        if self in parents:
            return True
        if not isinstance(other, Mapping):
            return False
        s1 = set(self.keys())
        s2 = set(other.keys())
        if s1 != s2:
            return False
        for k in list(s1):
            v = other[k]
            v2 = self[k]
            if isinstance(v2, CollectionProtocol):
                if not v2.__class__.__eq__(v2, v, parents=parents+(self, )):
                    return False
            elif v2 != v:
                return False
        return True

    def copy(self, _parents=tuple()):
        for orig, copy in _parents:
            if self is orig:
                return copy
        self.do_validate(items=True)
        copy = self.create({k: v for k, v in self._dataValidated.items() if k not in self._readOnly}, context=self._context, validate=False, lazy_loading=True)
        for k, v in copy._data.items():
            if isinstance(v, CollectionProtocol):
                copy._data[k] = v.copy(_parents=_parents + ((self, copy), ))
        copy.do_validate()
        return copy

    def diff(self, other, excludes=[], parents=tuple()):
        if not isinstance(other, Mapping):
            raise other
        if self in parents:
            return
        s1 = set(self.keys())
        s2 = set(other.keys())
        return {k: self[k].diff(other[k], parents=parents+(self, )) if isinstance(self[k], CollectionProtocol) else other[k]\
                for k in list(s1.intersection(s2).difference(excludes)) if not k.startswith('_') and self[k] != other[k]}

    def __len__(self):
        return len(self._dataValidated)

    def __iter__(self):
        yield from self._dataValidated.keys()

    def __next__(self):
        yield from self._dataValidated.keys()

    def _is_outdated(self, item):
        if self._data.get(item) is not None and self._dataValidated.get(item) is None:
            return True
        for v in self._dependencies.get(item, set()):
            cur = self
            vs = v.split('.')
            lvs = len(vs)
            for i, vv in enumerate(vs):
                if cur._is_outdated(vv):
                    return True
                if len(vs) > 1 and i != len(vs) - 1:
                    cur = cur.get(vv)
                    if cur is None:
                        break
        return False
        old_inputs = self._itemsInputs.get(item, {})
        new_inputs = self._items_inputs_evaluate(item)
        if set(old_inputs.keys()) != set(new_inputs.keys()):
            return True
        for k, nv in new_inputs.items():
            ov = old_inputs[k]
            if isinstance(ov, (DataFrame, Series)):
                if id(ov) != id(nv):
                    return True
            elif ov != nv:
                return True
        return False
        return (self._dataValidated[item] is None and self._data[item] is not None
                ) or (self._itemsInputs.get(item, {}) != self._items_inputs_evaluate(item))

    def _get_data(self, item):
        raw, trans = self._properties_raw_trans(item)
        if '.' in raw:
            cns = raw.split('.')
            cur = self
            for cn in cns:
                value = cur = cur._get_data(cn) if isinstance(cur, ObjectProtocol) else cur[cn]
                if value is None:
                    break
            return value
        value = CollectionProtocol._get_data(self, trans)
        return - value if raw in self._aliasesNegated else value

    __properties_raw_trans = None
    @classmethod
    def _properties_raw_trans(cls, name):
        if cls.__properties_raw_trans is None:
            cls.__properties_raw_trans = {}
        cached = cls.__properties_raw_trans.get(name)
        if cached:
            return cached
        if name in cls._properties:
            cls.__properties_raw_trans[name] = (name, name)
            return name, name
        for trans, raw in cls._propertiesTranslation.items():
            if name in (raw, trans):
                cls.__properties_raw_trans[name] = (raw, trans)
                return raw, trans
        alias = cls._aliases.get(name)
        if alias:
            cls.__properties_raw_trans[name] = (alias, name)
            #return name, alias
            return alias, name
        alias = cls._aliasesNegated.get(name)
        if alias:
            cls.__properties_raw_trans[name] = (alias, name)
            #return name, alias
            return alias, name
        if cls._propertiesAdditional:
            trans = clean_js_name(name) if isinstance(name, str) else name
            cls.__properties_raw_trans[name] = (name, trans)
            return name, trans
        #cls.__properties_raw_trans[name] = (None, None)
        return None, None

    def __getattr__(self, name):
        # private and protected attributes at accessed directly
        if name.startswith('_') or name in self._attributesOrig:
            if name.startswith('__'):
                return MutableMapping.__getattribute__(self, name)
            if name not in self._propertiesAllowed:
                return MutableMapping.__getattribute__(self, name)
                return self.__dict__[name]
        op = lambda x: neg(x) if name in self._aliasesNegated else x
        name = self._aliasesNegated.get(name, name)
        name = self._aliases.get(name, name)
        if '.' in name:
            return self[name]
        raw = self._propertiesTranslation.get(name, name)
        desc = self._propertiesDescriptor.get(raw) or self._relationshipsDescriptor.get(raw)
        if desc:
            return op(desc.__get__(self))
        if name in self._supersededBy:
            ss = self[self._supersededBy[name]]
            return ss[0] if len(ss) else None
        if self._propertiesAdditional and name in self._data:
            self._itemsInputs[raw] = self._items_inputs_evaluate(name)
            self._dataAdditional[raw] = v = op(self[name])
            return v
        if self._attributeByName:
            try:
                return op(self.resolve_cname([name]))
            except Exception as er:
                self._logger.error(er, exc_info=True)
                raise
        if not self._propertiesAdditional:
            # additional properties not allowed, raise exception
            raise AttributeError("'{0}' is not a valid property of {1}".format(
                                name, self.__class__.__name__))
        if name not in self._required:
            return
        raise AttributeError("'{0}' has not been set to {1}".format(
                                name, self.__class__.__name__))

    @classmethod
    def __subclasshook__(cls, subclass):
        """Override for issubclass(subclass, cls)."""
        # cls is subclass or cls in subclass parents
        subklass = subclass if not hasattr(subclass, '_proxyUri') else subclass.proxy_type()
        if cls in subklass.__mro__:
            return True
        else:
            return getattr(cls, '_id', None) in getattr(subklass, '_extendsProxy', [])

    def resolve_cname_path(self, cname):
        from ..models.instances import Instance
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
                        if Object.check(v) or Array.check(v, split_string=False):
                            for _ in _resolve_cname_path(cn, v, cn2, cur_path + [k]):
                                yield _
            if Array.check(cur, split_string=False):
                for i, v in enumerate(cur):
                    for _ in _resolve_cname_path(cn, v, cur_cn, cur_path + [i]):
                        yield _

        cname = [self.name] if isinstance(self, Instance) else []
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
        if name.startswith('_'):  # or name in self._attributesOrig:
            if name not in self._propertiesAllowed:
                self.__dict__[name] = value
                return
        try:
            self[name] = value
        except KeyError as er:
            #self._logger.error(er, exc_info=True)
            raise AttributeError("'{0}' is not a valid property of {1}".format(
                                 name, self.__class__.__name__))

    def __getitem__(self, key):
        if key is None:
            return self._parent
        key = self._aliases.get(key, key)
        if isinstance(key, str) and '.' in key:
            parts = split_cname(key)
            # case: canonical name such as a[0][1].b[0].c
            cur = self
            try:
                for p in parts:
                    cur = cur[p] if not hasattr(cur, p) else getattr(cur, p)
                    if cur is None:
                        return
                return cur
            except Exception as er:
                raise KeyError(key)
        desc = self._relationshipsDescriptor.get(key)
        if desc:
            return desc.__get__(self)
        op = lambda x: neg(x) if key in self._aliasesNegated else x
        raw, trans = self._properties_raw_trans(key)
        if raw not in self._data:
            raise KeyError(key)
        desc = self._propertiesDescriptor.get(raw)
        if desc:
            return op(desc.__get__(self))
        if raw in self._supersededBy:
            ss = self[self._supersededBy[raw]]
            return ss[0] if len(ss) else None
        if self._lazyLoading or self._is_outdated(key):
            self._itemsInputs[key] = self._items_inputs_evaluate(key)
            self._set_dataValidated(key, self._items_evaluate(key))
        return op(self._dataValidated[key])

    def __setitem__(self, key, value):
        op = lambda x: neg(x) if key in self._aliasesNegated else x
        key = self._aliasesNegated.get(key, key)
        key = self._aliases.get(key, key)
        if '.' in key:
            parts = split_cname(key) # case: canonical name such as a[0][1].b[0].c
            cur = self
            try:
                for p in parts[:-1]:
                    cp = cur[p] if not hasattr(cur, p) else getattr(cur, p)
                    if cp is None:
                        # if intermediate object is None, create an empty one
                        cur[p] = {}
                        cp = cur[p]
                    if hasattr(cur, 'items_touch'):  # just added
                        cur._items_touch(p)
                    cur = cp
                cur[parts[-1]] = value
                return
            except Exception as er:
                raise KeyError(key)
        raw, trans = self._properties_raw_trans(key)
        desc = self._propertiesDescriptor.get(raw) or self._relationshipsDescriptor.get(raw)
        if desc:
            return desc.__set__(self, op(value))
        if raw in self._supersededBy:
            return self[self._supersededBy[raw]].insert(value, 0)
        if not self._propertiesAdditional:
            raise KeyError(key)
        v = op(value)
        changed = v != self._data.get(key)
        if changed:
            self._items_touch(key)
        self._data[key] = self._dataAdditional[key] = self._dataValidated[key] = v

    def __delitem__(self, key):
        key = self._aliasesNegated.get(key, key)
        key = self._aliases.get(key, key)
        if '.' in key:
            parts = split_cname(key) # case: canonical name such as a[0][1].b[0].c
            cur = self
            try:
                for p in parts[:-1]:
                    cp = cur[p] if not hasattr(cur, p) else getattr(cur, p)
                    if cp is None:
                        # if intermediate object is None, create an empty one
                        cur[p] = {}
                        cp = cur[p]
                    if hasattr(cur, 'items_touch'):  # just added
                        cur._items_touch(p)
                    cur = cp
                del cur[parts[-1]]
                return
            except Exception as er:
                raise KeyError(key)
        for trans, raw in self._propertiesTranslation.items():
            if key in (trans, raw):
                delattr(self, trans)
                break
        else:
            del self._data[key]
            del self._itemsInputs[key]
            del self._dataValidated[key]

    def __contains__(self, key):
        try:
            # differs from the abc version which only checks key error
            # it seems more interesting to push the test to know if s not None
            return self[key] is not None
        except KeyError:
            return False
        else:
            return True

    @staticmethod
    def _serialize(self, value, schema=False, excludes=[], only=[], aliases=None, **opts):
        serializer = self if not isinstance(value, Serializer) else value.__class__
        context = getattr(value, '_context', self._context)
        attr_prefix = opts.get('attr_prefix', self._attrPrefix)
        if not isinstance(value, Mapping):  # hack for attributes initialized with fake objects
            value = {str(value): {}}
        ret = self._collection._serialize(serializer, value, excludes=excludes, only=only, **opts)
        ret = self._collType([((attr_prefix if self._items_type(serializer, k).is_primitive() else '') + k, ret[k])
                                for k in ret.keys()])
        aliases = dict(**self._aliases, **(aliases or {}))
        for alias, raw in aliases.items():
            if only and alias not in only:
                continue
            if alias not in excludes:
                v = ret.get(raw)
                v = value.get(raw) if v is None else v
                if v is not None:
                    # here we pop the alias reference
                    ret[(attr_prefix if self._items_type(self, raw).is_primitive() else '') + alias] = ret.pop(raw, v)
        for alias, raw in self._aliasesNegated.items():
            if only and alias not in only:
                continue
            if alias not in excludes:
                v = ret.get(raw)
                v = value.items_serialize(raw) if v is None else v
                if v is not None:
                    ret[(attr_prefix if self._items_type(self, raw).is_primitive() else '') + alias] = - v
        if isinstance(value, ObjectProtocol) and value._id != self._id:
            schema = True
        if schema:
            ret['$schema'] = Id.serialize(value._id, context=context)
            ret.move_to_end('$schema', False)
        return ret

    def __repr__(self):
        if self._repr is None:
            m = settings.PPRINT_MAX_EL
            ks = list(self._print_order(self, self._data, no_defaults=True, no_readOnly=True))
            hidden = max(0, len(ks) - m)
            #a = ['%s=%s' % (k, shorten(self._dataValidated[k] or self._data[k], str_fun=repr)) for k in ks[:m]]
            a = ['%s=%s' % (k, shorten(self._dataValidated[k] if self._dataValidated[k] is not None else self._data[k], str_fun=repr)) for k in ks[:m]]
            #a = ['%s=%s' % (k, shorten(self._dataValidated[k] if self._dataValidated[k] is not None else self._data[k]), str_fun=repr)) for k in ks[:m]]
            a += ['+%i...' % hidden] if hidden else []
            self._repr = '%s(%s)' % (self.qualname(), ', '.join(a))
        return self._repr

    def __str__(self):
        if self._str is None:
            m = settings.PPRINT_MAX_EL
            ks = list(self._print_order(self, self._data, no_defaults=True, no_readOnly=False))
            hidden = max(0, len(ks) - m)
            #a = ['%s: %s' % (k, shorten(self._dataValidated[k] or self._data[k], str_fun=repr)) for k in ks[:m]]
            a = ['%s: %s' % (k, shorten(self._dataValidated[k] if self._dataValidated[k] is not None else self._data[k], str_fun=repr)) for k in ks[:m]]
            a += ['+%i...' % hidden] if hidden else []
            self._str = '{%s}' % (', '.join(a))
        return self._str

    @classmethod
    def dosctring(cls, arguments=True, methods=True, methods_inherited=True):
        txt = cls.__doc__
        title = cls._title
        description = cls._description
        local_properties = cls._propertiesLocal

        doc = f'{title}\n\n{description or ""}\n\n'
        if local_properties:
            doc += _('ARGUMENTS:') + '\n'
            for a, p in local_properties.items():
                desc = p._description or p._title or ''
                pt = p._schema.get('type')
                if p._schema.get('$ref'):
                    pt = pt.__name__
                if pt == 'array':
                    pt = 'list'
                    if p._items:  # to remove items set to True
                        if not p._itemsIsList and p._items.is_constant():
                            pass
                        else:
                            items = p._items if p._itemsIsList else [p._items]
                            items = [getattr(i, '__name__', i._schema.get('type')) for i in items]
                            pt += f'[{", ".join(items)}]'
                doc += f'\t:param {a}: {_(desc)}\n'
                doc += f'\t:type {a}: {pt}\n'
            if cls._pbases:
                doc += _('Inherits from:') + '\n'
                doc += '\t' + ', '.join([pb.__name__ for pb in cls._pbases])

        def append_doc_dict(dict, title):
            global txt
            txt += '\n' + title + '\n'
            for k, m in dict.items():
                txt += '\t' + k
                if m.__doc__:
                    txt += ':\t' + m.__doc__.splitlines()[0]

        if methods and cls._methods:
            append_doc_dict(cls._methods, _('METHODS'))
        if methods_inherited and cls._methodsInherited:
            append_doc_dict(cls._methodsInherited, _('METHODS INHERITED'))
        return txt

    @staticmethod
    def _items_type(self, item):
        # add a cache to resolve type proxies and avoid property resolution
        from .type_proxy import TypeProxy
        t = self._items_type_cache.get(item)
        if t is None:
            i = self._aliases.get(item, item)
            i = self._aliasesNegated.get(item, item)
            t = Object._items_type(self, i)
            self._items_type_cache[item] = t
            if t and hasattr(t, '_proxyUri'):
                p = t.proxy_type()
                if p:
                    self._items_type_cache[item] = t = p
                else:
                    self._items_type_cache[item] = None  # not ready yet
        return t

    @staticmethod
    def build(id, schema, bases=(), attrs=None):
        from ..managers.type_builder import type_builder, scope
        from ..managers.relationship_builder import RelationshipDescriptor, RelationshipBuilder, relationship_builder
        from ..protocols import TypeProxy
        from ..contexts.entity_context import EntityContext
        try:
            from ngoinsp.inspectors.inspect_symbols import inspect_function
        except Exception as er:
            global _ngoinsp_loading_error_msg
            if not _ngoinsp_loading_error_msg:
                logging.debug('Optional module ngoinsp not found.')
                _ngoinsp_loading_error_msg = True
            inspect_function = lambda x: {'arguments': []}
        attrs = attrs or {}
        cname = default_ns_manager.get_id_cname(id)
        clsname = attrs.pop('_clsname', None) or cname.split('.')[-1]

        # create/set logger
        logger = logging.getLogger(cname)
        level = logging.getLevelName(attrs.get('_logLevel', LOGGER_LEVEL))
        logger.setLevel(level)
        attributes_orig = set([k for k in attrs.keys() if not k.startswith('__')])

        if schema.get('$schema'):
            # todo remove the following as never used?
            # raise
            ms_uri = schema['$schema']
            metaschema = resolve_uri(ms_uri)
            resolver = UriResolver.create(uri=id, schema=schema)
            meta_validator = DefaultValidator(metaschema, resolver=resolver)
            meta_validator.validate(schema)

        abstract = schema.get('abstract', False)
        description = schema.get('description')
        comment = schema.get('$comment')
        title = schema.get('title', clsname)


        bases_extended = [type_builder.load(scope(e, id)) for e in schema.get('extends', [])]
        bases_extended = [e for e in bases_extended if not any(issubclass(b, e) for b in bases)]
        wraps = schema.get('wraps')
        if wraps and Class.check(wraps, convert=True):
            wraps = Class.convert(wraps)
        #if wraps:
        #    if Class.check(wraps, convert=True):
        #        wraps_s = Class.convert(wraps)
        #        if wraps_s not in bases:
        #            bases = bases + (wraps_s, )
        #    else:
        #        logger.debug("%s not set to wrap %s." % (wraps, clsname))
        pbases = [b for b in bases if issubclass(b, ObjectProtocol) and not any(issubclass(e, b) for e in bases_extended)]
        bases = [b for b in bases if not any(issubclass(e, b) for e in bases_extended)]
        pbases = pbases + bases_extended
        # get entity type parents testing EntityContext and excluding the Entity class
        is_entity = any([issubclass(b, EntityContext) for b in pbases])
        ebases = [b for b in pbases if issubclass(b, EntityContext) and b.__name__ not in ['Entity', 'EntityNode']]

        not_ready_yet = tuple(b for b in pbases if issubclass(b, TypeProxy) and b.proxy_type() is None)
        not_ready_yet_sch = tuple(type_builder.expand(b._proxyUri) for b in not_ready_yet)
        pbases = tuple(b for b in pbases if b not in not_ready_yet)
        if not pbases:
            bases += [ObjectProtocol]

        if not wraps:
            bases_wraps = [b._wraps for b in pbases if b._wraps]
            if bases_wraps:
                wraps = bases_wraps[0]


        # create an aliases dictionary from all bases dependencies
        aliases = dict(ChainMap(schema.get('aliases', {}), *[b._aliases for b in pbases]))
        negated_aliases = dict(ChainMap(schema.get('negatedAliases', {}), *[b._aliasesNegated for b in pbases]))
        properties_translation = {}
        aks = set(aliases.keys())
        naks = set(negated_aliases.keys())

        # building inner definitions
        defs = {dn: type_builder.load(f'{id}/$defs/{dn}') for dn, defn in schema.get('$defs', {}).items()}

        # create a dependency dictionary from all bases dependencies
        dependencies = defaultdict(set)
        for s in not_ready_yet_sch:
            for k, v in s.get('dependencies', {}).items():
                dependencies[k].update(set(v))
        for b in pbases:
            for k, v in getattr(b, '_dependencies', {}).items():
                dependencies[k].update(set(v))
        for k, v in schema.get('dependencies', {}).items():
            # replace aliases
            vs = list(v)
            for i, v in enumerate(vs):
                v0 = v.split('.')[0]
                if v0 in aks:
                    v = v.replace(v0, aliases[v0])
                if v0 in naks:
                    v = v.replace(v0, negated_aliases[v0])
                vs[i] = v
            dependencies[k].update(set(vs))

        if is_entity:
            primary_keys = list(attrs.get('_primaryKeys', schema.get('primaryKeys', [])))
            if not primary_keys:
                for b in pbases:
                    primary_keys += [k for k in getattr(b, '_primaryKeys', []) if k not in primary_keys]
            if primary_keys:
                dependencies['identityKeys'] = set(primary_keys)

        methods = {}

        extends = [b._id for b in pbases if b._id] + [b._proxyUri for b in not_ready_yet]
        not_serialized = set().union(schema.get('notSerialized', attrs.get('_notSerialized', [])), *[b._notSerialized for b in pbases], *[s.get('notSerialized', []) for s in not_ready_yet_sch])
        not_validated = set().union(schema.get('notValidated', attrs.get('_notValidated', [])), *[b._notValidated for b in pbases], *[s.get('notValidated', []) for s in not_ready_yet_sch])
        required = set().union(schema.get('required', attrs.get('_required', [])), *[b._required for b in pbases], *[s.get('required', []) for s in not_ready_yet_sch])
        read_only = set().union(schema.get('readOnly', attrs.get('_readOnly', [])), *[b._readOnly for b in pbases], *[s.get('readOnly', []) for s in not_ready_yet_sch])
        has_default = set().union(*[b._propertiesWithDefault for b in pbases])

        # extends flattened for proxies
        extends_proxies_flattened = []
        def flatten_proxy_extends(proxy_id):
            extends_proxies_flattened.append(proxy_id)
            proxy_sch = resolve_uri(proxy_id)
            for e in proxy_sch.get('extends', []):
                flatten_proxy_extends(scope(e, proxy_id))
        for b in not_ready_yet:
            flatten_proxy_extends(b._proxyUri)
        # add extends proxies of ancesters
        for b in pbases:
            if b._extendsProxy:
                extends_proxies_flattened.extend(b._extendsProxy)
        # remove duplicates, order should not import
        extends_proxies_flattened = list(set(extends_proxies_flattened))

        # create type for properties
        local_properties = OrderedDict([(k, type_builder.build(f'{id}/properties/{k}', v))
                                  for k, v in schema.get('properties', {}).items()])
        # gathers superseded properties (local and inherited)
        supersededBy = ChainMap({v['supersedes']: k for k, v in schema.get('properties', {}).items()
                                 if is_mapping(v) and 'supersedes' in v},
                                *[b._supersededBy for b in pbases])
        inversesOf = ChainMap({v['inverseOf']: k for k, v in schema.get('properties', {}).items()
                               if is_mapping(v) and 'inverseOf' in v},
                                *[b._inversesOf for b in pbases])
        redefined_properties = OrderedDict()
        for i, s in zip(not_ready_yet, not_ready_yet_sch):
            for k, v in s.get('properties', {}).items():
                redefined_properties[k] = type_builder.build(f'{id}/properties/{k}', v)
        all_properties = ChainMap(local_properties, redefined_properties, *[b._propertiesChained for b in pbases])
        pattern_properties = set([(re.compile(k),
                                   type_builder.build(f'{id}/patternProperties/{k}', v))
                                   for k, v in schema.get('patternProperties', {}).items()])
        additional_properties = type_builder.build(f'{id}/additionalProperties', schema.get('additionalProperties', True))

        local_relationships = OrderedDict([(k, relationship_builder.build(f'{id}/relationships/{k}', v))
                                  for k, v in schema.get('relationships', {}).items()])
        local_relationships_descriptor = OrderedDict()
        relationships = ChainMap(local_relationships, *[b._relationships for b in pbases])
        # add foreign keys from inherited entities
        from inflection import underscore
        for b in ebases:
            rname = underscore(b.__name__)
            if not len(b._primaryKeys):
                if b._abstract:
                    continue
                raise InvalidValue(_("Entity class '%s' is not abstract and has no primary keys defined." % rname))
            pks = b._primaryKeys
            pname = rname + '_' + '_'.join(pks)
            ptype = b._properties[pks[0]]._type if len(pks) == 1 else 'array'
            psch = {'type': ptype, 'foreignKey': {'foreignSchema': b._id, 'foreignKeys': pks}}
            local_properties[pname] = type_builder.build(f'{id}/properties/{pname}', psch)
            rsch = {'foreignSchema': b._id, 'foreignKeys': [pname], 'inheritance': True}
            local_relationships[rname] = rl = relationship_builder.build(f'{id}/relationships/{rname}', rsch)
            local_relationships_descriptor[rname] = RelationshipDescriptor(pname, rl)
        # add relationships related to local properties
        for k, v in schema.get('properties', {}).items():
            if Object.check(v) and 'foreignKey' in v:
                rs = v['foreignKey']
                ra = {}
                # treat backpopulates
                bps = v.get('backPopulates', {})
                if not bps:
                    # add a pointer
                    bps[f'{k}_ptr'] = {'foreignSchema': scope(rs['foreignSchema'], id), 'foreignKeys': [k]}
                for kbp, bp in bps.items():
                    local_relationships[kbp] = rl = relationship_builder.build(f'{id}/relationships/{kbp}', bp, attrs=ra)
                    #local_relationships[rn] = rl = RelationshipBuilder.build(f'{id}/relationships/{rn}', rs, attrs=ra)
                    local_relationships_descriptor[kbp] = RelationshipDescriptor(k, rl)

        # add some magic on methods defined in class
        # exception handling, argument conversion/validation, dependencies, etc...
        add_logging = attrs.get('_add_logging', ADD_LOGGING)
        assert_args = attrs.get('_assert_args', ASSERT_ARGS)
        for k, v in attrs.items():
            if isinstance(v, TypeProtocol):
                schema[k] = v._schema
            if Function.check(v):
                f = v
                if not k.startswith('_'):
                    methods[k] = f
                if add_logging:
                    if k == '__init__':
                        f = decorators.log_init(f)
                if assert_args and f.__doc__:
                    from ..datatypes import Type
                    fi = inspect_function(f)
                    if 'assert_arg' in [d['name'] for d in fi.get('decorators', [])]:
                        # function is already using assert_arg
                        continue
                    for pos, a in enumerate(fi['arguments']):
                        t = a.get('type', False)
                        if t:
                            # only assert args which are defined
                            logger.debug(
                                "decorate <%s>.%s with argument %i validity check.",
                                clsname, k, pos)
                            f = decorators.assert_arg(pos, Type, **a)(f)
                # add exception logging
                if add_logging and not k.startswith("__"):
                    logger.debug("decorate <%s>.%s with exception logger", clsname, k)
                    f = decorators.log_exceptions(f)
                attrs[k] = f

        # go through attributes to find default values, accessors and additional dependencies
        # store additional data that will be used to rebuild the inner object type with property redefinitions
        def is_symbol(f):
            import types
            from ..decorators import ClassPropertyDescriptor
            return isinstance(f, types.FunctionType) or isinstance(f, classmethod)\
                   or isinstance(f, types.MethodType) or isinstance(f, ClassPropertyDescriptor)

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
                if ptype.check(attr, raw_literals=True, convert=True):
                    # allows to avoid instanciation
                    #v_ = ptype.serialize(
                    #    ptype(attr, items=False, raw_literals=True),
                    #    deserialize=False, no_defaults=True, raw_literals=True)
                    dsv = ptype.deserialize(attr, evaluate=False, items=False, raw_literals=True)
                    v = ptype.serialize(dsv, deserialize=False, no_defaults=True, raw_literals=True)
                    extra_schema_properties[pname] = dict(ptype._schema)
                    extra_schema_properties[pname]['default'] = v
                    has_default.add(pname)
                    #read_only.add(pname)  # as defined in schema attributes or hardcoded
                else:
                    raise InvalidValue("Impossible to get a default value of type '%s' from class attributes '%s' in '%s'." % (
                        ptype._schema.get("type"), pname, clsname))

            pfun = {}
            for prop in ['get', 'set', 'del']:
                fname = f'{PROP_PREF[prop]}{ptrans}'
                fun = attrs.get(fname)
                if not fun:
                    # should we look for setters/getters in bases or pbases?
                    # was it to allow mixins to take over?
                    fun = [getattr(b, fname) for b in pbases if hasattr(b, fname)]
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
            local_properties.update({k: type_builder.build(f'{id}/properties/{k}', sch)
                                     for k, sch in extra_schema_properties.items()})
            schema.setdefault('properties', {})
            schema['properties'].update(extra_schema_properties)

        # create descriptors
        # go through local properties and create descriptors
        properties_descriptor = {}
        for pname, ptype in ChainMap(local_properties, redefined_properties).items():
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
                b_a = getattr(b, ptrans, None)
                if isinstance(b_a, PropertyDescriptor):
                    d = copy.copy(b_a)
                    for k, v in pfun.items():
                        if v is not None:
                            setattr(d, f'f{k}', v)
                    properties_descriptor[pname] = d
                    break

        # create documentation
        doc = f'{title}\n\n{description or ""}\n\n'
        if local_properties:
            doc += _('Arguments:') + '\n'
            for a, p in local_properties.items():
                desc = p._description or p._title or ''
                pt = p._schema.get('type')
                if p._schema.get('$ref'):
                    pt = pt.__name__
                if pt == 'array':
                    pt = 'list'
                    if p._items:  # to remove items set to True
                        if not p._itemsIsList and p._items.is_constant():
                            pass
                        else:
                            items = p._items if p._itemsIsList else [p._items]
                            items = [getattr(i, '__name__', i._schema.get('type')) for i in items]
                            pt += f'[{", ".join(items)}]'
                doc += f'\t:param {a}: {_(desc)}\n'
                doc += f'\t:type {a}: {pt}\n'
            if pbases:
                doc += _('Inherits from:') + '\n'
                doc += '\t' + ', '.join([pb.__name__ for pb in pbases])

        # remove aliases now redefined in local properties
        for k in aks.intersection(set(local_properties)):
            del aliases[k]
        for k in naks.intersection(set(local_properties)):
            del negated_aliases[k]

        schema_chained = ChainMap(schema, *[getattr(b, '_schema', {}) for b in bases])
        schema_flattened = dict(schema)
        schema_flattened['required'] = required
        schema_flattened['properties'] = dict(ChainMap(schema.get('properties', {}), *[getattr(b, '_schema', {}).get('properties', {}) for b in bases]))
        schema_flattened['propertiesPattern'] = dict(ChainMap(schema.get('propertiesPattern', {}), *[getattr(b, '_schema', {}).get('propertiesPattern', {}) for b in bases]))
        schema_flattened.pop('extends', None)
        for f in ['required', 'properties', 'propertiesPattern']:
            if not schema_flattened[f]:
                del schema_flattened[f]

        # set the attributes
        attrs['_title'] = _(title)
        attrs['__doc__'] = doc.strip()
        attrs['_description'] = _(description)
        attrs['_comment'] = _(comment)
        attrs['_id'] = id
        attrs['_extends'] = extends
        attrs['_extendsProxy'] = extends_proxies_flattened
        attrs['_schema'] = schema_chained
        attrs['_schemaFlattened'] = schema_flattened
        attrs['_default'] = schema.get('default', ObjectProtocol._default)
        attrs['_wraps'] = wraps
        attrs['_abstract'] = abstract
        attrs['_hasPk'] = is_entity # or bool(primary_keys)
        #attrs['_hasPk'] = tuple(k for k, p in all_properties.items() if len(getattr(p, '_primaryKeys', [])))
        if is_entity:
            attrs['_primaryKeys'] = primary_keys
        #attrs['_properties'] = dict(all_properties)
        # TODO: dict(all_properties) takes a very long time, could it be faster to
        attrs['_properties'] = dict(ChainMap(local_properties, redefined_properties, *[b._properties for b in pbases]))
        attrs['_propertiesChained'] = all_properties
        attrs['_propertiesLocal'] = local_properties
        attrs['_propertiesRedefined'] = redefined_properties
        attrs['_propertiesPattern'] = set().union(pattern_properties, *[b._propertiesPattern for b in pbases])
        attrs['_propertiesAdditional'] = additional_properties
        attrs['_propertiesDescriptor'] = dict(ChainMap(properties_descriptor, *[getattr(b, '_propertiesDescriptor', {})
                                                                                for b in pbases]))
        attrs['_methods'] = methods
        attrs['_methodsInherited'] = dict(ChainMap(*[b._methods for b in pbases],
                                                   *[b._methodsInherited for b in pbases]))
        attrs['_methodsChained'] = dict(ChainMap({id: methods},
                                                 *[b._methodsChained for b in pbases]))
        attrs['_relationships'] = relationships
        attrs['_relationshipsLocal'] = local_relationships
        attrs['_relationshipsDescriptor'] = dict(ChainMap(local_relationships_descriptor,
                                                          *[getattr(b, '_relationshipsDescriptor', {}) for b in pbases]))
        attrs['_required'] = required
        attrs['_dependencies'] = dependencies
        attrs['_readOnly'] = read_only
        attrs['_notSerialized'] = not_serialized
        attrs['_notValidated'] = not_validated
        attrs['_attributesOrig'] = set().union(attributes_orig, *[b._attributesOrig for b in pbases])
        attrs['_propertiesTranslation'] = dict(ChainMap(properties_translation, *[b._propertiesTranslation for b in pbases]))
        attrs['_inversesOf'] = inversesOf
        attrs['_supersededBy'] = supersededBy
        attrs['_aliases'] = aliases
        attrs['_aliasesNegated'] = negated_aliases
        attrs['_propertiesAllowed'] = set(attrs['_properties']).union(attrs['_aliases']).union(attrs['_aliasesNegated']).union(attrs['_propertiesTranslation'])
        attrs['_propertiesWritingAllowed'] = attrs['_propertiesAllowed'].difference(read_only)
        attrs['_propertiesWithDefault'] = has_default
        attrs['_logger'] = logger
        attrs['_jsValidator'] = DefaultValidator(schema, resolver=UriResolver.create(uri=id, schema=schema))
        attrs['_items_type_cache'] = {}
        attrs['_pbases'] = pbases
        attrs['_pbasesProxy'] = tuple(not_ready_yet)
        if 'lazyLoading' in schema:
            attrs['_lazyLoading'] = schema['lazyLoading']
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
            # removing bases not ready. properties have descriptors
            # subclassing is handled in ObjectProtocol.__subclasshook__
            bases = tuple(b for b in bases if b not in not_ready_yet)
        try:
            cls = type(clsname, bases, attrs)
        except Exception as er:
            logger.error(f'Impossible to build {id}: {er}')
            raise
        cls._pyType = cls
        return cls


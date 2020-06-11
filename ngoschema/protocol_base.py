# *- coding: utf-8 -*-
"""
Derived classbuilder from python-jsonschema-object for ngoschema specific
requirements

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 11/06/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

import itertools

import six
import collections
import copy

from ngoschema.utils import get_descendant
from python_jsonschema_objects import \
    classbuilder as pjo_classbuilder, \
    util as pjo_util

from python_jsonschema_objects.validators import ValidationError

from . import utils
from . import mixins
from .mixins import HasLogger
from .resolver import resolve_uri, qualify_ref
from .validators.jsonschema import DefaultValidator
from .utils.json import ProtocolJSONEncoder
from .decorators import classproperty, memoized_property
from .utils import lazy_format
from .wrapper_types import ArrayWrapper
from .literals import LiteralValue


class ProtocolBase(mixins.HasParent, mixins.HasCache, HasLogger, pjo_classbuilder.ProtocolBase):
    __doc__ = pjo_classbuilder.ProtocolBase.__doc__ + """
    
    Protocol shared by all instances created by the class builder. It extends the 
    ProtocolBase object available in python-jsonschema-objects and add some features:

    * string literal value with patterns: a string literal value can be defined as a 
    formatted string which can depend on other properties.
    
    * complex literal types: path/date/datetime are automatically created and can be 
    handled as expected python objects, and will then be properly serialized
    
    * allow lazy loading on member access

    * methods are automatically decorated to add logging possibility, exception handling
    and argument validation/conversion to the proper type (type can be given as a schema
    through a decorator or simply by documenting the docstring with a schema)
    
    * default values can be configured in the config files
    """

    # additional private and protected props
    _validator = None
    __prop_names__ = dict()
    __prop_translated__ = dict()
    __schema_uri__ = 'http://numengo.org/ngoschema#/definitions/ProtocolBase'
    _RO_active = True
    _raw_literals = False

    def __new__(cls,
                *args,
                **props):
        """
        function creating the class with a special treatment to resolve subclassing
        """
        from .resolver import get_resolver
        from .classbuilder import get_builder

        base_uri = cls.__schema_uri__

        if '$ref' in props:
            props.update(resolve_uri(qualify_ref(props.pop('$ref'), base_uri)))

        if '$schema' in props:
            builder = get_builder()
            # handle case $schema is given as a canonical name
            if '/' not in props['$schema']:
                ns_cls, _ = cls.__schema_uri__.split('#')
                ns_name = {uri: name for name, uri in builder.namespaces.items()}.get(ns_cls)
                cn = props['$schema']
                ref = builder.get_cname_ref(cn, **{ns_name: ns_cls})
                props['$schema'] = ref
            if props['$schema'] != cls.__schema_uri__:
                cls = builder.resolve_or_construct(props['$schema'])

        cls.init_class_logger()

        # option to validate arguments at init even if lazy loading
        if cls.__lazy_loading__ and cls.__validate_lazy__ and cls._validator is None:
            cls._validator = DefaultValidator(
                cls.__schema_uri__, resolver=get_resolver())
            cls._validator._setDefaults = True

        new = super(ProtocolBase, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, **props)

    def pre_init_hook(self, *args, **props):
        """hook after containers allocation before properties initialization to overload"""
        pass

    def post_init_hook(self, *args, **props):
        """hook after properties initialization to overload"""
        pass

    def __init__(self, *args, **props):
        """
        main initialization method, dealing with lazy loading
        """
        self.logger.debug(lazy_format("INIT {0} with {1}", self.short_repr, props, to_format=[1]))

        cls = self.__class__
        props.pop('$schema', None)

        self._lazy_data = {}
        self._extended_properties = collections.OrderedDict()
        self._properties = collections.OrderedDict()
        self._key2attr = {}
        self._lazy_loading = props.pop('_lazy_loading', None) or cls.__lazy_loading__
        self._validate_lazy = props.pop('_validate_lazy', None) or cls.__validate_lazy__
        self._attr_by_name = props.pop('_attr_by_name', None) or cls.__attr_by_name__
        self._propagate = props.pop('_propagate', None) or cls.__propagate__
        self._strict = props.pop('_strict', None) or cls.__strict__

        for prop in self.__prop_names_ordered__.keys():
            self._properties[prop] = None

        parent = props.pop('_parent', None)
        # to avoid calling the setter if None
        if parent:
            self._parent = parent
        self._childConf = {
            '_lazy_loading':  self._lazy_loading,
            '_validate_lazy': self._validate_lazy,
            '_attr_by_name':  self._attr_by_name,
            '_propagate': self._propagate,
            '_strict': self._strict
        } if self._propagate else {}
        mixins.HasCache.__init__(self)

        self.pre_init_hook(*args, **props)

        # non keyword argument = reference to property extern to document to be resolved later
        if len(args) == 1 and utils.is_string(args[0]):
            props['$ref'] = args[0]
        if '$ref' in props:
            props.update(resolve_uri(props.pop('$ref')))

        # remove initial values of readonly members
        for k in self.__read_only__.intersection(props.keys()):
            props.pop(k)
            self.logger.warning('property %s is read-only. Initial value provided not used.', k)

        # To support defaults, we have to actually execute the constructors
        # but only for the ones that have defaults set.
        self.deactivate_read_only()
        sorted_keys = self._sort_property_list(self.__has_default__)
        for raw in sorted_keys:
            v = self.__has_default__[raw]
            trans = self.__prop_names_ordered__.get(raw, raw)
            if not set([raw, trans]).intersection(props.keys()):
                # no lazy loading for read only as it implies to reset RO status later
                if self._lazy_loading and raw not in self.__read_only__:
                    self._lazy_data.setdefault(raw, copy.copy(v))
                else:
                    prop = getattr(cls, trans, None)
                    setattr(self, trans, copy.copy(v))
                    # not setting default for properties with a getter
                    #if prop and not prop.fget:
                    #    setattr(self, trans, copy.copy(v))
        self.activate_read_only()

        if props.get('name'):
            if isinstance(self, mixins.HasCanonicalName):
                mixins.HasCanonicalName.set_name(self, props['name'])
            elif isinstance(self, mixins.HasName):
                mixins.HasName.set_name(self, props['name'])

        if self._lazy_loading:
            self._lazy_data.update({self.propname_raw_trans(k)[0]: v for k, v in props.items()})
            if self._attr_by_name:
                # replace refs / mandatory for loading ngomf nested schemas
                base_uri = self.__schema_uri__
                def replace_ref(coll, key, level):
                    if key != '$ref' or level > 2:
                        return
                    coll.update(resolve_uri(qualify_ref(coll.pop('$ref'), base_uri)))
                utils.apply_through_collection(self._lazy_data, replace_ref, recursive=True)
                for raw, v in self._lazy_data.items():
                    self._set_attr_by_name(raw, v)
            sorted_keys = self._sort_property_list(self._lazy_data)
            for raw in sorted_keys:
                # force setting additional props -> use raw name
                if raw not in self.__prop_names_ordered__:
                    setattr(self, raw, self._lazy_data.pop(raw))
                else:
                    trans = self.__prop_names_ordered__.get(raw, raw)
                    prop = getattr(cls, trans, None)
                    # force setting properties with setter -> use trans directly
                    if prop and prop.fset:
                        setattr(self, trans, self._lazy_data.pop(raw))
        else:
            try:
                sorted_keys = self._sort_property_list(props)
                for k in sorted_keys:
                    prop = props[k]
                    trans = self.__prop_names_ordered__.get(k, k)
                    setattr(self, trans, prop)
                # call getters on all required not defined in props
                for raw in self.__required__:
                    trans = self.__prop_names_ordered__.get(raw)
                    if set([raw, trans]).intersection(props.keys()):
                        getattr(self, trans)
                if self._strict:
                    self.validate()
            except Exception as er:
                self.logger.error("INIT %s: %s", self, er)
                raise

        self.post_init_hook(*args, **props)
        self._lazy_loading = False

    def __hash__(self):
        """hash function to store objects references"""
        return id(self)

    @memoized_property
    def short_repr(self):
        return "<%s id=%s>" % (self.cls_fullname, id(self))

    def __str__(self):
        from . import settings
        rep = "<%s {" % (self.cls_fullname)
        data = self._validated_data or {}
        elts = []
        for i, (k, v) in enumerate(data.items()):
            if utils.is_mapping(v):
                elts.append("%s={%i}" % (k, len(v)))
            elif utils.is_sequence(v):
                elts.append("%s=[%i]" % (k, len(v)))
            else:
                if utils.is_string(v) and len(v) >= settings.PPRINT_MAX_STRL:
                    v = v[:settings.PPRINT_MAX_STRL] + '..."'
                elts.append("%s=%s" % (k, v))
            if i >= settings.PPRINT_MAX_EL:
                elts.append('...')
                break
        return rep + ' '.join(elts) + '}>'

    def __repr__(self):
        from . import settings
        rep = "<%s id=%s validated=%s {" % (self.cls_fullname, id(self), self._validated_data is not None)
        data = self._validated_data or {}
        elts = []
        for i, (k, v) in enumerate(data.items()):
            if utils.is_mapping(v):
                elts.append("%s={%i}" % (k, len(v)))
            elif utils.is_sequence(v):
                elts.append("%s=[%i]" % (k, len(v)))
            else:
                if utils.is_string(v) and len(v) >= settings.PPRINT_MAX_STRL:
                    v = v[:settings.PPRINT_MAX_STRL] + '..."'
                elts.append("%s=%s" % (k, v))
            if i >= settings.PPRINT_MAX_EL:
                elts.append('...')
                break
        return rep + ' '.join(elts) + '}>'

    def __eq__(self, other):
        if not utils.is_mapping(other):
            return False
        if len(self) != len(other):
            return False
        for k in self.keys():
            if self.get(k) != other.get(k):
                return False
        return True

    def serialize(self, **opts):
        self.validate(excludes=opts.get('excludes', []), only=opts.get('only', []), validate_lazy=True)
        enc = ProtocolJSONEncoder(**opts)
        return enc.encode(self)

    _def_enc = ProtocolJSONEncoder()

    def for_json(self, **opts):
        # _for_json is invalidated in HasCache.touch
        self.validate(excludes=opts.get('excludes', []), only=opts.get('only', []), validate_lazy=True)
        if not opts:
            return self._def_enc.default(self)
        return ProtocolJSONEncoder(**opts).default(self)

    @classmethod
    def jsonschema(cls):
        from .resolver import get_resolver
        return get_resolver().resolve(cls.__schema_uri__)[1]

    def activate_read_only(self):
        self._RO_active = True

    def deactivate_read_only(self):
        self._RO_active = False

    def _set_attr_by_name(self, name, val):
        trans = self.propname_raw_trans(name)[1]
        if utils.is_mapping(val) and 'name' in val:
            self._key2attr[val['name']] = (trans, None)
        if utils.is_sequence(val):
            for i, v2 in enumerate(val):
                if utils.is_mapping(v2) and 'name' in v2:
                    self._key2attr[v2['name']] = (trans, i)

    @property
    def dependencies_raw1(self):
        """
        Create object dependency tree according to class declared dependencies and expression inputs.
        Make all property names raw and keep only first level
        """
        deps = dict(self.__dependencies_raw1__)
        if not self._raw_literals:
            for raw, p in self._properties.items():
                if p is not None and getattr(p, '_expr_inputs', False):
                    deps[raw] |= set([i.split('.')[0] for i in p._expr_inputs])
            for raw, p in self._extended_properties.items():
                deps[raw] = set([i.split('.')[0] for i in getattr(p, '_expr_inputs', [])])
        return deps

    def _sort_property_list(self, prop_list):
        ret = []
        if prop_list:
            prop_list = set(prop_list)
            deps = self.dependencies_raw1
            # call and validate props according to topological order
            for level in utils.topological_sort(deps):
                plist_level = level.intersection(prop_list)
                prop_list.difference_update(plist_level)
                ret += list(plist_level)
            ret += list(prop_list)
        return ret

    _opts_cached = {}

    def validate(self, excludes=[], only=[], **opts):
        raw_name = lambda k: self.propname_raw_trans(k)[0]

        opts.setdefault('raw_literals', self._raw_literals)
        opts.setdefault('validate_lazy', self._validate_lazy)
        opts['excludes'] = set([raw_name(k) for k in excludes])
        opts['only'] = set([raw_name(k) for k in only])

        raw_literals = opts['raw_literals']
        validate_lazy = opts['validate_lazy']

        if self.is_dirty() or opts != self._opts_cached:
            from .utils import topological_sort

            all = set(self.keys())
            deps = self.dependencies_raw1
            lazy = set(self._lazy_data.keys())
            # starting by all props already defined (all-lazy) with required props
            to_include = all.difference(lazy).union(self.__required__)

            # if validate_lazy, include lazy data and props with getters
            if validate_lazy:
                to_include.update(lazy)
                to_include.update(self.__with_getter__)

            # remove excludes and keep only
            to_include.difference_update(excludes)
            if only:
                to_include.intersection_update(only)

            # add included properties dependencies
            for p in list(to_include):
                dp = deps.get(p)
                if dp:
                    to_include.update(dp)

            errors = []
            # call and validate props according to topological order
            for level in topological_sort(deps):
                for raw in level.intersection(to_include):
                    # if prop is in lazy data or defined by a getter
                    if raw in lazy.union(self.__with_getter__) and self._properties.get(raw) is None:
                        getattr(self, raw)
                    prop = self._properties.get(raw)
                    # call validation of objects/arrays with same lazy_loading options
                    if isinstance(prop, (ProtocolBase, ArrayWrapper)) and not prop.validate(validate_lazy=validate_lazy):
                        errors.append(raw)
                    elif isinstance(prop, LiteralValue) and not prop.validate(raw_literals=raw_literals):
                        errors.append(raw)

            if errors:
                self.logger.info('errors validating %s', errors)
                self._validated_data = None
                return False

            # now look for missing required properties
            missing = self.missing_property_names()
            if len(missing) > 0:
                raise ValidationError("'{0}' are required attributes for {1}".format(missing, self.__class__.__name__))

            self._validated_data = {
                raw: prop._validated_data
                for raw, prop in self._properties.items()
                if prop is not None
            }

            # add additional properties (not validated)
            self._validated_data.update(self._extended_properties)

            self._opts_cached = opts
            self._inputs_cached = self._inputs_data()

        return True

    @classmethod
    def issubclass(cls, klass):
        """ Subclass specific method. """
        return pjo_util.safe_issubclass(cls, klass)

    _cls_fullname = None
    @classproperty
    def cls_fullname(cls):
        """ Returns class qualified name. """
        if cls._cls_fullname is None:
            cls._cls_fullname = utils.fullname(cls)
            if cls._cls_fullname.startswith('<abc.'):
                cls._cls_fullname = cls.__name__
        return cls._cls_fullname

    @classmethod
    def set_configfiles_defaults(cls, overwrite=False):
        """
        Look for default values in objects_config_loader to initialize properties
        in the object.

        :param overwrite: overwrite values already set
        """
        from . import settings
        defconf = settings.as_dict().get(utils.fullname(cls), {})
        for k, v in defconf.items():
            if overwrite:
                try:
                    cls.logger.debug("CONFIG SET %s.%s = %s", utils.fullname(cls), k, v)
                    cls.__propinfo__[k]['default'] = v
                except Exception as er:
                    cls.logger.error("CONFIG SET %s.%s = %s", utils.fullname(cls), k, v, exc_info=True)

    @classmethod
    def pbase_mro(cls, ngo_base=False):
        """ Returns MRO of only ProtocolBase classes (may only be ngoschema.ProtocolBase). """
        return cls.__ngo_pbase_mro__ if ngo_base else cls.__pbase_mro__

    @classmethod
    def propinfo(cls, propname):
        """ Returns class attribute schema. """
        # safe proof to name translation and inheritance
        raw = cls.propname_raw_trans(propname)[0]
        return cls.__propinfo_flatten__.get(raw, {})

    @classmethod
    def propname_raw_trans(cls, propname, no_exc=False):
        from .classbuilder import clean_prop_name
        for raw, trans in cls.__prop_names_ordered__.items():
            if propname in [trans, raw]:
                return raw, trans
        if no_exc or cls.__extensible__._additional_type:
            return propname, clean_prop_name(propname)
        raise AttributeError("'{0}' is not a valid property of {1}".format(propname, cls.__name__))

    def __iter__(self):
        return itertools.chain(
            self._extended_properties.keys(),
            list(self._lazy_data) +\
            list(raw for raw, v in self._properties.items() if v is not None)
        )

    def __len__(self):
        return len(self._extended_properties) \
               + len([v for v in self._properties.values() if v is not None]) \
               + len(self._lazy_data)

    def __contains__(self, key):
        # add test for existence in lazy_data and that prop is not None
        try:
            raw = self.propname_raw_trans(key)[0]
            if self._properties.get(raw) is not None:
                return True
            return raw in self._lazy_data or raw in self._extended_properties
        except Exception as er:
            return False

    def __getattr__(self, name):
        """
        Allow getting class attributes, protected attributes and protocolBase attributes
        as optimally as possible. attributes can be looked up base on their name, or by
        their canonical name, using a correspondence map done with _set_key2attr
        """
        # private and protected attributes at accessed directly
        if name.startswith("_"):
            return collections.MutableMapping.__getattribute__(self, name)

        # object attributes
        if name in self.__object_attr_list_flatten__:
            return object.__getattribute__(self, name)

        raw, trans = self.propname_raw_trans(name, no_exc=True)

        if self._attr_by_name:
            prop, index = self._key2attr.get(trans, (None, None))
            if prop:
                attr = ProtocolBase.__getattr__(self, prop)
                if index is None:
                    return attr
                else:
                    return attr[index]

        # check it s not a schema defined property, we should not reach there
        if raw in self.__prop_names_ordered__:
            prop = getattr(self.__class__, trans)
            try:
                return prop.__get__(self)
            except (TypeError, ValidationError) as er:
                raise six.reraise(ValidationError,
                                  ValidationError("Problem setting property '{0}': {1} ".format(name, er)),
                                  sys.exc_info()[2])
            except Exception as er:
                self.logger.info(er, exc_info=True)
                raise
        # check it s an extended property
        if raw in self._extended_properties:
            return self._extended_properties[raw]

        raise AttributeError("'{0}' is not a valid property of {1}".format(
                             name, self.__class__.__name__))

    def __getitem__(self, key):
        """access property as in a dict and returns json if not composed of objects """
        try:
            return getattr(self, key)
        except AttributeError as er:
            raise KeyError(key, str(er))
        except Exception as er:
            raise

    def get(self, key, default=None):
        """overrides get method to properly handle default behaviour"""
        #  collections.Mapping.get is bugged in our case if prop are None, default is not returned
        #return collections.Mapping.get(self, key, default)
        try:
            v = self[key]
            if v is None:
                v = default
            return v
        except KeyError as er:
            return default

    def __setattr__(self, name, value):
        """allow setting of protected attributes"""
        # protected members
        if name.startswith("_"):
            return collections.MutableMapping.__setattr__(self, name, value)

        # object attributes
        if name in self.__object_attr_list_flatten__:
            return object.__setattr__(self, name, val)

        raw, trans = self.propname_raw_trans(name)

        if self._attr_by_name:
            prop, index = self._key2attr.get(trans, (None, None))
            if prop:
                if index is None:
                    name = prop
                else:
                    attr = getattr(self, prop)
                    attr[index] = val
                    return

        if trans in self.__prop_allowed__:
            # If its in __propinfo__, then it actually has a property defined.
            # The property does special validation, so we actually need to
            # run its setter. We get it from the class definition and call
            # it directly. XXX Heinous.
            prop = getattr(self.__class__, trans)
            try:
                prop.__set__(self, val)
            except (TypeError, ValidationError) as er:
                raise six.reraise(ValidationError,
                                  ValidationError("Problem setting property '{0}': {1} ".format(name, er)),
                                  sys.exc_info()[2])
            except Exception as er:
                self.logger.info(er, exc_info=True)
                raise
        else:
            # This is an additional property of some kind
            try:
                casted = val.for_json() if hasattr(val, 'for_json') else val
                prop = self.__extensible__.instantiate(raw, casted)
            except (TypeError, ValidationError) as er:
                raise six.reraise(ValidationError,
                                  ValidationError("Attempt to set unknown property '{0}': {1} ".format(name, er)),
                                  sys.exc_info()[2])
            self._extended_properties[raw] = prop

    def _get_prop(self, name):
        """
        Accessor to property dealing with lazy_data, standard properties and potential extended properties
        """
        raw, trans = self.propname_raw_trans(name)
        if raw in self._lazy_data:
            setattr(self, trans, self._lazy_data.pop(raw))
        if raw in self._properties:
            return self._properties.get(raw)
        return self._extended_properties.get(raw)

    def _get_prop_value(self, name, default=None):
        """
        Accessor to property value (as for json)
        """
        prop = self._get_prop(name)
        if isinstance(prop, (ProtocolBase, LiteralValue, ArrayWrapper)):
            return prop.for_json()
        if prop is not None:
            return prop
        return default

    def _set_prop_value(self, name, value):
        """
        Set a property shortcutting the setter. To be used in setters
        """
        raw, trans = self.propname_raw_trans(name)
        if raw in self._lazy_data:
            self._lazy_data[raw] = value
        elif raw in self._properties:
            prop = self._properties[raw]
            if isinstance(prop, (LiteralValue, ArrayWrapper)):
                prop.touch()
                prop.__init__(value)
            else:
                desc = getattr(self.__class__, trans)
                typ = desc.prop_type
                self._properties[raw] = typ(value)
        else:
            self._extended_properties[raw] = self.__extensible__.instantiate(raw, value)

    def missing_property_names(self):
        # overrides original method to deal with inheritance
        missing = []
        for raw in self.__required__:
            # Allow the null type
            trans = self.__prop_names_ordered__[raw]
            propinfo = self.__propinfo_flatten__.get(raw, {})

            null_type = False
            if "type" in propinfo:
                type_info = propinfo["type"]
                null_type = (type_info == "null") or (utils.is_sequence(type_info) and 'null' in type_info)
            elif "oneOf" in propinfo:
                for o in propinfo["oneOf"]:
                    type_info = o.get("type")
                    if (type_info == "null") or (utils.is_sequence(type_info) and 'null' in type_info):
                        null_type = True
                        break

            if (raw not in self._properties and null_type) or (self._properties.get(raw) is None and not null_type):
                missing.append(raw)

        return missing

    def search_non_rec(self, path, *attrs, **attrs_value):
        from .query import search_object
        res = next(search_object(self, path, *attrs, **attrs_value))
        if res:
            p, e = res
            yield p, e
            # only next siblings and remaining next cousins, etc...
            p_cur, cur = p, e
            while cur and '/' in p_cur:
                if cur is self:
                    yield
                p_par = p_cur.rsplit('/', 1)[0]
                par = get_descendant(self, p_par.split('/'))
                if utils.is_sequence(par):
                    next_siblings = list(range(par.index(cur)+1, len(par)))
                else:
                    next_siblings = {k for i, k in enumerate(par.keys()) if i > list(par.keys()).index(cur)}
                for s in next_siblings:
                    for ps, pe in par[s].search_non_rec(path, *attrs, **attrs_value):
                        yield ps, pe
                p_cur, cur = p_par, cur._parent

    def search(self, path, *attrs, **attrs_value):
        from .query import search_object
        return search_object(self, path, *attrs, **attrs_value)

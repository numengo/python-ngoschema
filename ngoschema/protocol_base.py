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

from python_jsonschema_objects import \
    classbuilder as pjo_classbuilder, \
    util as pjo_util, \
    literals as pjo_literals

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


def get_descendant(obj, key_list, load_lazy=False):
    """
    Get descendant in an object/dictionary by providing the path as a list of keys
    :param obj: object to iterate
    :param key_list: list of keys
    :param load_lazy: in case of lazy loaded object, force loading
    """
    k0 = key_list[0]

    try:
        child = getattr(obj, k0)
    except Exception as er:
        try:
            child = obj[k0]
        except Exception as er:
            child = None
    return get_descendant(child, key_list[1:], load_lazy) \
            if child and len(key_list)>1 else child


def make_property(prop, info, fget=None, fset=None, fdel=None, desc=""):
    from . import descriptors

    prop = descriptors.AttributeDescriptor(prop, info, fget=fget, fset=fset, fdel=fdel, desc=desc)
    return prop


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
        #props.pop('$schema', None)

        self._lazy_data = {}
        self._extended_properties = {}
        self._properties = {}
        self._key2attr = {}
        self._lazyLoading = props.pop('_lazyLoading', None) or cls.__lazy_loading__
        self._validateLazy = props.pop('_validateLazy', None) or cls.__validate_lazy__
        self._attrByName = props.pop('_attrByName', None) or cls.__attr_by_name__
        self._propagate = props.pop('_propagate', None) or cls.__propagate__
        self._strict = props.pop('_strict', None) or cls.__strict__
        parent = props.pop('_parent', None)
        # to avoid calling the setter if None
        if parent:
            self._parent = parent
        self._childConf = {
            '_lazyLoading':  self._lazyLoading,
            '_validateLazy': self._validateLazy,
            '_attrByName':  self._attrByName,
            '_propagate': self._propagate,
            '_strict': self._strict
        } if self._propagate else {}
        mixins.HasCache.__init__(self,
                                 context=parent,
                                 inputs=self._inputs())

        for prop in self.__prop_names_flatten__.values():
            self._properties.setdefault(prop, None)

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
        for k, v in self.__has_default__.items():
            k2 = self.__prop_translated_flatten__.get(k, k)
            if k2 not in props:
                if self._lazyLoading:
                    self._lazy_data.setdefault(k2, copy.copy(v))
                else:
                    setattr(self, k2, copy.copy(v))

        if props.get('name'):
            if isinstance(self, mixins.HasCanonicalName):
                mixins.HasCanonicalName.set_name(self, props['name'])
            elif isinstance(self, mixins.HasName):
                mixins.HasName.set_name(self, props['name'])

        if self._lazyLoading:
            self._lazy_data.update({self.__prop_names_flatten__.get(k, k): v for k, v in props.items()})
            if self._attrByName:
                # replace refs / mandatory for loading ngomf nested schemas
                base_uri = self.__schema_uri__
                def replace_ref(coll, key, level):
                    if key != '$ref' or level > 2:
                        return
                    coll.update(resolve_uri(qualify_ref(coll.pop('$ref'), base_uri)))
                utils.apply_through_collection(self._lazy_data, replace_ref, recursive=True)
                for k, v in self._lazy_data.items():
                    if utils.is_mapping(v) and 'name' in v:
                        self._key2attr[v['name']] = (k, None)
                    if utils.is_sequence(v):
                        for i, v2 in enumerate(v):
                            if utils.is_mapping(v2) and 'name' in v2:
                                self._key2attr[v2['name']] = (k, i)
        else:
            try:
                for k, prop in props.items():
                    k2 = self.__prop_translated_flatten__.get(k, k)
                    setattr(self, k2, prop)
                # call getters on all required not defined in props
                for k in self.__required__:
                    if k not in props:
                        getattr(self, k)
                if self._strict:
                    self.do_validate()
                self.set_clean()
            except Exception as er:
                self.logger.error("INIT %s: %s", self, er)
                raise

        self.post_init_hook(*args, **props)

    def __hash__(self):
        """hash function to store objects references"""
        return id(self)

    @memoized_property
    def short_repr(self):
        return "<%s id=%s>" % (self.cls_fullname, id(self))

    def __str__(self):
        from . import settings
        rep = "<%s {" % (self.cls_fullname)
        elts = []
        for k in self.keys():
            prop = self._get_prop(k)
            if prop is None:
                continue
            if hasattr(prop, 'isLiteralClass'):
                s = str(prop._value)
                if utils.is_string(prop._value):
                    s = '"%s"' % s
                    if len(s) >= settings.PPRINT_MAX_STRL:
                        s = s[:settings.PPRINT_MAX_STRL] + '..."'
                elts.append("%s=%s" % (k, s))
            elif len(prop):
                if utils.is_mapping(prop):
                    elts.append("%s={%i}" % (k, len(prop)))
                if utils.is_sequence(prop):
                    elts.append("%s=[%i]" % (k, len(prop)))
            if len(elts) == settings.PPRINT_MAX_EL:
                elts.append('...')
                break
        return rep + ' '.join(elts) + '}>'

    def __repr__(self):
        from . import settings
        rep = "<%s id=%s validated=%s {" % (self.cls_fullname, id(self), not getattr(self, '_dirty', True))
        elts = []
        for k in self.keys():
            prop = self._get_prop(k)
            if prop is None:
                continue
            if hasattr(prop, 'isLiteralClass'):
                s = str(prop._value)
                if utils.is_string(prop._value):
                    s = '"%s"' % s
                    if len(s) >= settings.PPRINT_MAX_STRL:
                        s = s[:settings.PPRINT_MAX_STRL] + '..."'
                elts.append("%s=%s" % (k, s))
            elif len(prop):
                elts.append("%s=%s" % (k, prop))
            if len(elts) == settings.PPRINT_MAX_EL:
                elts.append('...')
                break
        return rep + ' '.join(elts) + '}>'

    def __format__(self, format_spec):
        props = {self.__prop_translated_flatten__.get(k, k): v.__format__(format_spec)
                        for k, v in itertools.chain(six.iteritems(self._properties),
                                    six.iteritems(self._extended_properties))
                        if v is not None and not (utils.is_collection(v) and not len(v))}
        return props.__format__(format_spec)

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
        self.validate()
        enc = ProtocolJSONEncoder(**opts)
        return enc.encode(self)

    _def_enc = ProtocolJSONEncoder()

    def for_json(self, **opts):
        # _for_json is invalidated in HasCache.touch
        if not opts:
            return self._def_enc.default(self)
        return ProtocolJSONEncoder(**opts).default(self)

    @classmethod
    def jsonschema(cls):
        from .resolver import get_resolver
        return get_resolver().resolve(cls.__schema_uri__)[1]

    def validate(self):
        if self._lazyLoading:
            if self._lazy_data and self._validateLazy:
                pass
        else:
            missing = self.missing_property_names()
            if len(missing) > 0:
                raise ValidationError("'{0}' are required attributes for {1}".format(missing, self.__class__.__name__))

            for prop, val in self._properties.items():
                if val is None:
                    continue

                if isinstance(val, (ProtocolBase, ArrayWrapper, LiteralValue)):
                    val.validate()
                elif getattr(val, "isLiteralClass", None) is True:
                    val.validate()
                else:
                    # This object is of the wrong type, but just try setting it
                    # The property setter will enforce its correctness
                    # and handily coerce its type at the same time
                    setattr(self, prop, val)

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
        prop_id = cls.__prop_translated_flatten__.get(propname, propname)
        return cls.__propinfo_flatten__.get(prop_id, {})

    def __getattr__(self, name):
        """
        Allow getting class attributes, protected attributes and protocolBase attributes
        as optimally as possible. attributes can be looked up base on their name, or by
        their canonical name, using a correspondence map done with _set_key2attr
        """
        # private and protected attributes at accessed directly
        if name.startswith("_"):
            return collections.MutableMapping.__getattribute__(self, name)

        if name in self._lazy_data:
            return self._get_prop(name)

        # check inner properties to get proper getter
        if name in self.__object_attr_list_flatten__:
            return object.__getattribute__(self, name)

        prop, index = self._key2attr.get(name, (None, None))
        if prop:
            attr = ProtocolBase.__getattr__(self, prop)
            if index is None:
                return attr
            else:
                return attr[index]

        # check it s not a schema defined property, we should not reach there
        if name in self.__prop_names_flatten__.values():
            if name in self._properties:
                return self._properties.get(name)
            raise KeyError(name)
        # check it s not a translated property
        if name in self.__prop_names_flatten__:
            return getattr(self, self.__prop_names_flatten__[name])
        # check it s an extended property
        if name in self._extended_properties:
            return self._extended_properties[name]

        raise AttributeError("'{0}' is not a valid property of {1}".format(
                             name, self.__class__.__name__))

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

    def __contains__(self, key):
        # add test for existence in lazy_data and that prop is not None
        key = self.__prop_names_flatten__.get(key, key)
        return key in self._lazy_data or self._properties.get(key) is not None or key in self._extended_properties

    def __getitem__(self, key):
        """access property as in a dict and returns json if not composed of objects """
        try:
            key = self.__prop_names_flatten__.get(key, key)
            ret = getattr(self, key)
            if isinstance(ret, pjo_literals.LiteralValue):
                return ret._value
            return ret
        except AttributeError as er:
            raise KeyError(key, str(er))
        except Exception as er:
            raise

    def __setattr__(self, name, val):
        """allow setting of protected attributes"""
        # protected members
        if name.startswith("_"):
            return collections.MutableMapping.__setattr__(self, name, val)
        # check inner properties to get proper setter
        if name in self.__object_attr_list_flatten__:
            return object.__setattr__(self, name, val)

        name = self.__prop_names_flatten__.get(name, name)
        if self._attrByName:
            prop, index = self._key2attr.get(name, (None, None))
            if prop:
                if index is None:
                    name = prop
                else:
                    attr = getattr(self, prop)
                    attr[index] = val
                    return

        if name in self.__prop_names_flatten__.values():
            # If its in __propinfo__, then it actually has a property defined.
            # The property does special validation, so we actually need to
            # run its setter. We get it from the class definition and call
            # it directly. XXX Heinous.
            prop = getattr(self.__class__, name)
            try:
                prop.__set__(self, val)
            except (TypeError, ValidationError) as er:
                raise six.reraise(ValidationError,
                                  ValidationError("Problem setting property '{0}': {1} ".format(name, er)),
                                  sys.exc_info()[2])
        else:
            # This is an additional property of some kind
            try:
                casted = val.for_json() if hasattr(val, 'for_json') else val
                val = self.__extensible__.instantiate(name, casted)
            except (TypeError, ValidationError) as er:
                raise six.reraise(ValidationError,
                                  ValidationError("Attempt to set unknown property '{0}': {1} ".format(name, er)),
                                  sys.exc_info()[2])
            self._extended_properties[name] = val

    def _get_prop(self, name):
        """
        Accessor to property dealing with lazy_data, standard properties and potential extended properties
        """
        if self._lazyLoading and name in self._lazy_data:
            setattr(self, name, self._lazy_data.pop(name))
        name = self.__prop_names_flatten__.get(name, name)
        if name in self._properties:
            return self._properties.get(name)
        return self._extended_properties.get(name)

    def _get_prop_value(self, name, default=None):
        """
        Accessor to property value (as for json)
        """
        if self._lazyLoading and name in self._lazy_data:
            val = self._lazy_data[name]
            return val.for_json() if hasattr(val, 'for_json') else val
        prop = self._get_prop(name)
        return prop.for_json() if prop else default

    def _set_prop_value(self, name, value):
        """
        Set a property shortcutting the setter. To be used in setters
        """
        if self._lazyLoading:
            self._lazy_data[name] = value
        else:
            prop = self._get_prop(name)
            if prop:
                prop.__init__(value)
                prop.do_validate()
            elif name in self.__prop_names_flatten__:
                pinfo = self.propinfo(name)
                typ = pinfo.get('_type') if pinfo else None
                if typ and issubclass(typ, pjo_literals.LiteralValue):
                    prop = typ(value)
                    prop.do_validate()
                    self._properties[name] = prop
                else:
                    raise AttributeError("no type specified for property '%s'"% name)

    def missing_property_names(self):
        # overrides original method to deal with inheritance
        propname = lambda x: self.__prop_names_flatten__[x]
        missing = []
        for x in self.__required__:

            # Allow the null type
            propinfo = self.propinfo(propname(x))
            null_type = False
            if "type" in propinfo:
                type_info = propinfo["type"]
                null_type = (
                    type_info == "null"
                    or isinstance(type_info, (list, tuple))
                    and "null" in type_info
                )
            elif "oneOf" in propinfo:
                for o in propinfo["oneOf"]:
                    type_info = o.get("type")
                    if (
                        type_info
                        and type_info == "null"
                        or isinstance(type_info, (list, tuple))
                        and "null" in type_info
                    ):
                        null_type = True
                        break

            if (propname(x) not in self._properties and null_type) or (
                self._properties[propname(x)] is None and not null_type
            ):
                missing.append(x)

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

    @classmethod
    def _prop_inputs(cls, name):
        return set(cls.__dependencies__.get(name, []))

    @classmethod
    def _prop_outputs(cls, name):
        return set([k for k, v in cls.__dependencies__.items() if name in v])

    @classmethod
    def _outputs(cls):
        return set(cls.__read_only__)

    @classmethod
    def _inputs(cls):
        # inputs are the properties not readonly and not referred in dependency tree
        return set(cls.__prop_names_flatten__).difference(cls.__read_only__)

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
    wrapper_types as pjo_wrapper_types, \
    literals as pjo_literals, \
    validators as pjo_validators

from . import utils
from . import mixins
from .mixins import HasLogger
from .resolver import resolve_uri
from .validators.jsonschema import DefaultValidator
from .utils.json import ProtocolJSONEncoder
from .decorators import classproperty, memoized_property
from .utils import lazy_format


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
    
    * metamodel has a richer vocabulary, and class definition supports inheritance, and 
    database persistence
    
    * hybrid classes: classes have a json schema defining all its members, but have some 
    business implementation done in python and where default setters/getters can be 
    overriden. 
    
    * string literal value with patterns: a string literal value can be defined as a 
    formatted string which can depend on other properties.
    
    * complex literal types: path/date/datetime are automatically created and can be 
    handled as expected python objects, and will then be properly serialized
    
    * allow lazy loading on member access

    * methods are automatically decorated to add logging possibility, exception handling
    and argument validation/conversion to the proper type (type can be given as a schema
    through a decorator or simply by documenting the docstring with a schema)
        
    * all instances created are registered and can then be queried using Query
    
    * default values can be configured in the config files
    """

    # additional private and protected props
    _validator = None
    __prop_names__ = dict()
    __prop_translated__ = dict()

    def __new__(cls,
                *args,
                **props):
        """
        function creating the class with a special treatment to resolve subclassing
        """
        from .resolver import get_resolver
        from .classbuilder import get_builder

        base_uri = cls.__schema__

        if '$ref' in props:
            props.update(resolve_uri(utils.resolve_ref_uri(base_uri, props.pop('$ref'))))

        if '$schema' in props:
            if props['$schema'] != cls.__schema__:
                cls = get_builder().resolve_or_construct(props['$schema'])

        cls.init_class_logger()

        # option to validate arguments at init even if lazy loading
        if cls.__lazy_loading__ and cls.__validate_lazy__ and cls._validator is None:
            cls._validator = DefaultValidator(
                cls.__schema__, resolver=get_resolver())
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

        self._lazy_data = dict()
        self._extended_properties = dict()
        self._properties = dict()
        self._key2attr = dict()
        self._lazyLoading = props.pop('_lazyLoading', None) or cls.__lazy_loading__
        self._validateLazy = props.pop('_validateLazy', None) or cls.__validate_lazy__
        self._attrByName = props.pop('_attrByName', None) or cls.__attr_by_name__
        self._propagate = props.pop('_propagate', None) or cls.__propagate__
        parent = props.pop('_parent', None)
        # to avoid calling the setter if None
        if parent:
            self._parent = parent
        self._childConf = {
            '_lazyLoading':  self._lazyLoading,
            '_validateLazy': self._validateLazy,
            '_attrByName':  self._attrByName,
            '_propagate': self._propagate
        } if self._propagate else {}

        mixins.HasCache.__init__(self,
                                 context=parent,
                                 inputs=self.__dependencies__)

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
            if k not in props:
                if self._lazyLoading:
                    self._lazy_data.setdefault(k, copy.copy(v))
                else:
                    setattr(self, k, copy.copy(v))

        if 'name' in props:
            if isinstance(self, mixins.HasCanonicalName):
                mixins.HasCanonicalName.set_name(self, props['name'])
            elif isinstance(self, mixins.HasName):
                mixins.HasName.set_name(self, props['name'])

        if self._lazyLoading:
            self._lazy_data.update({self.__prop_names_flatten__.get(k, k): v for k, v in props.items()})
            if self._attrByName:
                base_uri = self.__schema__
                def replace_ref(coll, key, level):
                    if key != '$ref' or level > 2:
                        return
                    coll.update(resolve_uri(utils.resolve_ref_uri(base_uri, coll.pop('$ref'))))
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
                    setattr(self, k, prop)
                if self.__strict__:
                    self.do_validate(force=True)
            except Exception as er:
                self.logger.error('problem initializing %s.', self, exc_info=True)
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
        rep = "<%s id=%s validated=%s {" % (self.cls_fullname, id(self), not self._dirty)
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
    def for_json(self):
        """removes None or empty or defaults of non required members """
        return {k: v for k, v in self._def_enc.default(self).items()
                if (v or utils.is_literal(v)) and v != self.__has_default__.get(k) and k not in self.__required__}

    @classmethod
    def jsonschema(cls):
        from .resolver import get_resolver
        return get_resolver().resolve(cls.__schema__)[1]

    def validate(self):
        if self._lazyLoading:
            if self._lazy_data and self._validateLazy:
                pass
        else:
            pjo_classbuilder.ProtocolBase.validate(self)

    @classmethod
    def issubclass(cls, klass):
        """subclass specific method"""
        return pjo_util.safe_issubclass(cls, klass)

    _cls_fullname = None
    @classproperty
    def cls_fullname(cls):
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
        return cls.__ngo_pbase_mro__ if ngo_base else cls.__pbase_mro__

    @classmethod
    def propinfo(cls, propname):
        # safe proof to name translation and inheritance
        propid = cls.__prop_translated_flatten__.get(propname, propname)
        for c in cls.__pbase_mro__:
            if propid in c.__prop_names__:
                return c.__propinfo__[propid]
            elif c is not cls and propid in getattr(c, '__prop_names_flatten__', {}):
                return c.propinfo(propid)
        return {}

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
        for c in self.pbase_mro():
            if name in c.__object_attr_list__:
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
        for c in self.pbase_mro():
            if name in c.__object_attr_list__:
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
            except Exception as er:
                raise six.reraise(
                    pjo_validators.ValidationError,
                    pjo_validators.ValidationError(
                        "Error setting property '{0}' in {1}: {2} ".format(name,
                                                                           self.__class__.__name__,
                                                                           er)),
                    sys.exc_info()[2])
            return


        # This is an additional property of some kind
        try:
            val = self.__extensible__.instantiate(name, val)
        except Exception as e:
            raise six.reraise(
                pjo_validators.ValidationError,
                pjo_validators.ValidationError(
                    "Attempted to set unknown property '{0}' in {1}: {2} ".format(name, self.__class__.__name__, e)),
                sys.exc_info()[2])
        self._extended_properties[name] = val

    def _get_prop(self, name):
        """
        Accessor to property dealing with lazy_data, standard properties and potential extended properties
        """
        if self._lazyLoading and name in self._lazy_data:
            setattr(self, name, self._lazy_data.pop(name))
        if name in self.__prop_names_flatten__.values():
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

    def search(self, path, *attrs, **attrs_value):
        from .query import search_object
        return search_object(dict(self), path, *attrs, **attrs_value)

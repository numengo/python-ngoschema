# *- coding: utf-8 -*-
"""
Derived classbuilder from python-jsonschema-object for ngoschema specific
requirements

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 22/05/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import copy
import datetime
import inspect
import itertools
import logging
import pathlib
import re
import weakref
import dpath.util
from builtins import object

import arrow
import python_jsonschema_objects.classbuilder as pjo_classbuilder
import python_jsonschema_objects.literals as pjo_literals
import python_jsonschema_objects.pattern_properties as pjo_pattern_properties
import python_jsonschema_objects.util as pjo_util
import python_jsonschema_objects.validators as pjo_validators
import python_jsonschema_objects.wrapper_types as pjo_wrapper_types
import six
from future.utils import text_to_native_str as native_str

from . import jinja2
from . import pjo_validators as ngo_pjo_validators
from . import utils
from .canonical_name import CN_KEY
from .canonical_name import resolve_cname
from .config import ConfigLoader
from .decorators import classproperty
from .resolver import DEFAULT_MS_URI
from .resolver import get_resolver
from .uri_identifier import norm_uri
from .uri_identifier import resolve_uri
from .validators import DefaultValidator
from .foreign_key import ForeignKey

logger = pjo_classbuilder.logger

_NEW_TYPES = ngo_pjo_validators.NGO_TYPE_MAPPING

# loader to register module with a transforms folder where to look for model transformations
models_module_loader = utils.GenericModuleFileLoader('models')

# loader of objects default configuration
objects_config_loader = ConfigLoader()

# default builder global variable
_default_builder = None


def get_builder(resolver=None):
    """retrieves the default class builder

    :param resolver: non default resolver to use in builder (default None uses get_resolver)
    :return default ClassBuilder instance
    """
    global _default_builder
    if _default_builder is None:
        _default_builder = ClassBuilder(resolver or get_resolver())
    else:
        if resolver:
            _default_builder.resolver = resolver
    return _default_builder


def get_descendant(obj, key_list, load_lazy=False):
    """
    Get descendant in an object/dictionary by providing the path as a list of keys
    :param obj: object to iterate
    :param key_list: list of keys
    :param load_lazy: in case of lazy loaded object, force loading
    """
    logger = logging.getLogger(__name__)
    if load_lazy and getattr(obj, '_lazy_loading', {}):
        obj._load_lazy()
    elif getattr(obj, '_lazy_loading', {}):
        try:
            return resolve_cname(key_list, obj._lazy_loading)
        except Exception as er:
            #logger.warning(er)
            return None
    k0 = key_list[0]
    try:
        child = obj[k0]
    except Exception as er:
        child = None
    #if hasattr(obj, k0):
    #    child = getattr(obj, k0)
    #else:
    #    child = obj[k0] if k0 in obj else None
    return get_descendant(child, key_list[1:], load_lazy) \
            if child and len(key_list)>1 else child


_reserved_fields_defaults = {
    '_lazy_loading': False,
    '_validate_lazy': True,
    '_attr_by_name': False,
}

# Registry of alive instances using a weakref dictionary
# For each class we have a distinct dictionary
_class_instance_ref = {}

def register_instance(instance):
    """
    Register an instance in the class registy
    Register it for each subclass inheriting ProtocolBase
    """
    for cls in instance.__class__.__mro__:
        if issubclass(cls, ProtocolBase):
            _class_instance_ref.setdefault(id(cls), weakref.WeakValueDictionary()). \
                update({id(instance): instance})

def iter_instances(cls):
    """iterator on alive instances of a given class"""
    return ( ref() for ref in _class_instance_ref.setdefault(id(cls), 
        weakref.WeakValueDictionary()).valuerefs() )


class ProtocolBase(pjo_classbuilder.ProtocolBase):
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
    __class_attr_list__ = set()
    _short_repr_ = True
    #_name = None
    _key2attr = {}
    _lazy_loading = {}
    _ref = None
    _validator = None
    __dependencies__ = {}
    __properties_depends_on__ = {}
    __properties_depends_of__ = {}

    def _set_dependencies(self, **dependencies):
        for prop, depends_of in dependencies.items():
            depends_of = utils.to_list(depends_of)
            self.__properties_depends_on__[prop] = depends_of
            for prop2 in depends_of:
                self.__properties_depends_of__.setdefault(prop2, [])
                self.__properties_depends_of__[prop2].append(prop)

    def __new__(cls, *args, **props):
        """
        function creating the class with a special treatment to resolve subclassing
        """
        if props.get('_lazy_loading', False) and props.get(
                '_validate_lazy', True) and cls._validator is None:
            cls._validator = DefaultValidator(
                cls.__schema__, resolver=get_resolver())
            cls._validator._setDefaults = True
        # specific treatment in case schemaUri redefines the class to create
        if len(args) == 1 and utils.is_string(args[0]):
            ref = args[0]
            if '/' in ref:
                props = resolve_uri(ref)
            else:
                props = resolve_cname(ref)
            props['$ref'] = ref
        schemaUri = props.get('schemaUri', None)
        if schemaUri is not None and schemaUri != cls.__schema__.get('$id'):
            builder = get_builder()
            uri = pjo_util.resolve_ref_uri(builder.resolver.resolution_scope,
                                           schemaUri)
            if uri in builder.resolved:
                cls2 = builder.resolved[uri]
            else:
                with builder.resolver.resolving(schemaUri) as resolved:
                    cls2 = builder.construct(schemaUri, resolved,
                                             (ProtocolBase, ))
            return cls2(*args, **props)
        new = super(ProtocolBase, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, **props)
        # return new(cls, *args, **props) super ProtocolBase does not support args

    def __init__(self, *args, **props):
        """
        main initialization method, dealing with lazy loading
        """
        #if self._iname is not None:
        #    # already initialized calling __new__ with schemaUri
        #    # no workaround found tricking __new__ to subclass on the fly
        #    return

        register_instance(self)

        self._set_dependencies(**self.__dependencies__)

        # remove options from props dictionary and set them as attributes
        for f, d in _reserved_fields_defaults.items():
            setattr(self, f, props.pop(f, d))
        self._attr_by_name = self._attr_by_name or self.__attr_by_name__
        # propagate non default options to children
        for k, v in props.items():
            if isinstance(v, dict):
                for f, d in _reserved_fields_defaults.items():
                    if getattr(self, f) != d:
                        v[f] = getattr(self, f)
            elif isinstance(v, list):
                for i, v2 in enumerate(v):
                    if utils.is_mapping(v2):
                        for f, d in _reserved_fields_defaults.items():
                            if getattr(self, f) != d:
                                v2[f] = getattr(self, f)

        # reference to property extern to document to be resolved later
        if len(args)==1 and utils.is_string(args[0]):
            props['$ref'] = args[0]
        if '$ref' in props:
            self._ref = props.pop('$ref')
            self._load_ref()

        # we set name now, but it will be overwritten when data is loaded
        # important for canonical names
        from .metadata import Metadata
        if isinstance(self, Metadata): 
            if CN_KEY in props:
                self.set_name(props[CN_KEY])

        # remove initial values of readonly members
        for k in self.__read_only__.intersection(props.keys()):
            props.pop(k)
            self.logger.warning('property %s is read-only. Initial value provided not used.', k)

        if self._lazy_loading:
            # validate data to make sure no problem will appear at creation
            if self._validate_lazy:
                dont_check = list(_reserved_fields_defaults.keys()) + ['$ref']
                #self._validator.validate(utils.process_collection(props, replace_refs=True, but=dont_check, fields_recursive=True))
            # lazy loading treatment: add a flag to 1st level objects data only
            # in level 1, lazy_loading is removed calling __init__
            self._lazy_loading = props
            # we add it to _lazy_loading dictionary to make it queriable
            if isinstance(self, Metadata):
                self._lazy_loading.setdefault('canonicalName', self.cname)

        if not self._lazy_loading and not self._ref:
            pjo_classbuilder.ProtocolBase.__init__(self, **props)
            # we set key2attr after to avoid collusion at initialization between
            self._set_key2attr(props)
        else:
            # necessary for proper behaviour of object, normally done in init
            self._extended_properties = dict()
            self._properties = dict(
                zip(self.__prop_names__.values(),
                    [None
                     for x in six.moves.xrange(len(self.__prop_names__))]))

    def for_json(self, no_defaults=True):
        """
        serialization method, removing all members flagged as NotSerialized
        """
        out = {}
        for prop in self:
            # remove items flagged as not_serilalized
            if prop in self.__not_serialized__:
                continue
            propval = getattr(self, prop)
            if hasattr(propval, 'for_json'):
                out[prop] = propval.for_json()
            elif isinstance(propval, list):
                out[prop] = [getattr(x, 'for_json', lambda:x)() for x in propval]
            elif isinstance(propval, (ProtocolBase, pjo_literals.LiteralValue)):
                out[prop] = propval.as_dict()
            elif propval is not None:
                out[prop] = propval
            # evaluate default value and drop it from json
            if no_defaults and prop in self.__has_default__:
                default_value = self.__propinfo__[prop]['default']
                if out[prop] == default_value:
                    out.pop(prop)
        return out

    def _load_ref(self):
        try:
            from .metadata import Metadata
            if '/' in self._ref:
                data = resolve_uri(self._ref)
            elif isinstance(self, Metadata):
                data = self.resolve_cname(self._ref)
            self._validator.validate(data)
            self._set_key2attr(data)
            self._lazy_loading = data
            self._ref = None
            return True
        except Exception as er:
            logger.warning(er, exc_info=True)
            return False

    def _load_lazy(self):
        """
        lazy loading: initialize the object with data stored in _lazyloading attribute
        will only initialize 1st level ones (and do a proper validation)
        """
        data = self._lazy_loading
        try:
            self._lazy_loading = {}
            # remove initial values of readonly members
            ros = self.__read_only__.intersection(data.keys())
            if ros:
                for ro in ros:
                    self.logger.warning('property %s is read-only. Initial value provided not used.', ro)
                data_no_ro = {k: v for k, v in data.items() if k not in self.__read_only__}
                pjo_classbuilder.ProtocolBase.__init__(self, **data_no_ro)
            else:
                pjo_classbuilder.ProtocolBase.__init__(self, **data)
            # we set key2attr after to avoid collusion at initialization between
            self._set_key2attr(data)
            return True
        except Exception as er:
            self._lazy_loading = data
            logger.warning('problem lazy loading %s' % self)
            logger.warning(er, exc_info=True)
            return False

    def _load_missing(self):
        """entry point to trigger methods which are supposed to load missing data (or lazy load)"""
        if self._ref:
            return self._load_ref()
        if self._lazy_loading:
            return self._load_lazy()
        return False

    def _set_key2attr(self, props):
        """create the map associating canonical names to properties"""
        from .metadata import Metadata
        if isinstance(self, Metadata):
            if CN_KEY in props:
                self.set_name(props[CN_KEY])
            if 'canonicalName' in props:
                if self._lazy_loading:
                    self._set_prop_value('canonicalName', props['canonicalName'])
                else:
                    self.canonicalName = props['canonicalName']
        self._key2attr = {}
        if self._attr_by_name:
            for k, v in props.items():
                if utils.is_mapping(v) and CN_KEY in v:
                    self._key2attr[v[CN_KEY]] = (k, None)
                if utils.is_sequence(v):
                    for i, v2 in enumerate(v):
                        if utils.is_mapping(v2) and CN_KEY in v2:
                            self._key2attr[v2[CN_KEY]] = (k, i)

    @classmethod
    def issubclass(cls, klass):
        """subclass specific method"""
        return pjo_util.safe_issubclass(cls, klass)

    def set_configfiles_defaults(self, overwrite=False):
        """
        Look for default values in objects_config_loader to initialize properties
        in the object.

        :param overwrite: overwrite values already set
        """
        defconf = objects_config_loader.get_values(self._fullname,
                                                   self._property_list)
        for k, v in defconf.items():
            if self._properties.get(k, None) or overwrite:
                try:
                    self.logger.debug("CONFIG SET %r.%s = %s", self, k, v)
                    setattr(self, k, v)
                except Exception as er:
                    self.logger.error(er, exc_info=True)

    @property
    def _fullname(self):
        return utils.fullname(self.__class__)

    @property
    def _property_list(self):
        """list of all available properties"""
        return itertools.chain(self._properties.keys(),
                               self._extended_properties.keys())


    def __getattr__(self, name):
        """
        Allow getting class attributes, protected attributes and protocolBase attributes
        as optimally as possible. attributes can be looked up base on their name, or by
        their canonical name, using a correspondence map done with _set_key2attr
        """
        if name in self.__class_attr_list__:
            collections.MutableMapping.__getattribute__(self, name)
        elif name.startswith("_"):
            return collections.MutableMapping.__getattribute__(self, name)
        else:
            self._load_missing()
            prop, index = self._key2attr.get(name, (None, None))
            if prop:
                return getattr(self, prop) if index is None else getattr(
                    self, prop)[index]
            name = self.__prop_translated__.get(name, name)
            return pjo_classbuilder.ProtocolBase.__getattr__(self, name)

    def __setattr__(self, name, val):
        """allow setting of protected attributes"""
        if name.startswith("_"):
            collections.MutableMapping.__setattr__(self, name, val)
        else:
            self._load_missing()
            prop, index = self._key2attr.get(name, (None, None))
            if prop:
                if index is None:
                    pjo_classbuilder.ProtocolBase.__setattr__(self, prop, val)
                else:
                    attr = getattr(self, prop)
                    attr[index] = val
            else:
                name = self.__prop_translated__.get(name, name)
                pjo_classbuilder.ProtocolBase.__setattr__(self, name, val)

    def _set_prop_value(self, prop, value):
        """
        Set a property shorcutting the setter. To be used in setters
        """
        # if the component is lazy loaded, dont force its loading now
        # add the value to the data to be loaded later and return
        if self._lazy_loading and isinstance(self._lazy_loading, dict):
            self._lazy_loading[prop] = value
            return
        propval = self._properties.get(prop)
        propinfo = self.propinfo(prop)
        if hasattr(propval, 'validate'):
            propval.__init__(value)
            propval.validate()
            # should be enough... set it back anyway ?
            self._properties[prop] = value
        # a validator is available
        elif issubclass(propinfo.get('_type'), pjo_literals.LiteralValue):
            val = propinfo['_type'](value)
            val.validate()
            self._properties[prop] = val
        else:
            prop_ = getattr(self.__class__, self.__prop_names__[prop])
            prop_.fset(self, value)

    def _get_prop_value(self, prop, default=None):
        """
        Get a property shorcutting the setter. To be used in setters
        """
        if self._lazy_loading and isinstance(self._lazy_loading, dict):
            return self._lazy_loading.get(prop, default)
        validator = self._properties.get(prop)
        if validator is not None:
            if is_property_dirty(validator):
                validator.validate()
            return validator
        return default


    @classmethod
    def one(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves exactly one instance corresponding to query
        
        Query can used all usual operators"""
        from .query import Query
        ret = list(
            Query(iter_instances(cls))._filter_or_exclude(
                *attrs, load_lazy=load_lazy, **attrs_value))
        if len(ret) == 0:
            raise ValueError('Entry %s does not exist' % attrs_value)
        elif len(ret) > 1:
            import logging
            cls.logger.error(ret)
            raise ValueError('Multiple objects returned')
        return ret[0]

    @classmethod
    def one_or_none(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves exactly one instance corresponding to query
        
        Query can used all usual operators"""
        from .query import Query
        ret = list(
            Query(iter_instances(cls))._filter_or_exclude(
                *attrs, load_lazy=load_lazy, **attrs_value))
        if len(ret) == 0:
            return None
        elif len(ret) > 1:
            import logging
            cls.logger.error(ret)
            raise ValueError('Multiple objects returned')
        return ret[0]

    @classmethod
    def first(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves exactly one instance corresponding to query
        
        Query can used all usual operators"""
        from .query import Query
        return next(
            Query(iter_instances(cls)).filter(
                *attrs, load_lazy=load_lazy, **attrs_value))

    @classmethod
    def filter(cls, *attrs, load_lazy=False, **attrs_value):
        """retrieves a list of instances corresponding to query
        
        Query can used all usual operators"""
        from .query import Query
        return list(
            Query(iter_instances(cls)).filter(
                *attrs, load_lazy=load_lazy, **attrs_value))

    @classproperty
    def instances(cls):
        return iter_instances(cls)


class ClassBuilder(pjo_classbuilder.ClassBuilder):
    """
    A modified ClassBuilder to build a class with SchemaMetaClass, to create
    properties according to schema, and associating with detected getter/setter
    or default values

    For a property PROP, the class builder will look for method called get_PROP
    or set_PROP to create the property with the setters/getters

    If a value of the same name is detected, it will attemp to use it as a
    default value.

    Additional pseudo-literal types are also handled (date, time, datetime,
    path). Those pseudo-literals will be properly deserialized/serialized
    and will provide all methods user would expect from standard python types.
        * date: datetime.date
        * time: datetime.time
        * arrow: arrow
        * path: pathlib.Path
    """
    def __init__(self, resolver):
        pjo_classbuilder.ClassBuilder.__init__(self, resolver)
        self.definitions = {}

    def resolve_or_build(self, uri, scope=None):
        resolver = self.resolver
        scope = scope or resolver.resolution_scope
        uri = resolver._urljoin_cache(scope, uri)
        if uri not in self.resolved:
            uri, schema = resolver.resolve(uri)
            self.resolved[uri] = self._construct(uri, schema)
        return self.resolved[uri]

    def _build_pseudo_literal(self, nm, clsdata, parent):
        def __getattr_pseudo__(self, name):
            """
            Special __getattr__ method to be able to use subclass methods
            directly on literal
            """
            if hasattr(self.__subclass__, name):
                if isinstance(self._value, self.__subclass__):
                    return getattr(self._value, name)
            elif hasattr(self.__class__, name):
                return getattr(self, name)
            else:
                return pjo_literals.LiteralValue.__getattribute__(self, name)

        #cls_schema = copy.deepcopy(clsdata)
        cls_schema = clsdata
        propinfo = {
            "__literal__": cls_schema,
            "__default__": cls_schema.get("default")
        }

        if 'foreignKey' in cls_schema:
            # we merge the schema in propinfo to access it directly
            fk_uri = cls_schema['foreignKey']['foreignSchemaUri']
            scope = self.resolver.resolution_scope
            fk_uri_dfg = self.resolver._urljoin_cache(scope, fk_uri)
            cls_schema['foreignKey']['foreignSchemaUri'] = fk_uri_dfg
            propinfo.update(cls_schema)
            return type(
                native_str(nm),
                (ForeignKey, ),
                {
                    "__propinfo__": propinfo,
                },
            )

        return type(
            native_str(nm),
            (pjo_literals.LiteralValue, ),
            {
                "__propinfo__": propinfo,
                "__subclass__": parent,
                "__getattr__": __getattr_pseudo__,
            },
        )

    def _construct(self, uri, clsdata, parent=(ProtocolBase, ), **kw):
        if clsdata.get("type") not in ("string", "path", "date", "time", "datetime") \
            and 'foreignKey' not in clsdata:
            return pjo_classbuilder.ClassBuilder._construct(
                    self, uri, clsdata, parent, **kw)

        typ = clsdata["type"]

        if typ == "string":
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, str)
        if typ == "path":
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, pathlib.Path)
        if typ == "date":
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, datetime.date)
        if typ == "time":
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, datetime.time)
        if typ == "datetime":
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, arrow.Arrow)
        if 'foreignKey' in clsdata:
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, ForeignKey)

        return self.resolved[uri]

    def _build_object(self, nm, clsdata, parents, **kw):
        logger.debug(pjo_util.lazy_format("Building object {0}", nm))

        # To support circular references, we tag objects that we're
        # currently building as "under construction"
        self.under_construction.add(nm)
        current_scope = self.resolver.resolution_scope

        # necessary to build type
        clsname = native_str(nm.split("/")[-1])

        props = dict()
        defaults = set()
        dependencies = dict()

        class_attrs = kw.get("class_attrs", {})

        # setup logger and make it a property
        if "logger" not in class_attrs:
            class_attrs["logger"] = logging.getLogger(clsname)

        # create a setter for logLevel
        if "logLevel" in clsdata.get("properties", {}):

            def set_logLevel(self, logLevel):
                level = logging.getLevelName(logLevel)
                self.logger.setLevel(level)

            class_attrs["set_logLevel"] = set_logLevel

        # we set class attributes as properties now, and they will be
        # overwritten if they are default values
        props.update(class_attrs)

        __object_attr_list__ = pjo_classbuilder.ProtocolBase.__object_attr_list__
        props["__object_attr_list__"] = __object_attr_list__

        props["__class_attr_list__"] = set(class_attrs.keys())

        #cls_schema = copy.deepcopy(clsdata)
        cls_schema = clsdata
        props["__schema__"] = cls_schema
        props["__schema__"]["$id"] = nm

        properties = dict()
        parent_properties = dict()

        # parent classes
        for ext in cls_schema.get("extends", []):
            uri = pjo_util.resolve_ref_uri(current_scope, ext)
            base = self.resolved.get(uri)
            if not base:
                logger.debug('resolving inherited class for %s', uri)
                schemaUri, schema = self.resolver.resolve(uri)
                base = self.resolved[uri] = self._build_object(schemaUri, schema, (ProtocolBase, ))
            if not any([issubclass(p, base) for p in parents]):
                parents = (base, ) + parents

        for p in reversed(parents):
            if issubclass(p, ProtocolBase):
                properties = pjo_util.propmerge(properties,
                                                p.__propinfo__)

        properties = pjo_util.propmerge(properties, cls_schema.get("properties",{}))


        def find_getter_setter_defv(propname, class_attrs):
            """
            Helper to retrieve getters/setters/default value in class attribute
            dictionary for a given property name
            """
            getter = None
            setter = None
            defv = None
            pn = propname
            gpn = "get_%s" % pn
            spn = "set_%s" % pn
            if pn in class_attrs:
                a = class_attrs[pn]
                if inspect.isfunction(a) or inspect.ismethod(a):
                    logger.warning(
                        pjo_util.lazy_format("{} will be overwritten",
                                             propname))
                elif inspect.isdatadescriptor(a):
                    par_prop_sch = list(dpath.util.search(class_attrs, "__schema__/properties/"+propname, yielded=True))
                    prop_sch = list(dpath.util.search(cls_schema, "properties/"+propname, yielded=True))
                    par_prop_sch = par_prop_sch[0] if par_prop_sch else {}
                    prop_sch = prop_sch[0] if prop_sch else {}
                    if all(k in prop_sch and par_prop_sch[k] == prop_sch[k] 
                        for k in par_prop_sch):
                        if propname not in parent_properties:
                            parent_properties[propname] = (a, class_attrs['__propinfo__'].get(propname, {}).get('_type'))
                    #getter = a.fget
                    #setter = a.fset
                else:
                    defv = a
            if gpn in class_attrs:
                a = class_attrs[gpn]
                if inspect.isfunction(a) or inspect.ismethod(a):
                    getter = a
            if spn in class_attrs:
                a = class_attrs[spn]
                if inspect.isfunction(a) or inspect.ismethod(a):
                    setter = a
            return getter, setter, defv

        name_translation = {}
        name_translated = {}

        for prop, detail in properties.items():
            logger.debug(
                pjo_util.lazy_format("Handling property {0}.{1}", nm, prop))
            #properties[prop]["raw_name"] = prop
            translated = re.sub(r"[^a-zA-z0-9\-_]+", "", prop)
            name_translation[prop] = translated
            if translated != prop:
                name_translated[translated] = prop
            ##name_translation[prop] = prop.replace("@", "").replace("$", "")
            prop = name_translation[prop]

            # look for getter/setter/defaultvalue first in class definition
            ogetter, osetter, odefv = find_getter_setter_defv(prop, class_attrs)
            getter, setter, defv = ogetter, osetter, odefv
            # look for missing getter/setter/defaultvalue in parent classes
            for p in reversed(parents):
                par_attrs = p.__dict__
                pgetter, psetter, pdefv = find_getter_setter_defv(
                    prop, par_attrs)
                getter = getter or pgetter
                setter = setter or psetter
                defv = defv or pdefv

            if defv is not None:
                detail["default"] = defv

            if detail.get("default") is None and detail.get("enum") is not None:
                detail['default'] = detail["enum"][0]

            if detail.get("default") is None and detail.get("type") == 'array':
                detail['default'] = []

            if detail.get("default") is not None:
                defaults.add(prop)

            if detail.get('dependencies') is not None:
                dependencies[prop] = utils.to_list(detail['dependencies'].get('additionalProperties', []))

            if prop in parent_properties:
                pprop, _typ = parent_properties[prop]
                pass
                #props[prop] = pprop
                #if _typ:
                #    properties[prop]["type"] = _typ
                #continue

            if detail.get("type", None) == "object":
                uri = "{0}/{1}_{2}".format(nm, prop, "<anonymous>")
                self.resolved[uri] = self.construct(uri, detail,
                                                    (ProtocolBase, ))

                props[prop] = make_property(
                    prop,
                    {"type": self.resolved[uri]},
                    fget=getter,
                    fset=setter,
                    desc=self.resolved[uri].__doc__,
                )
                properties[prop]["type"] = self.resolved[uri]

            elif "type" not in detail and "$ref" in detail:
                ref = detail["$ref"]
                # TODO CRN: shouldn't we retrieve also the reference and construct from it??
                uri = pjo_util.resolve_ref_uri(current_scope, ref)
                logger.debug(
                    pjo_util.lazy_format("Resolving reference {0} for {1}.{2}",
                                         ref, nm, prop))
                if uri in self.resolved:
                    typ = self.resolved[uri]
                else:
                    typ = self.construct(uri, detail, (ProtocolBase, ))

                props[prop] = make_property(
                    prop, {"type": typ},
                    fget=getter,
                    fset=setter,
                    desc=typ.__doc__)
                properties[prop]["$ref"] = uri
                properties[prop]["type"] = typ

            elif "oneOf" in detail:
                potential = self.resolve_classes(detail["oneOf"])
                logger.debug(
                    pjo_util.lazy_format("Designating {0} as oneOf {1}", prop,
                                         potential))
                desc = detail["description"] if "description" in detail else ""
                props[prop] = make_property(
                    prop, {"type": potential},
                    fget=getter,
                    fset=setter,
                    desc=desc)

            elif "type" in detail and detail["type"] == "array":
                # for resolution in create in wrapper_types
                detail['classbuilder'] = self
                if "items" in detail and isinstance(detail["items"], dict):
                    if "$ref" in detail["items"]:
                        uri = pjo_util.resolve_ref_uri(current_scope,
                                                       detail["items"]["$ref"])
                        typ = self.construct(uri, detail["items"])
                        propdata = {
                            "type":
                            "array",
                            "validator":
                            pjo_wrapper_types.ArrayWrapper.create(
                                uri, item_constraint=typ),
                        }
                    else:
                        uri = "{0}/{1}_{2}".format(nm, prop,
                                                   "<anonymous_field>")
                        try:
                            if "oneOf" in detail["items"]:
                                typ = pjo_classbuilder.TypeProxy([
                                    self.construct(uri + "_%s" % i,
                                                   item_detail)
                                    if "$ref" not in item_detail else
                                    self.construct(
                                        pjo_util.resolve_ref_uri(
                                            current_scope,
                                            item_detail["$ref"],
                                        ),
                                        item_detail,
                                    ) for i, item_detail in enumerate(detail[
                                        "items"]["oneOf"])
                                ])
                            else:

                                typ = self._construct(uri, detail["items"])
                            propdata = {
                                "type":
                                "array",
                                "validator":
                                pjo_wrapper_types.ArrayWrapper.create(
                                    uri, item_constraint=typ, **detail),
                            }
                        except NotImplementedError:
                            typ = copy.deepcopy(detail["items"])
                            propdata = {
                                "type":
                                "array",
                                "validator":
                                pjo_wrapper_types.ArrayWrapper.create(
                                    uri, item_constraint=typ, **detail),
                            }

                    props[prop] = make_property(
                        prop,
                        propdata,
                        fget=getter,
                        fset=setter,
                        desc=typ.__doc__)
                elif "items" in detail:
                    typs = []
                    for i, elem in enumerate(detail["items"]):
                        uri = "{0}/{1}/<anonymous_{2}>".format(nm, prop, i)
                        typ = self.construct(uri, elem)
                        typs.append(typ)

                    props[prop] = make_property(
                        prop, {"type": typs}, fget=getter, fset=setter)

            else:
                desc = detail["description"] if "description" in detail else ""
                uri = "{0}/{1}".format(nm, prop)
                typ = self.construct(uri, detail)

                props[prop] = make_property(
                    prop, {"type": typ}, fget=getter, fset=setter, desc=desc)
                properties[name_translated.get(prop, prop)]["_type"] = typ
        """
        If this object itself has a 'oneOf' designation, then
        make the validation 'type' the list of potential objects.
        """
        if "oneOf" in cls_schema:
            klasses = self.resolve_classes(cls_schema["oneOf"])
            # Need a validation to check that it meets one of them
            props["__validation__"] = {"type": klasses}

        props["__extensible__"] = pjo_pattern_properties.ExtensibleValidator(
            nm, cls_schema, self)

        props["__prop_names__"] = name_translation
        props['__prop_translated__'] = name_translated

        # automatically adds property names to foreign keys
        for prop_name, prop in properties.items():
            fkey = prop.get('foreignKey')
            if fkey and 'name' not in fkey:
                prop['foreignKey']['name'] = prop_name
            # case array of foreignkeys
            fkey =  prop.get('items', {}).get('foreignKey')                
            if fkey and 'name' not in fkey:
                prop['items']['foreignKey']['name'] = prop_name

        props["__propinfo__"] = properties
        required = set.union(
            *[getattr(p, "__required__", set()) for p in parents])
        read_only = set.union(
            *[getattr(p, "__read_only__", set()) for p in parents])
        not_serialized = set.union(
            *[getattr(p, "__not_serialized__", set()) for p in parents])

        required.update(cls_schema.get("required",[]))
        read_only.update(cls_schema.get("readOnly",[]))
        not_serialized.update(cls_schema.get("notSerialized",[]))

        invalid_requires = [
            req for req in required if req not in props["__propinfo__"]
        ]
        if len(invalid_requires) > 0:
            raise pjo_validators.ValidationError(
                "Schema Definition Error: {0} schema requires "
                "'{1}', but properties are not defined".format(
                    nm, invalid_requires))

        props["__required__"] = required
        props["__dependencies__"] = dependencies
        props["__read_only__"] = read_only
        props["__not_serialized__"] = not_serialized
        # default value on children force its resolution at each init
        # seems the best place to treat this special case
        #props["__has_default__"] = defaults.difference(['children'])
        props["__has_default__"] = defaults
        props["__add_logging__"] = class_attrs.get('__add_logging__', False)
        props["__attr_by_name__"] = class_attrs.get('__attr_by_name__', False)
        props["__strict__"] = required or kw.get("strict")

        cls = type(clsname, tuple(parents), props)
        self.under_construction.remove(nm)

        dp = nm.split('definitions/')
        dp = [_.strip('/') for _ in dp]
        if len(dp)>1:
            dpath.util.new(self.definitions, dp[1:], cls)
            logger.info('CREATE %s', '.'.join(dp[1:]))
        else:
            logger.info('CREATE %s', clsname)
            self.definitions[clsname] = cls

        return cls

    def from_uri(self, schemaUri):
        resolver = self.resolver
        schemaUri, schema = resolver.resolve(schemaUri)
        # default resolver uses _expand and already return a copy
        #schema = copy.deepcopy(schema)
        return self.construct(schemaUri, schema)


def touch_property(prop):
    """touch a property to force its validation later"""
    if isinstance(prop, pjo_literals.LiteralValue):
        prop._validated = False
    elif isinstance(prop, pjo_wrapper_types.ArrayWrapper):
        prop._dirty = True
        #for c in prop._typed:
        #    touch_property(c)


def is_property_dirty(prop):
    """test if a property needs validation"""
    if isinstance(prop, pjo_literals.LiteralValue):
        return (prop._validated == False)
    elif isinstance(prop, pjo_wrapper_types.ArrayWrapper):
        if prop._dirty:
            return True
        for c in prop._typed:
            if is_property_dirty(c):
                return True
    return False


def has_property_value(prop):
    if isinstance(prop, pjo_literals.LiteralValue):
        return (prop._value is not None)
    elif isinstance(prop, pjo_wrapper_types.ArrayWrapper):
        return bool(prop._data)


def make_property(prop, info, fget=None, fset=None, fdel=None, desc=""):
    # flag to know if variable is readOnly check is active
    info['RO_active'] = True

    def getprop(self):
        self._load_missing()
        self.logger.debug(pjo_util.lazy_format("GET {!r}.{!s}", self, prop))
        val = self._properties.get(prop)
        if fget and (val is None or is_property_dirty(val)):
            try:
                #self._properties[prop] = val
                info['RO_active'] = False
                setprop(self, fget(self))
            except Exception as er:
                info['RO_active'] = True
                self.logger.error( "GET {!r}.{!s}.\n%s", self, prop, er)
                raise AttributeError(
                    "Error getting property %s.\n%s" % (prop, er))
        try:
            val = self._properties[prop]
            if hasattr(val, "_pattern"):
                evaluated = jinja2.TemplatedString(val._pattern)(self)
                val._value = evaluated
                # we flag patterns as not validated as they depend on other props
                val._validated = False
                val.validate()
            if is_property_dirty(val):
                val.validate()
            return val
        except KeyError as er:
            raise AttributeError("No attribute %s" % prop)


    def setprop(self, val):
        from .metadata import Metadata
        self._load_missing()
        self.logger.debug(
            pjo_util.lazy_format("SET {!r}.{!s}={!s}", self, prop, val))
        if info['RO_active'] and prop in self.__read_only__:
            # in case default has not been set yet
            if not (prop in self.__has_default__ and self._properties.get(prop) is None):
                raise AttributeError("'%s' is read only" % prop)

        infotype = info["type"]

        if fset:
            # call the setter, and get the value stored in _properties
            if infotype:
                validator = infotype
                val = validator(val)
                self._properties[prop] = val
                fset(self, val)
                # fset is supposed to set the property with set_prop_value
                val = self._properties[prop]
            else:
                self._properties[prop] = val
                fset(self, val)
            if val and isinstance(val, Metadata):
                if val._lazy_loading:
                    val._set_prop_value('parent', self)
                else:
                    val.parent = self
            return

        if isinstance(infotype, (list, tuple)):
            ok = False
            errors = []
            type_checks = []

            for typ in infotype:
                if not isinstance(typ, dict):
                    type_checks.append(typ)
                    continue
                typ = next(t for n, t in pjo_validators.SCHEMA_TYPE_MAPPING +
                           pjo_validators.USER_TYPE_MAPPING
                           if typ["type"] == n)
                if typ is None:
                    typ = type(None)
                if isinstance(typ, (list, tuple)):
                    type_checks.extend(typ)
                else:
                    type_checks.append(typ)

            for typ in type_checks:
                if isinstance(val, typ):
                    ok = True
                    break
                elif hasattr(typ, "isLiteralClass"):
                    try:
                        validator = typ(val)
                    except Exception as e:
                        errors.append("Failed to coerce to '{0}': {1}".format(
                            typ, e))
                    else:
                        validator.validate()
                        ok = True
                        break
                elif pjo_util.safe_issubclass(typ, ProtocolBase):
                    # force conversion- thus the val rather than validator assignment
                    try:
                        if not utils.is_string(val):
                            val = typ(**pjo_util.coerce_for_expansion(val))
                        else:
                            val = typ(val)
                    except Exception as e:
                        errors.append(
                            "Failed to coerce to '%s': %s" % (typ, e))
                    else:
                        val.validate()
                        ok = True
                        break
                elif pjo_util.safe_issubclass(typ,
                                              pjo_wrapper_types.ArrayWrapper):
                    try:
                        val = typ(val)
                    except Exception as e:
                        errors.append(
                            "Failed to coerce to '%s': %s" % (typ, e))
                    else:
                        val.validate()
                        ok = True
                        break

            if not ok:
                errstr = "\n".join(errors)
                raise pjo_validators.ValidationError(
                    "Object must be one of %s: \n%s" % (infotype, errstr))

        elif infotype == "array":
            val = info["validator"](val)
            # only validate if items are not foreignKey
            if not hasattr(info["validator"].__itemtype__, '_foreignClass'):
                val.validate()
                for e in val:
                    if isinstance(e, Metadata):
                        if e._lazy_loading:
                            e._set_prop_value('parent', self)
                        else:
                            e.parent = self

        elif getattr(infotype, "isLiteralClass", False) is True:
            if not isinstance(val, infotype):
                validator = infotype(val)
                # handle case of patterns
                if utils.is_pattern(val):
                    vars = jinja2.get_variables(val)
                    self.__properties_depends_on__.setdefault(prop, [])
                    self.__properties_depends_on__[prop].extend(vars)
                    for var in vars:
                        self.__properties_depends_of__.setdefault(var, [])
                        self.__properties_depends_of__[var].append(prop)
                    validator._pattern = val
                # only validate if it s not a pattern or a foreign key
                else:
                    # it s not a pattern, remove
                    if hasattr(validator, "_pattern"):
                        delattr(validator, "_pattern")
                    if not hasattr(validator, '_foreignClass'):
                        validator.validate()
                if validator._value is not None:
                    # This allows setting of default Literal values
                    val = validator
                    if not val == self._properties.get(prop):
                        for p in self.__properties_depends_of__.get(prop, []):
                            _p = self._properties.get(prop)
                            if _p:
                                touch_property(_p)

        elif pjo_util.safe_issubclass(infotype, ProtocolBase):
            if not isinstance(val, infotype):
                if not utils.is_string(val):
                    val = infotype(**pjo_util.coerce_for_expansion(val))
                else:
                    val = infotype(val)
            val.validate()

        elif isinstance(infotype, pjo_classbuilder.TypeProxy):
            val = infotype(val)

        elif isinstance(infotype, pjo_classbuilder.TypeRef):
            if not isinstance(val, infotype.ref_class):
                if utils.is_string(val):
                    val = infotype(val)
                else:
                    val = infotype(**val)

            val.validate()

        elif infotype is None:
            # This is the null value
            if val is not None:
                raise pjo_validators.ValidationError(
                    "None is only valid value for null")

        else:
            raise TypeError("Unknown object type: '%s'" % infotype)

        if val and isinstance(val, Metadata):
            if val._lazy_loading:
                val._set_prop_value('parent', self)
            else:
                val.parent = self
        self._properties[prop] = val


    def delprop(self):
        self._load_missing()
        self.logger.debug(pjo_util.lazy_format("DEL {!r}.{!s}", self, prop))
        if prop in self.__required__:
            raise AttributeError("'%s' is required" % prop)
        else:
            if fdel:
                fdel(self)
            del self._properties[prop]

    return property(getprop, setprop, delprop, desc)



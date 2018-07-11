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
from .canonical_name import get_cname
from .config import ConfigLoader
from .resolver import DEFAULT_MS_URI
from .resolver import get_resolver
from .uri_identifier import norm_uri
from .uri_identifier import resolve_uri
from .validators import DefaultValidator

logger = pjo_classbuilder.logger

_NEW_TYPES = ngo_pjo_validators.NGO_TYPE_MAPPING

# loader to register module with a transforms folder where to look for model transformations
models_module_loader = utils.GenericModuleFileLoader('models')

# loader of objects default configuration
objects_config_loader = ConfigLoader()

_default_builder = None


def get_builder(resolver=None):
    global _default_builder
    if _default_builder is None:
        _default_builder = ClassBuilder(resolver or get_resolver())
    else:
        base_uri = _default_builder.resolver.base_uri
        resolver = resolver or get_resolver(base_uri)
        _default_builder.resolver = resolver
    return _default_builder


def get_descendant(obj, key_list, load_lazy=False):
    """
    Get descendant in an object/dictionary by providing the path as a list of keys
    :param obj: object to iterate
    :param key_list: list of keys
    :param load_lazy: in case of lazy loaded object, force loading
    """
    if load_lazy and getattr(obj, '_lazy_loading', {}):
        obj.load_lazy()
    elif getattr(obj, '_lazy_loading', {}):
        try:
            return get_cname(key_list, obj._lazy_loading)
        except Exception as er:
            return None
    k0 = key_list[0]
    if hasattr(obj, k0):
        child = getattr(obj, k0)
    else:
        child = obj[k0] if k0 in obj else None
    return child if len(key_list) == 1 else get_descendant(
        child, key_list[1:], load_lazy)


class ProtocolBase(pjo_classbuilder.ProtocolBase):
    __doc__ = pjo_classbuilder.ProtocolBase.__doc__

    # additional private and protected props
    __class_attr_list__ = set()
    _short_repr_ = True
    _name = None
    _parent = None
    _key2attr = {}
    _lazy_loading = {}
    _ref = None
    _validator = None

    def __new__(cls, schemaUri=None, *args, **props):
        if props.get('lazy_loading', False) and props.get(
                'validate_lazy', True) and cls._validator is None:
            cls._validator = DefaultValidator(
                cls.__schema__, resolver=get_resolver())
            cls._validator._setDefaults = True
        # specific treatment in case schemaUri redefines the class to create
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
        return new(cls, *args, **props)

    def __init__(self, lazy_loading=False, validate_lazy=True, *args, **props):
        if self._name is not None:
            # already initialized calling __new__ with schemaUri
            # no workaround found tricking __new__ to subclass on the fly
            return

        # reference to property extern to document to be resolved later
        if '$ref' in props:
            self._ref = props.pop('$ref')
            self._load_ref()

        self._set_key2attr(props)

        if lazy_loading:
            # validate data to make sure no problem will appear at creation
            if validate_lazy:
                self._validator.validate(props)
            # lazy loading treatment: add a flag to 1st level objects data only
            # in level 1, lazy_loading is removed calling __init__
            for k, v in props.items():
                if utils.is_mapping(v):
                    v['lazy_loading'] = True
                if utils.is_sequence(v):
                    for i, v2 in enumerate(v):
                        if utils.is_mapping(v2):
                            v2['lazy_loading'] = True
            self._lazy_loading = props

        if not self._lazy_loading and not self._ref:
            self._set_key2attr(props)
            pjo_classbuilder.ProtocolBase.__init__(self, **props)
        else:
            # necessary for proper behaviour of object, normally done in init
            self._extended_properties = dict()
            self._properties = dict(
                zip(self.__prop_names__.values(),
                    [None
                     for x in six.moves.xrange(len(self.__prop_names__))]))

    def _load_ref(self):
        try:
            data = resolve_uri(self._ref)
            self._validator.validate(data)
            self._set_key2attr(data)
            self._lazy_loading = data
            self._ref = None
        except Exception as er:
            logger.warning(er, exc_info=True)

    def _load_lazy(self):
        # lazy loading: initialize the object with data stored in _lazyloading attribute
        # will only initialize 1st level ones (and do a proper validation)
        data = self._lazy_loading
        try:
            self._lazy_loading = {}
            pjo_classbuilder.ProtocolBase.__init__(self, **data)
        except Exception as er:
            self._lazy_loading = data
            logger.warning(er, exc_info=True)

    def _load_missing(self):
        if self._ref:
            self._load_ref()
        if self._lazy_loading:
            self._load_lazy()

    def _set_key2attr(self, props):
        self._name = re.sub(r"[^a-zA-z0-9\-_]+", "", props.get(
            CN_KEY, "")) or "<anonymous>"
        # create the map associating canonical names to properties
        self._key2attr = {}
        if getattr(self, '__attr_by_name__', False):
            for k, v in props.items():
                if utils.is_mapping(v) and CN_KEY in v:
                    self._key2attr[v[CN_KEY]] = (k, None)
                if utils.is_sequence(v):
                    for i, v2 in enumerate(v):
                        if utils.is_mapping(v2) and CN_KEY in v2:
                            self._key2attr[v2[CN_KEY]] = (k, i)

    def get_cname(self):
        return '%s.%s' % (self._parent.cname,
                          self._name) if self._parent else self._name

    cname = property(get_cname)

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
        return itertools.chain(self._properties.keys(),
                               self._extended_properties.keys())

    def __repr__(self):
        if not self._short_repr_:
            return pjo_classbuilder.ProtocolBase.__repr__(self)
        repr = self.__class__.__name__
        if self.cname:
            repr += ' name=%s' % self.cname
        return "<%s id=%i>" % (repr, id(self))

    def __getattr__(self, name):
        """
        Allow getting class attributes, protected attributes and
        protocolBase attributes
        """
        if name in self.__class_attr_list__:
            collections.MutableMapping.__getattribute__(self, name)
        elif name.startswith("_"):
            return collections.MutableMapping.__getattribute__(self, name)
        else:
            self._load_missing()
            if name in self._key2attr:
                prop, index = self._key2attr[name]
                return getattr(self, prop) if index is None else getattr(
                    self, prop)[index]
            if name in self.__prop_translated__:
                name = self.__prop_translated__[name]
            return pjo_classbuilder.ProtocolBase.__getattr__(self, name)

    def __setattr__(self, name, val):
        """allow setting of protected attributes"""
        if name.startswith("_"):
            collections.MutableMapping.__setattr__(self, name, val)
        else:
            self._load_missing()
            if name in self._key2attr:
                prop, index = self._key2attr[name]
                if index is None:
                    pjo_classbuilder.ProtocolBase.__setattr__(self, prop, val)
                else:
                    getattr(self, prop)[index] = val
            else:
                if name in self.__prop_translated__:
                    name = self.__prop_translated__[name]
                pjo_classbuilder.ProtocolBase.__setattr__(self, name, val)

    def _set_prop_value(self, prop, value):
        """
        Set a property shorcutting the setter. To be used in setters
        """
        validator = self._properties.get(prop, None)
        if hasattr(validator, "validate"):
            validator(value)
            validator.validate()
        else:
            self._properties[prop] = value

    def _get_prop_value(self, prop):
        """
        Get a property shorcutting the setter. To be used in setters
        """
        if self._properties.get(prop, None) is not None:
            return self._properties[prop].for_json()


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

    def _build_pseudo_literal(self, nm, clsdata, parent):
        def __getattr__(self, name):
            """
            Special __getattr__ method to be able to use subclass methods
            directly on literal
            """
            if hasattr(self.__subclass__, name):
                return getattr(self._value, name)
            else:
                return pjo_literals.LiteralValue.__getattribute__(self, name)

        return type(
            native_str(nm),
            (pjo_literals.LiteralValue, ),
            {
                "__propinfo__": {
                    "__literal__": clsdata,
                    "__default__": clsdata.get("default"),
                },
                "__subclass__": parent,
                "__getattr__": __getattr__,
            },
        )

    def _construct(self, uri, clsdata, parent=(ProtocolBase, ), **kw):
        if clsdata.get("type") not in ("path", "date", "time", "datetime"):
            return pjo_classbuilder.ClassBuilder._construct(
                self, uri, clsdata, parent, **kw)

        typ = clsdata["type"]

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

        props["__schema__"] = copy.deepcopy(clsdata)
        props["__schema__"]["$id"] = nm

        properties = dict()

        # parent classes
        for ext in clsdata.get("extends", []):
            uri = pjo_util.resolve_ref_uri(current_scope, ext)
            if uri in self.resolved:
                base = self.resolved[uri]
                if not any([issubclass(p, base) for p in parents]):
                    parents = (base, ) + parents

        for p in reversed(parents):
            properties = pjo_util.propmerge(properties,
                                            getattr(p, "__propinfo__", {}))

        if "properties" in clsdata:
            properties = pjo_util.propmerge(properties, clsdata["properties"])

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
                    pass
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
            getter, setter, defv = find_getter_setter_defv(prop, class_attrs)
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
                                typ = self.construct(uri, detail["items"])
                            propdata = {
                                "type":
                                "array",
                                "validator":
                                pjo_wrapper_types.ArrayWrapper.create(
                                    uri, item_constraint=typ, **detail),
                            }
                        except NotImplementedError:
                            typ = detail["items"]
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
        """
        If this object itself has a 'oneOf' designation, then
        make the validation 'type' the list of potential objects.
        """
        if "oneOf" in clsdata:
            klasses = self.resolve_classes(clsdata["oneOf"])
            # Need a validation to check that it meets one of them
            props["__validation__"] = {"type": klasses}

        props["__extensible__"] = pjo_pattern_properties.ExtensibleValidator(
            nm, clsdata, self)

        props["__prop_names__"] = name_translation
        props['__prop_translated__'] = name_translated

        props["__propinfo__"] = properties
        # required = set.union(*[p.__required__ for p in parents])
        required = set.union(
            *[getattr(p, "__required__", set()) for p in parents])

        if "required" in clsdata:
            for prop in clsdata["required"]:
                required.add(prop)

        invalid_requires = [
            req for req in required if req not in props["__propinfo__"]
        ]
        if len(invalid_requires) > 0:
            raise pjo_validators.ValidationError(
                "Schema Definition Error: {0} schema requires "
                "'{1}', but properties are not defined".format(
                    nm, invalid_requires))

        props["__required__"] = required
        props["__has_default__"] = defaults
        props["__add_logging__"] = class_attrs.get('__add_logging__', False)
        props["__attr_by_name__"] = class_attrs.get('__attr_by_name__', False)
        props["__strict__"] = required or kw.get("strict")

        cls = type(clsname, tuple(parents), props)
        self.under_construction.remove(nm)

        return cls


def make_property(prop, info, fget=None, fset=None, fdel=None, desc=""):
    # flag to know if variable is readOnly
    RO = "readOnly" in info and info["readOnly"]
    RO_active = RO

    def getprop(self):
        self._load_missing()
        self.logger.debug(pjo_util.lazy_format("GET {!r}.{!s}", self, prop))
        #self.logger.debug("GET %r.%s", self, prop)
        if fget:
            try:
                RO_active = False
                setprop(self, fget(self))
            except Exception as er:
                RO_active = RO
                raise AttributeError(
                    "Error getting property %s.\n%s" % (prop, er.message))
        try:
            val = self._properties[prop]
            if hasattr(val, "_pattern"):
                evaluated = jinja2.TemplatedString(val._pattern)(self)
                val._value = evaluated
                # we flag patterns as not validated as they depend on other props
                val._validated = False
                val.validate()
            return val
        except KeyError:
            raise AttributeError("No attribute %s" % prop)

    def setprop(self, val):
        self._load_missing()
        self.logger.debug(
            pjo_util.lazy_format("SET {!r}.{!s}={!s}", self, prop, val))
        #self.logger.debug("SET %r.%s=%s", self, prop, val)
        if RO_active:
            raise AttributeError("'%s' is read only" % prop)

        if fset and self._properties[prop] is not None:
            # call the setter, and get the value stored in _properties
            fset(self, val)
            val = self._properties[prop]

        if isinstance(info["type"], (list, tuple)):
            ok = False
            errors = []
            type_checks = []

            for typ in info["type"]:
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
                        val = typ(**pjo_util.coerce_for_expansion(val))
                    except Exception as e:
                        errors.append(
                            "Failed to coerce to '%s': %s" % (typ, e))
                    else:
                        val.validate()
                        val._parent = self
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
                        val._parent = self
                        ok = True
                        break

            if not ok:
                errstr = "\n".join(errors)
                raise pjo_validators.ValidationError(
                    "Object must be one of %s: \n%s" % (info["type"], errstr))

        elif info["type"] == "array":
            val = info["validator"](val)
            val.validate()
            for e in val:
                if isinstance(e,
                              (ProtocolBase, pjo_wrapper_types.ArrayWrapper)):
                    e._parent = self

        elif pjo_util.safe_issubclass(info["type"],
                                      pjo_wrapper_types.ArrayWrapper):
            raise Exception('WAS I EVER THERE???')
            # An array type may have already been converted into an ArrayValidator
            val = info["type"](val)
            val.validate()
            for e in val:
                if isinstance(e,
                              (ProtocolBase, pjo_wrapper_types.ArrayWrapper)):
                    e._parent = self

        elif getattr(info["type"], "isLiteralClass", False) is True:
            if not isinstance(val, info["type"]):
                validator = info["type"](val)
                # handle case of patterns
                if utils.is_pattern(val):
                    validator._pattern = val
                # only validate if it s not a pattern
                else:
                    # it s not a pattern, remove
                    if hasattr(validator, "_pattern"):
                        delattr(validator, "_pattern")
                    validator.validate()
                if validator._value is not None:
                    # This allows setting of default Literal values
                    val = validator

        elif pjo_util.safe_issubclass(info["type"], ProtocolBase):
            if not isinstance(val, info["type"]):
                val = info["type"](**pjo_util.coerce_for_expansion(val))
            val.validate()
            val._parent = self

        elif isinstance(info["type"], pjo_classbuilder.TypeProxy):
            val = info["type"](val)

        elif isinstance(info["type"], pjo_classbuilder.TypeRef):
            if not isinstance(val, info["type"].ref_class):
                val = info["type"](**val)

            val.validate()

        elif info["type"] is None:
            # This is the null value
            if val is not None:
                raise pjo_validators.ValidationError(
                    "None is only valid value for null")

        else:
            raise TypeError("Unknown object type: '%s'" % info["type"])

        self._properties[prop] = val

    def delprop(self):
        self._load_missing()
        self.logger.debug(pjo_util.lazy_format("DEL {!r}.{!s}", self, prop))
        #self.logger.debug("DEL %r.%s", self, prop)
        if prop in self.__required__:
            raise AttributeError("'%s' is required" % prop)
        else:
            if fdel:
                fdel(self)
            del self._properties[prop]

    return property(getprop, setprop, delprop, desc)

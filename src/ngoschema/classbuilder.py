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
import datetime
import gettext
import inspect
import logging
import pathlib
from builtins import object

import arrow
import python_jsonschema_objects.classbuilder as pjo_classbuilder
import python_jsonschema_objects.literals as pjo_literals
import python_jsonschema_objects.pattern_properties as pjo_pattern_properties
import python_jsonschema_objects.util as pjo_util
import python_jsonschema_objects.validators as pjo_validators
import python_jsonschema_objects.wrapper_types as pjo_wrapper_types
from future.utils import text_to_native_str as native_str

from . import jinja2
from . import pjo_validators as ngo_pjo_validators
from . import utils
from .config import ConfigLoader

_ = gettext.gettext

logger = pjo_classbuilder.logger

_NEW_TYPES = ngo_pjo_validators.NGO_TYPE_MAPPING


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
                pjo_util.lazy_format("{} will be overwritten", propname))
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


class ProtocolBase(pjo_classbuilder.ProtocolBase):
    __doc__ = pjo_classbuilder.ProtocolBase.__doc__

    __class_attr_list__ = set()

    def __new__(cls, *args, **kwargs):
        new = super(pjo_classbuilder.ProtocolBase, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):

        # convert arguments that might are given as imported objects
        propnames = self.__prop_names__.values()
        for k, v in kwargs.items():
            if k in propnames and not utils.is_string(v) and utils.is_imported(
                    v):
                kwargs[k] = utils.fullname(v)

        # initialize Protocol Base
        pjo_classbuilder.ProtocolBase.__init__(self, **kwargs)

        # we wait for init to be done in protocolbase, as many things to get
        # attribute lookup need to be done
        try:
            defconf = ConfigLoader(singleton=True).get_values(
                self.fullname, self.__prop_names__.values())
            for k, v in defconf.items():
                if k not in kwargs:
                    try:
                        self.logger.debug(
                            "CONFIG SET %s.%s = %s" % (self.alt_repr(), k, v))
                        setattr(self, k, v)
                    except Exception as er:
                        pass
        except Exception as er:
            pass

    @property
    def fullname(self):
        return utils.fullname(self.__class__)

    def alt_repr(self):
        return "<%s id=%i>" % (self.__class__.__name__, id(self))

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
            return pjo_classbuilder.ProtocolBase.__getattr__(self, name)

    def __setattr__(self, name, val):
        """allow setting of protected attributes"""
        if name.startswith("_"):
            collections.MutableMapping.__setattr__(self, name, val)
        else:
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
                return object.__getattr__(self, name)

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

        # necessary to build type
        clsname = native_str(nm.split("/")[-1])

        props = {}
        defaults = set()

        class_attrs = kw.get("class_attrs", {})

        # setup logger and make it a property
        if "logger" not in class_attrs:
            class_attrs["__logger__"] = logging.getLogger(clsname)

            def get_logger(self):
                return self.__logger__

            class_attrs["logger"] = property(get_logger, doc="class logger")

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

        properties = {}

        for p in parents:
            properties = pjo_util.propmerge(properties,
                                            getattr(p, "__propinfo__", {}))

        if "properties" in clsdata:
            properties = pjo_util.propmerge(properties, clsdata["properties"])

        name_translation = {}

        for prop, detail in properties.items():
            logger.debug(
                pjo_util.lazy_format("Handling property {0}.{1}", nm, prop))
            properties[prop]["raw_name"] = prop
            name_translation[prop] = prop.replace("@", "").replace("$", "")
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

            if detail.get("default", None) is not None:
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
                uri = pjo_util.resolve_ref_uri(self.resolver.resolution_scope,
                                               ref)
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
                if "items" in detail and isinstance(detail["items"], dict):
                    if "$ref" in detail["items"]:
                        uri = pjo_util.resolve_ref_uri(
                            self.resolver.resolution_scope,
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
                                            self.resolver.resolution_scope,
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
                                    uri,
                                    item_constraint=typ,
                                    addl_constraints=detail),
                            }
                        except NotImplementedError:
                            typ = detail["items"]
                            propdata = {
                                "type":
                                "array",
                                "validator":
                                pjo_wrapper_types.ArrayWrapper.create(
                                    uri,
                                    item_constraint=typ,
                                    addl_constraints=detail),
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
        if required and kw.get("strict"):
            props["__strict__"] = True

        cls = type(clsname, tuple(parents), props)
        self.under_construction.remove(nm)

        return cls


def make_property(prop, info, fget=None, fset=None, fdel=None, desc=""):
    # flag to know if variable is readOnly
    RO = "readOnly" in info and info["readOnly"]
    RO_active = RO

    def getprop(self):
        self.logger.debug("GET %s.%s" % (self.alt_repr(), prop))
        if fget:
            try:
                RO_active = False
                setprop(self, fget(self))
            except Exception as er:
                RO_active = RO
                raise AttributeError(
                    _("Error getting property %s.\n%s" % (prop, er.message)))
        try:
            val = self._properties[prop]
            if hasattr(val, "_pattern"):
                evaluated = jinja2.templatedString(val._pattern)(self)
                val._value = evaluated
                val.validate()
            return val
        except KeyError:
            raise AttributeError(_("No attribute %s" % prop))

    def setprop(self, val):
        self.logger.debug("SET %s.%s=%s" % (self.alt_repr(), prop, val))
        if RO_active:
            raise AttributeError(_("'%s' is read only" % prop))

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
                            _("Failed to coerce to '%s': %s" % (typ, e)))
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
                            _(("Failed to coerce to '%s': %s") % (typ, e)))
                    else:
                        val.validate()
                        ok = True
                        break

            if not ok:
                errstr = "\n".join(errors)
                raise pjo_validators.ValidationError(
                    _("Object must be one of %s: \n%s" % (info["type"],
                                                          errstr)))

        elif info["type"] == "array":
            val = info["validator"](val)
            val.validate()

        elif pjo_util.safe_issubclass(info["type"],
                                      pjo_wrapper_types.ArrayWrapper):
            # An array type may have already been converted into an ArrayValidator
            val = info["type"](val)
            val.validate()

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
                    _("None is only valid value for null"))

        else:
            raise TypeError(_("Unknown object type: '%s'" % (info["type"])))

        self._properties[prop] = val

    def delprop(self):
        self.logger.debug("DEL %s.%s" % (self.alt_repr(), prop))
        if prop in self.__required__:
            raise AttributeError(_("'%s' is required" % prop))
        else:
            if fdel:
                fdel(self)
            del self._properties[prop]

    return property(getprop, setprop, delprop, desc)

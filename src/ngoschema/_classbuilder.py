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

import gettext
import inspect
import logging
import pathlib
import arrow
import datetime
from builtins import object
from builtins import str

import python_jsonschema_objects.classbuilder as pjo_classbuilder
import python_jsonschema_objects.literals as pjo_literals
import python_jsonschema_objects.validators as pjo_validators
import python_jsonschema_objects.pattern_properties as pjo_pattern_properties
import python_jsonschema_objects.util as pjo_util
import python_jsonschema_objects.wrapper_types
from python_jsonschema_objects.validators import ValidationError

from . import _jso_validators

from future.utils import text_to_native_str as native_str

_ = gettext.gettext

#from ngoschema import _jso_validators as ngo_validators

def find_getter_setter_defv(propname, class_attrs):
    getter = None
    setter = None
    defv = None
    pn = propname
    gpn = 'get_%s' % pn
    spn = 'set_%s' % pn
    if pn in class_attrs:
        a = class_attrs.pop(pn)
        if inspect.isfunction(a) or inspect.ismethod(a):
            getter = a
        elif inspect.isdatadescriptor(a):
            getter = a.fget
            setter = a.fset
        else:
            defv = a
    if gpn in class_attrs:
        a = class_attrs.pop(gpn)
        if inspect.isfunction(a) or inspect.ismethod(a):
            getter = a
    if spn in class_attrs:
        a = class_attrs.pop(spn)
        if inspect.isfunction(a) or inspect.ismethod(a):
            setter = a
    return getter, setter, defv, class_attrs


class ProtocolBase(pjo_classbuilder.ProtocolBase):
    __doc__ = pjo_classbuilder.ProtocolBase.__doc__

    def __new__(cls, *args, **kwargs):
        new = super(pjo_classbuilder.ProtocolBase, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        pjo_classbuilder.ProtocolBase.__init__(self, **kwargs)

    def __getattr__(self, name):
        if name in self.__object_attr_list__:
            return object.__getattribute__(self, name)
        if name in self.__prop_names__:
            raise KeyError(name)
        if name in self._extended_properties:
            return self._extended_properties[name]
        
        raise AttributeError("{0} is not a valid attribute of {1}".format(
            name, self.__class__.__name__))


class ClassBuilder(pjo_classbuilder.ClassBuilder):
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

        return type(native_str(nm), (pjo_literals.LiteralValue,) , {
            '__propinfo__': {
                '__literal__': clsdata,
                '__default__': clsdata.get('default')
            },
            '__subclass__': parent,
            '__getattr__': __getattr__

        })

    def _construct(self, uri, clsdata, parent=(ProtocolBase,),**kw):
        if clsdata.get('type') not in ('path', 'date', 'time', 'datetime'):
            return pjo_classbuilder.ClassBuilder._construct(self, uri, clsdata, parent, **kw)

        typ = clsdata['type']

        if typ == 'path':
            self.resolved[uri] = self._build_pseudo_literal(uri, clsdata,
                                                            pathlib.Path)
        if typ == 'date':
            self.resolved[uri] = self._build_pseudo_literal(uri, clsdata,
                                                            datetime.date)
        if typ == 'time':
            self.resolved[uri] = self._build_pseudo_literal(uri, clsdata,
                                                            datetime.time)
        if typ == 'datetime':
            self.resolved[uri] = self._build_pseudo_literal(uri, clsdata,
                                                            arrow.Arrow)

        return self.resolved[uri]

    def _build_object(self, nm, clsdata, parents, **kw):
        logger = pjo_classbuilder.logger
        logger.debug(pjo_util.lazy_format("Building object {0}", nm))

        # To support circular references, we tag objects that we're
        # currently building as "under construction"
        self.under_construction.add(nm)

        # necessary to build type
        clsname = native_str(nm.split('/')[-1])

        props = {}
        defaults = set()

        class_attrs = kw.get('class_attrs', {})

        # setup logger and make it a property
        if 'logger' not in class_attrs:
            class_attrs['__logger__'] = logging.getLogger(clsname)
            def get_logger(self):
                return self.__logger__
            class_attrs['logger'] = property(get_logger, doc='class logger')

        # create a setter for logLevel
        if 'logLevel' in clsdata.get('properties', {}):
            def set_logLevel(self, logLevel):
                level = logging.getLevelName(logLevel)
                self.logger.setLevel(level)
            class_attrs['set_logLevel'] = set_logLevel


        __object_attr_list__ = ProtocolBase.__object_attr_list__

        props['__object_attr_list__'] = __object_attr_list__

        properties = {}
        for p in parents:
            #properties = pjo_util.propmerge(properties, p.__propinfo__)
            properties = pjo_util.propmerge(properties,
                                            getattr(p, '__propinfo__', {}))

        if 'properties' in clsdata:
            properties = pjo_util.propmerge(properties, clsdata['properties'])

        name_translation = {}

        for prop, detail in properties.items():
            logger.debug(
                pjo_util.lazy_format("Handling property {0}.{1}", nm, prop))
            properties[prop]['raw_name'] = prop
            name_translation[prop] = prop.replace('@', '').replace('$', '')
            prop = name_translation[prop]

            # look for getter/setter/defaultvalue first in class definition
            getter, setter, defv, class_attrs = find_getter_setter_defv(
                prop, class_attrs)
            # look for missing getter/setter/defaultvalue in parent classes
            for p in reversed(parents):
                par_attrs = p.__dict__
                pgetter, psetter, pdefv, par_attrs = find_getter_setter_defv(
                    prop, par_attrs)
                getter = getter or pgetter
                setter = setter or psetter
                defv = defv or pdefv

            if detail.get('default', None) is not None:
                defaults.add(prop)

            if detail.get('type', None) == 'object':
                uri = "{0}/{1}_{2}".format(nm, prop, "<anonymous>")
                self.resolved[uri] = self.construct(uri, detail,
                                                    (ProtocolBase, ))

                props[prop] = make_property(
                    prop, {'type': self.resolved[uri]},
                    fget=getter,
                    fset=setter,
                    desc=self.resolved[uri].__doc__)
                properties[prop]['type'] = self.resolved[uri]

            elif 'type' not in detail and '$ref' in detail:
                ref = detail['$ref']
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
                    prop, {'type': typ},
                    fget=getter,
                    fset=setter,
                    desc=typ.__doc__)
                properties[prop]['$ref'] = uri
                properties[prop]['type'] = typ

            elif 'oneOf' in detail:
                potential = self.resolve_classes(detail['oneOf'])
                logger.debug(
                    pjo_util.lazy_format("Designating {0} as oneOf {1}", prop,
                                         potential))
                desc = detail['description'] if 'description' in detail else ""
                props[prop] = make_property(
                    prop, {'type': potential},
                    fget=getter,
                    fset=setter,
                    desc=desc)

            elif 'type' in detail and detail['type'] == 'array':
                if 'items' in detail and isinstance(detail['items'], dict):
                    if '$ref' in detail['items']:
                        uri = pjo_util.resolve_ref_uri(
                            self.resolver.resolution_scope,
                            detail['items']['$ref'])
                        typ = self.construct(uri, detail['items'])
                        propdata = {
                            'type':
                            'array',
                            'validator':
                            python_jsonschema_objects.wrapper_types.
                            ArrayWrapper.create(uri, item_constraint=typ)
                        }
                    else:
                        uri = "{0}/{1}_{2}".format(nm, prop,
                                                   "<anonymous_field>")
                        try:
                            if 'oneOf' in detail['items']:
                                typ = pjo_classbuilder.TypeProxy([
                                    self.construct(uri + "_%s" % i,
                                                   item_detail)
                                    if '$ref' not in item_detail else
                                    self.construct(
                                        pjo_util.resolve_ref_uri(
                                            self.resolver.resolution_scope,
                                            item_detail['$ref']), item_detail)
                                    for i, item_detail in enumerate(
                                        detail['items']['oneOf'])
                                ])
                            else:
                                typ = self.construct(uri, detail['items'])
                            propdata = {
                                'type':
                                'array',
                                'validator':
                                python_jsonschema_objects.wrapper_types.
                                ArrayWrapper.create(
                                    uri,
                                    item_constraint=typ,
                                    addl_constraints=detail)
                            }
                        except NotImplementedError:
                            typ = detail['items']
                            propdata = {
                                'type':
                                'array',
                                'validator':
                                python_jsonschema_objects.wrapper_types.
                                ArrayWrapper.create(
                                    uri,
                                    item_constraint=typ,
                                    addl_constraints=detail)
                            }

                    props[prop] = make_property(
                        prop,
                        propdata,
                        fget=getter,
                        fset=setter,
                        desc=typ.__doc__)
                elif 'items' in detail:
                    typs = []
                    for i, elem in enumerate(detail['items']):
                        uri = "{0}/{1}/<anonymous_{2}>".format(nm, prop, i)
                        typ = self.construct(uri, elem)
                        typs.append(typ)

                    props[prop] = make_property(
                        prop, {'type': typs}, fget=getter, fset=setter)

            else:
                desc = detail['description'] if 'description' in detail else ""
                uri = "{0}/{1}".format(nm, prop)
                typ = self.construct(uri, detail)

                props[prop] = make_property(
                    prop, {'type': typ}, fget=getter, fset=setter, desc=desc)
        """ If this object itself has a 'oneOf' designation, then
        make the validation 'type' the list of potential objects.
        """
        if 'oneOf' in clsdata:
            klasses = self.resolve_classes(clsdata['oneOf'])
            # Need a validation to check that it meets one of them
            props['__validation__'] = {'type': klasses}

        props['__extensible__'] = pjo_pattern_properties.ExtensibleValidator(
            nm, clsdata, self)

        props['__prop_names__'] = name_translation

        props['__propinfo__'] = properties
        #required = set.union(*[p.__required__ for p in parents])
        required = set.union(
            *[getattr(p, '__required__', set()) for p in parents])

        if 'required' in clsdata:
            for prop in clsdata['required']:
                required.add(prop)

        invalid_requires = [
            req for req in required if req not in props['__propinfo__']
        ]
        if len(invalid_requires) > 0:
            raise pjo_validators.ValidationError(
                "Schema Definition Error: {0} schema requires "
                "'{1}', but properties are not defined".format(
                    nm, invalid_requires))

        props['__required__'] = required
        props['__has_default__'] = defaults
        if required and kw.get("strict"):
            props['__strict__'] = True

        props.update(class_attrs)

        cls = type(clsname, tuple(parents), props)
        self.under_construction.remove(nm)

        return cls


def make_property(prop, info, fget=None, fset=None, fdel=None, desc=""):
    # flag to know if variable is readOnly
    RO = 'readOnly' in info and info['readOnly']
    RO_active = RO

    def getprop(self):
        self.logger.debug('GET %s.%s' % (self.__class__.__name__, prop))
        if fget:
            try:
                RO_active = False
                setprop(self, fget(self))
            except Exception as er:
                RO_active = RO
                raise AttributeError(_("Error getting property %s.\n%s"%(prop,er.message)))
        try:
            return self._properties[prop]
        except KeyError:
            raise AttributeError(_("No attribute %s" % prop))

    def setprop(self, val):
        self.logger.debug('SET %s.%s=%s' % (self.__class__.__name__, prop,
                                            val))
        if RO_active:
            raise AttributeError(_("'%s' is read only" % prop))

        if isinstance(info['type'], (list, tuple)):
            ok = False
            errors = []
            type_checks = []

            for typ in info['type']:
                if not isinstance(typ, dict):
                    type_checks.append(typ)
                    continue
                typ = next(t for n, t in pjo_validators.SCHEMA_TYPE_MAPPING
                                       + pjo_validators.USER_TYPE_MAPPING
                           if typ['type'] == n)
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
                elif hasattr(typ, 'isLiteralClass'):
                    try:
                        validator = typ(val)
                    except Exception as e:
                        errors.append("Failed to coerce to '{0}': {1}".format(
                            typ, e))
                        pass
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
                        pass
                    else:
                        val.validate()
                        ok = True
                        break
                elif pjo_util.safe_issubclass(
                        typ,
                        python_jsonschema_objects.wrapper_types.ArrayWrapper):
                    try:
                        val = typ(val)
                    except Exception as e:
                        errors.append(
                            _(("Failed to coerce to '%s': %s") % (typ, e)))
                        pass
                    else:
                        val.validate()
                        ok = True
                        break

            if not ok:
                errstr = "\n".join(errors)
                raise pjo_validators.ValidationError(
                    _("Object must be one of %s: \n%s" % (info['type'],
                                                          errstr)))

        elif info['type'] == 'array':
            val = info['validator'](val)
            val.validate()

        elif pjo_util.safe_issubclass(
                info['type'],
                python_jsonschema_objects.wrapper_types.ArrayWrapper):
            # An array type may have already been converted into an ArrayValidator
            val = info['type'](val)
            val.validate()

        elif getattr(info['type'], 'isLiteralClass', False) is True:
            if not isinstance(val, info['type']):
                validator = info['type'](val)
                validator.validate()
                if validator._value is not None:
                    # This allows setting of default Literal values
                    val = validator

        elif pjo_util.safe_issubclass(info['type'], ProtocolBase):
            if not isinstance(val, info['type']):
                val = info['type'](**pjo_util.coerce_for_expansion(val))

            val.validate()

        elif isinstance(info['type'], pjo_classbuilder.TypeProxy):
            val = info['type'](val)

        elif isinstance(info['type'], pjo_classbuilder.TypeRef):
            if not isinstance(val, info['type'].ref_class):
                val = info['type'](**val)

            val.validate()

        elif info['type'] is None:
            # This is the null value
            if val is not None:
                raise pjo_validators.ValidationError(
                    _("None is only valid value for null"))

        else:
            raise TypeError(_("Unknown object type: '%s'" % (info['type'])))

        self._properties[prop] = val
        if fset:
            fset(self, val)

    def delprop(self):
        self.logger.debug('DEL %s' % (self.__class__.__name__, prop))
        if prop in self.__required__:
            raise AttributeError(_("'%s' is required" % prop))
        else:
            if fdel:
                fdel(self)
            del self._properties[prop]

    return property(getprop, setprop, delprop, desc)

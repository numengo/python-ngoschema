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
import pathlib
import re
import dpath.util

import arrow
import python_jsonschema_objects.classbuilder as pjo_classbuilder
import python_jsonschema_objects.literals as pjo_literals
import python_jsonschema_objects.pattern_properties as pjo_pattern_properties
import python_jsonschema_objects.util as pjo_util
import python_jsonschema_objects.validators as pjo_validators
from future.utils import text_to_native_str as native_str

from .protocol_base import ProtocolBase, make_property
from . import jinja2
from . import pjo_validators as ngo_pjo_validators
from . import utils
from .resolver import get_resolver
from .foreign_key import ForeignKey
from .wrapper_types import ArrayWrapper
from .mixins import HasCache

logger = pjo_classbuilder.logger

_NEW_TYPES = ngo_pjo_validators.NGO_TYPE_MAPPING

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

    def _build_pseudo_literal(self, nm, clsdata, *parents):

        def __init_pseudo__(self, *args, **kwargs):
            HasCache.__init__(self)
            pjo_literals.LiteralValue.__init__(self, *args, **kwargs)

        def __getattr_pseudo__(self, name):
            """
            Special __getattr__ method to be able to use subclass methods
            directly on literal
            """
            if hasattr(self.__subclass__, name):
                if isinstance(self._value, self.__subclass__):
                    return getattr(self._value, name)
            elif hasattr(self.__class__, name):
                return object.__getattribute__(self, name)
            else:
                return pjo_literals.LiteralValue.__getattribute__(self, name)

        def __eq_pseudo__(self, other):
            if not pjo_literals.LiteralValue.__eq__(self, other):
                return False
            if not HasCache.__eq__(self, other):
                return False
            return True

        def validate_pseudo(self):
            instance = self._context() if self._context else None
            #if getattr(self, "_pattern", False):
            if '_pattern' in self.__dict__:
                self._value = jinja2.TemplatedString(self._pattern)(instance)
            pjo_literals.LiteralValue.validate(self)

        #cls_schema = copy.deepcopy(clsdata)
        cls_schema = clsdata
        propinfo = {
            '__literal__': cls_schema,
            '__default__': cls_schema.get('default')
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
                    '__propinfo__': propinfo,
                },
            )

        return type(
            native_str(nm),
            (pjo_literals.LiteralValue, HasCache),
            {
                '__init__': __init_pseudo__,
                '__propinfo__': propinfo,
                '__subclass__': parents[0],
                '__getattr__': __getattr_pseudo__,
                '__eq__': __eq_pseudo__,
                'validate': validate_pseudo,
            },
        )

    def _construct(self, uri, clsdata, parent=(ProtocolBase,), **kw):
        typ = clsdata.get('type')

        if typ not in (
            'string', 'path', 'date', 'time', 'datetime',
            'integer', 'number', 'boolean', 'null'
        ) and not set(clsdata.keys()).intersection(['foreignKey', 'enum']):
            return pjo_classbuilder.ClassBuilder._construct(
                    self, uri, clsdata, parent, **kw)

        if typ == 'integer':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, int)
        elif typ == 'number':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, float)
        elif typ == 'boolean':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, bool)
        elif typ == 'string' or 'enum' in clsdata:
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, str)
        elif typ == 'path':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, pathlib.Path)
        elif typ == 'datetime':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, arrow.Arrow)
        elif typ == 'date':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, datetime.date)
        elif typ == 'time':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, datetime.time)
        elif typ == 'null':
            self.resolved[uri] = self._build_pseudo_literal(
                uri, clsdata, None)
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
        defaults = dict()
        dependencies = dict()

        class_attrs = kw.get('class_attrs', {})

        # complete object attribute list with class attributes to use prop  attribute setter
        __object_attr_list__ = set(pjo_classbuilder.ProtocolBase.__object_attr_list__)

        #cls_schema = copy.deepcopy(clsdata)
        cls_schema = clsdata
        props['__schema__'] = cls_schema
        props['__schema__']['$id'] = nm

        # parent classes
        extends = [self.resolve_or_build(pjo_util.resolve_ref_uri(current_scope, ext))
                   for ext in cls_schema.get('extends', [])]
        extends = tuple(e for e in extends
                        if not any(issubclass(_, e) for _ in extends if e is not _)
                        and not any(issubclass(p, e) for p in parents))
        parents = extends + tuple(p for p in parents if not any(issubclass(e, p) for e in extends))

        # add parent attributes to class attribute list
        for p in reversed(parents):
            __object_attr_list__.update(getattr(p, '__object_attr_list__', []))
            __object_attr_list__.update([a for a in p.__dict__.keys() if not a.startswith('__')])
            defaults.update(getattr(p, '__has_default__', {}))


        properties = collections.OrderedDict(cls_schema.get('properties', {}))

        def find_getter_setter_defv(propname, class_attrs):
            """
            Helper to retrieve getters/setters/default value in class attribute
            dictionary for a given property name
            """
            getter = None
            setter = None
            defv = None
            pn = propname
            gpn = 'get_%s' % pn
            spn = 'set_%s' % pn
            if pn in class_attrs:
                a = class_attrs[pn]
                if inspect.isfunction(a) or inspect.ismethod(a):
                    logger.warning(
                        pjo_util.lazy_format("{} will be overwritten",
                                             propname))
                elif inspect.isdatadescriptor(a):
                    par_prop_sch = list(dpath.util.search(class_attrs, '__schema__/properties/'+propname, yielded=True))
                    prop_sch = list(dpath.util.search(cls_schema, 'properties/'+propname, yielded=True))
                    par_prop_sch = par_prop_sch[0] if par_prop_sch else {}
                    prop_sch = prop_sch[0] if prop_sch else {}
                else:
                    defv = class_attrs.pop(pn)
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
            if translated != prop:
                name_translated[translated] = prop
            ##name_translation[prop] = prop.replace("@", "").replace("$", "")
            name_translation[prop] = translated
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
                detail['default'] = defv

            if detail.get('default') is None and detail.get('enum') is not None:
                detail['default'] = detail['enum'][0]

            if detail.get('default') is None and detail.get('type') == 'array':
                detail['default'] = []

            if detail.get('default') is not None:
                defaults[prop] = detail.get('default')

            if detail.get('dependencies') is not None:
                dependencies[prop] = utils.to_list(detail['dependencies'].get('additionalProperties', []))

            if detail.get('type', None) == 'object':
                uri = '{0}/{1}_{2}'.format(nm, prop, '<anonymous>')
                self.resolved[uri] = self.construct(uri, detail,
                                                    (ProtocolBase,))

                props[prop] = make_property(
                    prop,
                    {'type': self.resolved[uri]},
                    fget=getter,
                    fset=setter,
                    desc=self.resolved[uri].__doc__,
                )
                properties[prop]['type'] = self.resolved[uri]

            elif 'type' not in detail and '$ref' in detail:
                ref = detail['$ref']
                # TODO CRN: shouldn't we retrieve also the reference and construct from it??
                uri = pjo_util.resolve_ref_uri(current_scope, ref)
                logger.debug(
                    pjo_util.lazy_format("Resolving reference {0} for {1}.{2}",
                                         ref, nm, prop))
                if uri in self.resolved:
                    typ = self.resolved[uri]
                else:
                    typ = self.construct(uri, detail, (ProtocolBase,))

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
                desc = detail['description'] if 'description' in detail else ''
                props[prop] = make_property(
                    prop, {'type': potential},
                    fget=getter,
                    fset=setter,
                    desc=desc)

            elif 'type' in detail and detail['type'] == 'array':
                # for resolution in create in wrapper_types
                detail['classbuilder'] = self
                if 'items' in detail and isinstance(detail['items'], dict):
                    if '$ref' in detail['items']:
                        uri = pjo_util.resolve_ref_uri(current_scope,
                                                       detail['items']['$ref'])
                        typ = self.construct(uri, detail['items'])
                        propdata = {
                            'type':
                            'array',
                            'validator':
                            ArrayWrapper.create(uri, item_constraint=typ),
                        }
                    else:
                        uri = '{0}/{1}_{2}'.format(nm, prop,
                                                   '<anonymous_field>')
                        try:
                            if 'oneOf' in detail['items']:
                                typ = pjo_classbuilder.TypeProxy([
                                    self.construct(uri + '_%s' % i,
                                                   item_detail)
                                    if '$ref' not in item_detail else
                                    self.construct(
                                        pjo_util.resolve_ref_uri(
                                            current_scope,
                                            item_detail['$ref'],
                                        ),
                                        item_detail,
                                    ) for i, item_detail in enumerate(detail[
                                        'items']['oneOf'])
                                ])
                            else:

                                typ = self._construct(uri, detail['items'])
                            propdata = {
                                'type':
                                'array',
                                'validator':
                                ArrayWrapper.create(uri, item_constraint=typ, **detail),
                            }
                        except NotImplementedError:
                            typ = copy.deepcopy(detail['items'])
                            propdata = {
                                'type':
                                'array',
                                'validator':
                                ArrayWrapper.create(uri, item_constraint=typ, **detail),
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
                        uri = '{0}/{1}/<anonymous_{2}>'.format(nm, prop, i)
                        typ = self.construct(uri, elem)
                        typs.append(typ)

                    props[prop] = make_property(
                        prop, {'type': typs}, fget=getter, fset=setter, desc=detail.get('description'))

            else:
                desc = detail['description'] if 'description' in detail else ''
                uri = '{0}/{1}'.format(nm, prop)
                typ = self.construct(uri, detail)

                props[prop] = make_property(
                    prop, {'type': typ}, fget=getter, fset=setter, desc=desc)
                properties[name_translated.get(prop, prop)]['_type'] = typ
        """
        If this object itself has a 'oneOf' designation, then
        make the validation 'type' the list of potential objects.
        """
        if 'oneOf' in cls_schema:
            klasses = self.resolve_classes(cls_schema['oneOf'])
            # Need a validation to check that it meets one of them
            props['__validation__'] = {'type': klasses}

        props['__extensible__'] = pjo_pattern_properties.ExtensibleValidator(
            nm, cls_schema, self)

        # add class attrs after removing defaults
        __object_attr_list__.update([a for a in class_attrs.keys() if not a.startswith('__')])
        props['__object_attr_list__'] = __object_attr_list__

        # we set class attributes as properties now, and they will be
        # overwritten if they are default values
        props.update([(k, v) for k, v in class_attrs.items() if k not in props])

        name_translation_flatten = name_translation.copy()
        for p in parents:
            name_translation_flatten.update(getattr(p, '__prop_names_flatten__',
                                             getattr(p, '__prop_names__', {})))

        props['__prop_names__'] = name_translation
        props['__prop_names_flatten__'] = name_translation_flatten
        props['__prop_translated_flatten__'] = {v: k for k, v in name_translation_flatten.items() if v!= k}
        props['__has_default__'] = defaults

        # automatically adds property names to foreign keys
        for prop_name, prop in properties.items():
            fkey = prop.get('foreignKey')
            if fkey and 'name' not in fkey:
                prop['foreignKey']['name'] = prop_name
            # case array of foreignkeys
            fkey =  prop.get('items', {}).get('foreignKey')                
            if fkey and 'name' not in fkey:
                prop['items']['foreignKey']['name'] = prop_name

        props['__propinfo__'] = properties

        # prepare set of inherited required, read_only, not_serialized attributes
        required = set.union(
            *[getattr(p, '__required__', set()) for p in parents])
        read_only = set.union(
            *[getattr(p, '__read_only__', set()) for p in parents])
        not_serialized = set.union(
            *[getattr(p, '__not_serialized__', set()) for p in parents])

        required.update(cls_schema.get('required', []))
        read_only.update(cls_schema.get('readOnly', []))
        not_serialized.update(cls_schema.get('notSerialized', []))

        invalid_requires = [
            req for req in required if req not in properties
        ]
        if len(invalid_requires) > 0:
            raise pjo_validators.ValidationError(
                "Schema Definition Error: {0} schema requires "
                "'{1}', but properties are not defined".format(
                    nm, invalid_requires))

        props['__required__'] = required
        props['__dependencies__'] = dependencies
        props['__read_only__'] = read_only
        props['__not_serialized__'] = not_serialized

        # default value on children force its resolution at each init
        # seems the best place to treat this special case
        props['__add_logging__'] = class_attrs.get('__add_logging__', False)
        props['__attr_by_name__'] = class_attrs.get('__attr_by_name__', False)
        props['__lazy_loading__'] = class_attrs.get('__lazy_loading__', False)
        props['__validate_lazy__'] = class_attrs.get('__validate_lazy__', False)
        props['__strict__'] = bool(required) or kw.get('strict', False) or class_attrs.get('__strict__', False)

        cls = type(clsname, tuple(parents), props)
        cls.__pbase_mro__ = tuple(c for c in cls.__mro__ if issubclass(c, pjo_classbuilder.ProtocolBase))
        cls.__ngo_pbase_mro__ = tuple(c for c in cls.__mro__ if issubclass(c, ProtocolBase))

        self.under_construction.remove(nm)

        # set default from config file
        cls.set_configfiles_defaults()

        dp = nm.split('definitions/')
        dp = [_.strip('/') for _ in dp]
        if len(dp)>1:
            dpath.util.new(self.definitions, dp[1:], cls)
            logger.info('CREATE %s', '.'.join(dp[1:]))
        else:
            logger.info('CREATE %s', clsname)
            self.definitions[clsname] = cls

        return cls


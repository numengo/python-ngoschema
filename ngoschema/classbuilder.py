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

import logging
import inflection
import copy
import inspect
import re

from collections import OrderedDict, ChainMap
import python_jsonschema_objects.classbuilder as pjo_classbuilder
import python_jsonschema_objects.pattern_properties as pjo_pattern_properties
import python_jsonschema_objects.util as pjo_util
import python_jsonschema_objects.validators as pjo_validators
from future.utils import text_to_native_str as native_str

from .protocol_base import ProtocolBase, make_property
from . import utils
from .resolver import get_resolver, qualify_ref, resolve_uri, domain_uri
from .wrapper_types import ArrayWrapper
from .decorators import memoized_method
from . import settings

logger = logging.getLogger(__name__)

# default builder global variable
_default_builder = None

LITERALS_TYPE = dict(settings.LITERALS_TYPE_CLASS_MAPPING)

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


def clean_def_name(name):
    return inflection.camelize(name.split(':')[-1])


def clean_prop_name(name):
    return re.sub(r"[^a-zA-z0-9\-_]+", "", name.split(':')[-1]).replace('-', '_')


def clean_ns_name(name):
    return inflection.underscore(name).replace('-', '_')


def get_default_ns_name(ns_uri):
    from . import settings
    # if main domain, make a default canonical name from path
    if ns_uri.startswith(settings.MS_DOMAIN):
        ns = ns_uri[len(settings.MS_DOMAIN):]
        ns = '.'.join([clean_ns_name(n) for n in ns.split('/')])
    # other domain: take last part of path
    else:
        ns = clean_ns_name(ns_uri.split('/')[-1])
    return ns


def clean_uri(uri):
    frag = None
    if '#' in uri:
        uri, frag = uri.split('#')
    uri = uri.lower().replace('_', '-')
    return uri if frag is None else uri + '#' + frag

count =0

class ClassBuilder(pjo_classbuilder.ClassBuilder):
    """
    A modified ClassBuilder to build a class with SchemaMetaclass, to create
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
        self._imported = {}
        self._usernamespace = {}
        self._django_ns = domain_uri('django')

    def set_namespace(self, ns, uri):
        self._usernamespace[ns] = uri

    @property
    def _namespaces(self):
        ns = set([k.split('#')[0] for k in self.resolved.keys()])
        return {get_default_ns_name(uri): uri for uri in ns}

    @property
    def namespaces(self):
        return ChainMap(self._usernamespace, self._namespaces, self.available_namespaces)

    def get_ref_cname(self, ref, **ns):
        ns_ = {k: uri for k, uri in ChainMap(ns, self._usernamespace, self._namespaces).items()}
        ns_names = sorted([k for k, uri in ns_.items() if ref.startswith(uri)],
                          key=lambda x: len(x[1]))
        if ns_names:
            ns_name = ns_names[0]
            ns = ns_[ns_name]
        else:
            ns = ref.split('#')[0]
            ns_name = get_default_ns_name(ns)
        cname = [ns_name]
        ref = ref.replace(ns, '').strip('#')
        clean_name = str
        for r in ref.split('/'):
            if not r or r == 'definitions':
                continue
            if r == 'properties':
                clean_name = clean_prop_name
                continue
            cname.append(clean_name(r))
        return '.'.join(cname)

    def get_cname_ref(self, cname, **ns):
        ns_ = {k: uri for k, uri in ChainMap(ns, self._usernamespace, self._namespaces).items()}
        for name, uri in ns_.items():
            if cname.startswith(name) and (cname == name or cname[len(name)] == '.'):
                ns_uri = ns_[name]
                cname = cname[len(name)+1:]
                break
        else:
            # retrieve local namespace if any
            ns_uri = ns_.get('')
            _ns = '.'.join(filter(lambda x: x[0].islower(), cname.split('.'))) or clean_ns_name(cname.split('.')[0])
            # or build a domain name from the first part of its canonical name
            ns_uri = ns_uri or domain_uri(get_default_ns_name(_ns))
            # set a default domain uri
            cname = cname.split('.', 1)[-1]
        if '#' not in ns_uri:
            ns_uri += '#'
        if not cname:
            return ns_uri
        cns = cname.split('.')
        tags = ['definitions'] * (len(cns)-1) + ['definitions' if cns[-1][0].isupper() else 'properties']
        return ns_uri + ''.join([f'/{t}/{c}' for t, c in zip(tags, cns)])

    @memoized_method()
    def namespace_name(self, uri):
        uri = uri.split('#')[0]
        for n, u in self.namespaces.items():
            if u == uri:
                return n

    def namespace_def_cnames(self, ns_name):
        ns = self.namespaces.get(ns_name)
        in_ns = [k for k in self.resolved.keys() if k.startswith(ns)]
        return [self.get_ref_cname(e, ns_name) for e in in_ns]

    @property
    def available_namespaces(self):
        from .schemas_loader import get_schema_store_list
        return {get_default_ns_name(k): k for k in get_schema_store_list()}

    def load_namespace(self, ns_name):
        ns = self.available_namespaces.get(ns_name)
        if not ns:
            raise ValueError('"%s" is not available in loaded documents %s.' % (ns_name, self.available_namespaces))
        return self.resolve_or_construct(ns)

    def load(self, cname):
        try:
            ns = cname.split('.')[0]
            uri = self.get_cname_ref(cname, **self.namespaces)
            return self.resolve_or_construct(uri)
        except Exception as er:
            raise ValueError('impossible to load "%s": %s' % (cname, er))

    def resolve_cname(self, cname):
        ns_name, defs = cname.split('.', 1)
        ns = self.namespaces.get(ns_name)
        if not ns:
            raise ValueError('"%s" namespace is not available %s.' % (ns, list(self.namespaces.keys())))
        uri = f'{ns}#/' + '/'.join(['definitions/' + d for d in defs.split('.')])
        cls = self.resolved.get(uri)
        if not cls:
            raise ValueError('"%s" could not be resolved in namespace definitions: %s.' % (cname, self.namespace_def_cnames(ns_name)))
        return cls

    def resolve_or_construct(self, uri, **kwargs):
        resolver = get_resolver()
        if uri not in self.resolved:
            if uri in self.under_construction:
                return pjo_classbuilder.TypeRef(uri, self.resolved)
            uri_no_fgt = uri.rsplit('#', 1)[0]
            if uri_no_fgt:
                resolver.push_scope(uri_no_fgt)
            uri, schema = resolver.resolve(uri)
            self.resolved[uri] = self.construct(uri, schema, **kwargs)
            if uri_no_fgt:
                resolver.pop_scope()
        return self.resolved[uri]

    def _build_literal(self, nm, clsdata, *parents):
        from .literals import LiteralValue
        from .models.foreign_key import ForeignKey, CnameForeignKey

        propinfo = {
            '__literal__': clsdata,
            '__default__': clsdata.get('default')
        }

        if 'foreignKey' in clsdata:
            # we merge the schema in propinfo to access it directly
            self.resolver.push_scope(nm.rsplit('#', 1)[0])
            uri, sch = self.resolver.resolve(clsdata['foreignKey']['$schema'])
            self.resolver.pop_scope()
            clsFK = CnameForeignKey if clsdata['foreignKey'].get('key', 'canonicalName') == 'canonicalName' \
                else ForeignKey
            clsdata['foreignKey']['$schema'] = uri
            propinfo.update(sch) # merge the schema in propinfo to access it directly
            propinfo.update(clsdata) # update with possibly overriding class
            return type(
                str(nm),
                tuple((clsFK, )),
                {
                    '__propinfo__': propinfo,
                    '__subclass__': str,
                },
            )

        return type(
            str(nm),
            tuple((LiteralValue,)),
            {
                '__propinfo__': propinfo,
                '__subclass__': parents[0],
            },
        )

    def _construct(self, uri, clsdata, parent=(ProtocolBase,), **kw):
        if 'nsPrefix' in clsdata:
            self.set_namespace(clsdata['nsPrefix'], uri)
        if '$ref' in clsdata:
            ref_uri = qualify_ref(clsdata['$ref'], uri)
            self.resolved[uri] = cls = self.resolve_or_construct(ref_uri)
            return cls
        if "enum" in clsdata:
            clsdata.setdefault("type", "string")
        typ = clsdata.get('type')
        if typ == 'array':
            typ = self.construct(f'{uri}/items', clsdata['items'])
            self.resolved[uri] = obj = ArrayWrapper.create(uri, item_constraint=typ, **kw)
            return obj
        if typ not in LITERALS_TYPE.keys() and 'foreignKey' not in clsdata:
            return pjo_classbuilder.ClassBuilder._construct(
                    self, uri, clsdata, parent, **kw)

        sub_cls = LITERALS_TYPE.get(typ)
        if 'foreignKey' in clsdata:
            self.resolved[uri] = self._build_literal(
                uri, clsdata, sub_cls)
        elif sub_cls:
            self.resolved[uri] = self._build_literal(
                uri, clsdata, sub_cls)

        return self.resolved[uri]

    def _build_object(self, nm, clsdata, parents, **kw):
        logger.debug(pjo_util.lazy_format("Building object {0}", nm))

        if '/' not in nm:
            ref = nm
            nm = self.get_cname_ref(ref)

        current_scope = nm.rsplit("#", 1)[0]
        ns_name = self.namespace_name(current_scope) or get_default_ns_name(current_scope)
        ns = {ns_name: current_scope}

        # To support circular references, we tag objects that we're
        # currently building as "under construction"
        self.under_construction.add(nm)

        parents_scope = set([current_scope])

        def scoped_uri(uri):
            return qualify_ref(uri, current_scope)

        def resolve_in_scope(ref):
            errors = []
            for p in parents_scope:
                try:
                    uri = qualify_ref(ref, p)
                    return uri, resolve_uri(uri)
                except Exception as er:
                    errors.append(er)
                    pass
            else:
                raise ReferenceError('impossible to resolve %s in %s' % (ref, parents_scope))

        # necessary to build type
        cls_name = inflection.camelize(native_str(nm.split("/")[-1]).replace('-', '_'))

        props = dict()
        defaults = dict()
        dependencies = dict()

        class_attrs = kw.get('class_attrs', {})

        # complete object attribute list with class attributes to use prop attribute setter
        object_attr_list = set()

        # first add all attributes from ProtocolBase and its parents
        for p in ProtocolBase.__mro__:
            object_attr_list.update(getattr(p, '__object_attr_list__', []))
            object_attr_list.update([a for a, v in p.__dict__.items()
                                     if not a.startswith('_') and not (utils.is_method(v) or utils.is_function(v))])

        cls_schema = clsdata
        props['__schema__'] = nm

        # parent classes (remove any django definition as it would trigger metaclass conflicts)
        extends = [scoped_uri(ext) for ext in cls_schema.get('extends', [])]

        def add_extend_recursively_to_scope(exts):
            for e in exts:
                uri, ext = resolve_in_scope(e)
                parents_scope.add(uri.rsplit("#", 1)[0])
                add_extend_recursively_to_scope(ext.get('extends', []))

        add_extend_recursively_to_scope(extends)

        e_parents = [self.resolve_or_construct(e) for e in extends]
        # remove typerefs and remove duplicates
        e_parents_sorted = tuple(e for e in e_parents
                        if not isinstance(e, pjo_classbuilder.TypeRef)
                        and not any(issubclass(_, e) for _ in e_parents if e is not _)
                        and not any(issubclass(p, e) for p in parents))
        parents = e_parents_sorted + tuple(p for p in parents if not any(issubclass(e, p) for e in e_parents_sorted))

        # add parent attributes to class attribute list
        for p in reversed(parents):
            if hasattr(p, '__schema__'):
                parents_scope.add(p.__schema__.rsplit("#", 1)[0])
            #object_attr_list.update(getattr(p, '__object_attr_list__', []))
            #object_attr_list.update([a for a, v in p.__dict__.items()
            #                             if not a.startswith('_') and not (utils.is_method(v) or utils.is_function(v))])
            defaults.update(getattr(p, '__has_default__', {}))

        propinfo = OrderedDict(cls_schema.get('properties', {}))

        # as any typeref has been removed from parent but add its properties to object_attr_list and name translation
        for e in e_parents:
            if isinstance(e, pjo_classbuilder.TypeRef):
                def add_prop_and_extends(uri):
                    _, sch = resolve_in_scope(uri)
                    sch_prop = sch.get('properties', {})
                    propinfo.update(sch_prop)
                    for ext in sch.get('extends', []):
                        add_prop_and_extends(ext)
                add_prop_and_extends(e._ref_uri)

        # name translation
        name_translation = OrderedDict()
        for prop, detail in propinfo.items():
            logger.debug(
                pjo_util.lazy_format("Handling property {0}.{1}", nm, prop))
            name_translation[prop] = clean_prop_name(prop)

        # flattening
        object_attr_list_flatten = ChainMap()
        name_translation_flatten = ChainMap()
        propinfo_flatten = ChainMap()

        for p in parents:
            object_attr_list_flatten = ChainMap(getattr(p, '__object_attr_list_flatten__',
                                                        getattr(p, '__object_attr_list__', {})),
                                                *object_attr_list_flatten.maps)
            name_translation_flatten = ChainMap(getattr(p, '__prop_names_flatten__',
                                                        getattr(p, '__prop_names__', {})),
                                                *name_translation_flatten.maps)
            propinfo_flatten = ChainMap(getattr(p, '__propinfo_flatten__',
                                                    getattr(p, '__propinfo__', {})),
                                                *propinfo_flatten.maps)

        object_attr_list_flatten = ChainMap(object_attr_list, *object_attr_list_flatten.maps)
        name_translation_flatten = ChainMap(name_translation, *name_translation_flatten.maps)
        propinfo_flatten = ChainMap(propinfo, *propinfo_flatten.maps)

        name_translated = {v: k for k, v in name_translation_flatten.items() if v != k}

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

        # looking for default values, getters and setters overriding inherited properties
        from_parents = set(name_translation_flatten.values()).difference(name_translation.values())
        for pn in from_parents:
            # get default value from class attributes or schema
            defv = class_attrs.get(pn) or cls_schema.get(pn)
            getter = class_attrs.get('get_' + pn)
            setter = class_attrs.get('set_' + pn)
            if defv:
                defaults[pn] = defv
            if defv or getter or setter:
                logger.warning("redefining property '%s' to use new default value, getter or setter from class code." % pn)
                for p in parents:
                    pi = p.propinfo(pn) if issubclass(p, ProtocolBase) else None
                    if pi:
                        getter = getattr(p, 'get_' + pn, None)
                        setter = getattr(p, 'set_' + pn, None)
                        defv = getattr(p, '__has_default__', {}).get(pn)
                        # add a copy of default value, setter, getter of parents into class if not already existing
                        for k, v in zip([pn, 'get_' + pn,  'set_' + pn],
                                        [defv, getter, setter]):
                            if v and k not in class_attrs:
                                class_attrs[k] = v
                        propinfo[name_translation_flatten[pn]] = pi.copy()
                        break
                else:
                    raise AttributeError("Impossible to find inherited property '%s' in schema" % pn)

        for prop, detail in propinfo.items():
            prop_uri = f'{nm}/properties/{prop}'
            prop = name_translation_flatten[prop]

            # look for getter/setter/defaultvalue first in class definition
            defv = class_attrs.get(prop)
            if defv is not None and (
                inspect.isfunction(defv) or inspect.ismethod(defv) or inspect.isdatadescriptor(defv)):
                raise AttributeError(
                    "Impossible to get an initial value from attribute '%s' as defined in class code." % prop)
            getter = class_attrs.get('get_' + prop)
            if getter and not (inspect.isfunction(getter) or inspect.ismethod(getter)):
                raise AttributeError(
                    "Impossible to use getter of attribute '%s' as defined in class code." % prop)
            setter = class_attrs.get('set_' + prop)
            if setter and not (inspect.isfunction(setter) or inspect.ismethod(setter)):
                raise AttributeError(
                    "Impossible to use setter of attribute '%s' as defined in class code." % prop)

            if defv is not None:
                detail['default'] = defv

            if detail.get('default') is None and detail.get('enum') is not None:
                detail['default'] = detail['enum'][0]

            if prop in required and 'default' not in detail and detail.get('type') == 'object':
                    detail['default'] = {}

            if detail.get('default') is None and detail.get('type') == 'array':
                detail['default'] = []

            if detail.get('default') is not None:
                defaults[prop] = detail.get('default')

            if detail.get('dependencies') is not None:
                dependencies[prop] = utils.to_list(detail['dependencies'].get('additionalProperties', []))

            if detail.get('type') == 'object':
                typ = self.resolved[prop_uri] = self.construct(prop_uri, detail,
                                                    (ProtocolBase,))

                props[prop] = make_property(
                    prop,
                    {'type': typ},
                    fget=getter,
                    fset=setter,
                    desc=typ.__doc__,
                )
                propinfo[name_translated.get(prop, prop)]['_type'] = typ

            elif 'type' not in detail and '$ref' in detail:
                ref, _ = resolve_in_scope(detail['$ref'])
                logger.debug(
                    pjo_util.lazy_format("Resolving reference {0} for {1}.{2}", ref, nm, prop))
                #uri, sch_ref = resolve_in_scope(ref)
                #if uri in self.resolved:
                #    typ = self.resolved[uri]
                #else:
                #    global count
                #    count = count + 1
                #    typ = self.construct(uri, sch_ref, (ProtocolBase,))

                typ = self.resolve_or_construct(ref)

                props[prop] = make_property(
                    prop, {'type': typ},
                    fget=getter,
                    fset=setter,
                    desc=typ.__doc__)

                if hasattr(typ, 'isLiteralClass') and typ.default() is not None:
                    defaults[prop] = typ.default()
                elif issubclass(typ, ArrayWrapper):
                    defaults[prop] = []

                #alias = name_translated.get(prop, prop) if prop not in propinfo else prop
                #propinfo[alias] = {'$ref': uri
                #propinfo[alias]['_type'] = typ
                if prop in required and 'default' not in detail:
                    if issubclass(typ, pjo_classbuilder.ProtocolBase):
                        defaults[prop] = {}

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

            elif detail.get('type') == 'array':
                # for resolution in create in wrapper_types
                detail['classbuilder'] = self
                defaults.setdefault(prop, [])

                if 'items' in detail and utils.is_mapping(detail['items']):
                    if '$ref' in detail['items']:
                        constraints = copy.copy(detail)
                        constraints["strict"] = kw.get("_strict")
                        uri, _ = resolve_in_scope(detail['items']['$ref'])
                        typ = self.construct(uri, detail['items'])
                        detail['items']['_type'] = typ
                        propdata = {
                            'type': 'array',
                            'validator': ArrayWrapper.create(prop_uri, item_constraint=typ, **constraints),
                        }
                    else:
                        try:
                            if 'oneOf' in detail['items']:
                                typ = pjo_classbuilder.TypeProxy([
                                    self.construct(uri + '_%s' % i,
                                                   item_detail)
                                    if '$ref' not in item_detail else
                                    self.construct(
                                        resolve_in_scope(item_detail['$ref'])[0],
                                        item_detail,
                                    ) for i, item_detail in enumerate(detail[
                                        'items']['oneOf'])
                                ])
                            else:
                                typ = self._construct(prop_uri+'/items', detail['items'])
                            constraints = copy.copy(detail)
                            constraints["strict"] = kw.get("_strict")
                            propdata = {
                                'type': 'array',
                                'validator': ArrayWrapper.create(prop_uri, item_constraint=typ, **constraints),
                            }
                        except NotImplementedError:
                            typ = detail["items"]
                            constraints = copy.copy(detail)
                            constraints["strict"] = kw.get("_strict")
                            propdata = {
                                'type': 'array',
                                'validator': ArrayWrapper.create(prop_uri, item_constraint=typ, **constraints),
                            }

                    props[prop] = make_property(
                        prop,
                        propdata,
                        fget=getter,
                        fset=setter,
                        desc=typ.__doc__)
                elif 'items' in detail:
                    #typs = []
                    for i, elem in enumerate(detail['items']):
                        uri = '{0}/{1}>'.format(prop_uri, i)
                        typ = self.construct(uri, elem)
                        #typs.append(typ)

                    props[prop] = make_property(
                        prop, {'type': 'array', '_type': typ}, fget=getter, fset=setter, desc=detail.get('description'))

            else:
                desc = detail['description'] if 'description' in detail else ''
                typ = self.construct(prop_uri, detail)

                props[prop] = make_property(
                    prop, {'type': typ}, fget=getter, fset=setter, desc=desc)
                propinfo[name_translated.get(prop, prop)]['_type'] = typ

                if hasattr(typ, 'isLiteralClass') and typ.default() is not None:
                    defaults[prop] = typ.default()


        # build inner definitions
        inner_defs = {}
        for def_name, detail in clsdata.get('definitions', {}).items():
            def_uri = f'{nm}/definitions/{def_name}'
            inner_defs[def_name] = self.resolved[def_uri] = self._build_object(def_uri, detail, (ProtocolBase,), **kw)

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
        object_attr_list.update([a for a, v in class_attrs.items()
                                 if not a.startswith('_')]) # and not (utils.is_method(v) or utils.is_function(v))])
        props['__object_attr_list__'] = object_attr_list
        props['__object_attr_list_flatten__'] = object_attr_list_flatten

        # we set class attributes as properties now, and they will be
        # overwritten if they are default values
        props.update([(k, v) for k, v in class_attrs.items() if k not in props])

        props['__prop_names__'] = name_translation
        props['__prop_names_flatten__'] = name_translation_flatten
        props['__prop_translated_flatten__'] = name_translated

        props['__has_default__'] = defaults

        props['__propinfo__'] = propinfo
        props['__propinfo_flatten__'] = propinfo_flatten

        invalid_requires = [req for req in required if req not in name_translation_flatten]
        if len(invalid_requires) > 0:
            raise pjo_validators.ValidationError(
                "Schema Definition Error: {0} schema requires "
                "'{1}', but properties are not defined".format(
                    nm, invalid_requires))

        props['__required__'] = required
        props['__dependencies__'] = dependencies
        props['__read_only__'] = read_only
        props['__not_serialized__'] = not_serialized
        props['__extends__'] = extends

        # default value on children force its resolution at each init
        # seems the best place to treat this special case
        props['__schema__'] = kw.get('$schema') or class_attrs.get('__schema__', nm)
        props['__add_logging__'] = kw.get('_addLogging') or class_attrs.get('__add_logging__', False)
        props['__attr_by_name__'] = kw.get('_attrByName') or class_attrs.get('__attr_by_name__', False)
        props['__validate_lazy__'] = kw.get('_validateLazy') or class_attrs.get('__validate_lazy__', False)
        props['__propagate__'] = kw.get('_propagate') or class_attrs.get('__propagate__', False)
        props['__lazy_loading__'] = kw.get('_lazyLoading') or class_attrs.get('__lazy_loading__', False)
        props['__strict__'] = bool(required) or kw.get('_strict') or class_attrs.get('__strict__', False)
        props['__log_level__'] = kw.get('_logLevel') or class_attrs.get('__log_level__', 'INFO')

        cls = type(cls_name, tuple(parents), props)
        cls.__doc__ = clsdata.get('description')
        cls.__pbase_mro__ = tuple(c for c in cls.__mro__ if issubclass(c, pjo_classbuilder.ProtocolBase))
        cls.__ngo_pbase_mro__ = tuple(c for c in cls.__pbase_mro__ if issubclass(c, ProtocolBase))
        # adds inner classes as members
        for k, v in inner_defs.items():
            setattr(cls, k, v)

        if nm not in self.resolved:
            self.under_construction.remove(nm)

        # set default from config file
        cls.set_configfiles_defaults()

        logger.info('CREATED %s', self.get_ref_cname(nm))

        return cls


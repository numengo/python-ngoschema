# *- coding: utf-8 -*-
"""
Utilities and classes to deal with schemas

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import inspect
import gettext
import json
import logging
import weakref
from builtins import object
from builtins import str

import jsonschema
from future.builtins import object
from future.utils import with_metaclass
from jsonschema.compat import iteritems
from pyrsistent import pmap

from . import validators
from . import utils
from . import str_utils
from .schemas_loader import load_module_schemas
from .schemas_loader import load_schema_file
from .resolver import get_resolver
from .validators import DefaultValidator
from .inspect_objects import FunctionInspector
from ._classbuilder import ProtocolBase, ClassBuilder, make_property
from . import decorators

_ = gettext.gettext

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())

# necessary to load schemas before any resolution can be done
load_module_schemas()


class SchemaMetaclass(type):
    """
    Metaclass used for classes with schema
    """

    def __new__(cls, clsname, bases, attrs):
        """
        Process schema given by schemaPath if found and merges the schemas of bases

        When processing the schema dictionary, any harcoded initial value for
        schema is used.
        If a dictionary is found it will initialize the object define in schema
        """

        # base schema, should be overwritten
        schema = {}
        # default resolver and builder
        resolver = get_resolver()
        builder = ClassBuilder(resolver)
        if attrs.get('schema'):
            schemaUri, schema = load_schema(attrs['schema'])
            schema = resolver.expand(schemaUri, schema)
        elif attrs.get('schemaPath'):
            schemaUri, schema = load_schema_file(attrs['schemaPath'])
            schema = resolver.expand(schemaUri, schema)
        elif attrs.get('schemaUri'):
            schemaUri, schema = resolver.resolve(attrs['schemaUri'])
        if schema:
            # validate schema with its meta-schema
            metaschema = DefaultValidator.META_SCHEMA
            if schema.get('$schema'):
                ms_uri, metaschema = resolver.resolve(schema['$schema'])
            meta_validator = DefaultValidator(metaschema,resolver=resolver)
            # with hacked validator, can set a mode to set default values during
            # validation => schema will have its default values set
            def_bak = getattr(DefaultValidator, '_setDefaults', False)
            DefaultValidator._setDefaults = True
            meta_validator.validate(schema)
            DefaultValidator._setDefaults = def_bak

            logger.debug(_('creating <%s> with schema' % (clsname)))

            # reset resolver and builder to use the schemaUri as base
            resolver = get_resolver(schemaUri)
            builder = ClassBuilder(resolver)
            # building inner definitions
            for nm, defn in iteritems(schema.get('definitions', {})):
                uri = pjo_util.resolve_ref_uri(
                    schemaUri,"#/definitions/" + nm)
                builder.construct(uri, defn, attrs.get('nm',{}))
        else:
            schema['type'] = 'object'

        # add weak value dict to know all managers
        attrs['_managers'] = weakref.WeakValueDictionary()
        # add some magic on methods defined in class
        # exception handling, argument conversion/validation, etc...
        for k, fn in attrs.items():
            if not inspect.isfunction(fn) and not inspect.ismethod(fn):
                continue

            if k == '__init__':
                logger.debug(
                        _('decorate <%s>.__init__ with init logger' %
                         (clsname)))
                fn = decorators.log_init(fn)

            # add argument checking
            fi = FunctionInspector(fn)
            for pos, p in enumerate(fi.parameters):
                if p.type:
                    logger.debug(_('decorate <%s>.%s ' % (clsname, k) +
                                   'with argument %i validity check.' % pos))
                    fn = decorators.assert_arg(pos, p.type)(fn)

            # add exception logging
            if not k.startswith('__'):
                logger.debug(_('decorate <%s>.%s with exception logger'
                               % (clsname, k)))
                fn = decorators.log_exceptions(fn)

            attrs[k] = fn

        return builder.construct(clsname, schema, parent=bases, class_attrs=dict(attrs))


class SchemaBase(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/Class"

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, **kwargs)
        # add managers and so on


class ObjectManager(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/ObjectManager"
    _instances = {}

    def __new__(cls, *args, **kwargs):
        clsname = cls.__name__
        if clsname == 'ObjectManager':
            raise TypeError('ObjectManager must not be instantiated directly')
        if clsname not in cls._instances:
            cls._instances[clsname] = super(ObjectManager, cls).__new__(
                cls, *args, **kwargs)
            #cls._instances[clsname].__object_attr_list__.update(['_managed', '_serializers', '_parsers', '_objectClass'])
            cls._instances[clsname]._managed = dict()
        return cls._instances[clsname]

    def _obj_or_str(val):
        if str_utils.is_string(val):
            return val, utils.import_from_string(e)
        elif utils.is_class(e):
            return utils.fullname(e), e
        else:
            raise InvalidValue(_('%r is not an object class' % value))

    def _obj_or_str_arr(array):
        s_a = o_a = []
        for e in array:
            s, o = _object_or_string(e)
            s_a.append(s)
            o_a.append(o)
        return s_a, o_a

    def set_objectClass(self, value):
        self._properties['objectClass'], self._objectClass = _obj_or_str(value)

    def set_serializers(self, value):
        self._properties['serializers'], self._serializers = _obj_or_str_arr(value)

    def set_parsers(self, value):
        self._properties['parsers'], self._parsers = _obj_or_str_arr(value)






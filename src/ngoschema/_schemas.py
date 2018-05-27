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
from builtins import object
from builtins import str

import jsonschema
from future.builtins import object
from future.utils import with_metaclass
from jsonschema.compat import iteritems
from pyrsistent import pmap

from . import validators
from .schemas_loader import load_module_schemas
from .schemas_loader import load_schema_file
from .resolver import get_resolver
from .validators import DefaultValidator
from ._classbuilder import ProtocolBase, ClassBuilder, make_property
from . import _decorators as decorators

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
        schema = {}
        resolver = get_resolver()
        if attrs.get('schema'):
            schemaUri, schema = load_schema(attrs['schema'])
            schema = resolver.expand(schemaUri, schema)
        elif attrs.get('schemaPath'):
            schemaUri, schema = load_schema_file(attrs['schemaPath'])
            schema = resolver.expand(schemaUri, schema)
        elif attrs.get('schemaUri'):
            schemaUri, schema = resolver.resolve(attrs['schemaUri'])
        if not schema:
            raise Exception('no schema found')

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

        logger.debug(_('SCHEMA %s creating class with schema' % (clsname)))

        for k, fn in attrs.items():
            if not inspect.isfunction(fn) and not inspect.ismethod(fn):
                continue
            if k == '__init__':
                logger.debug(
                        _('SCHEMA %s decorate __init__ with init logger' %
                         (clsname)))
                attrs[k] = decorators.log_init(fn)
            if k[0] == '_':
                continue

        resolver = get_resolver(schemaUri)
        builder = ClassBuilder(resolver)
        for nm, defn in iteritems(schema.get('definitions', {})):
            uri = pjo_util.resolve_ref_uri(
                schemaUri,"#/definitions/" + nm)
            builder.construct(uri, defn,attrs.get('nm',{}))

        return builder.construct(clsname, schema, parent=bases, class_attrs=dict(attrs))


class SchemaBase(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaUri = "http://numengo.org/draft-04/defs-schema#/definitions/Class"

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, **kwargs)
        # add managers and so on


# *- coding: utf-8 -*-
"""
Utilities and classes to deal with schemas

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

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

_ = gettext.gettext

logging.basicConfig(level=logging.WARNING)

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
        logger = logging.getLogger(clsname)
        logger.setLevel(logging.DEBUG)

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

        metaschema = DefaultValidator.META_SCHEMA
        if schema.get('$schema'):
            ms_uri, metaschema = resolver.resolve(schema['$schema'])
        meta_validator = DefaultValidator(metaschema,resolver=resolver)
        DefaultValidator._setDefaults = True
        meta_validator.validate(schema)
        DefaultValidator._setDefaults = False

        logger.debug(_('SCHEMA %s creating class with schema' % (clsname)))
        logger.setLevel(logging.DEBUG)
        attrs['logger'] = logger

        builder = ClassBuilder(resolver)
        for nm, defn in iteritems(schema.get('definitions', {})):
            uri = pjo_util.resolve_ref_uri(
                schemaUri,"#/definitions/" + nm)
            builder.construct(uri, defn,attrs.get('nm',{}))

        return builder.construct(clsname, schema, parent=bases, class_attrs=dict(attrs))


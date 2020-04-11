# *- coding: utf-8 -*-
"""
Utilities and classes to deal with schemas

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from jsonschema.compat import iteritems

from . import decorators
from . import utils
from .classbuilder import get_builder
from .literals import LiteralValue
from ngoschema.inspect.inspect_objects import FunctionInspector
from .resolver import get_resolver
from .validators.jsonschema import DefaultValidator

logger = logging.getLogger(__name__)


class SchemaMetaclass(type):
    """
    Metaclass used for classes with schema.

    It processes the following class attributes:
    __schema_uri__ : id of schema to look up on loaded module schemas or online
    __assert_args__: automatically convert/validate methods arguments based on their documented typed
    __add_logging__: adds logging around each method call
    __attr_by_name__: allows to look for attributes by their name
    __lazy_loading__: boolean to activate lazy loading
    __propagate__: boolean to propage settings to children objects
    __strict__: stricly validate
    __log_level__: default class logger log level
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
        schema_uri = None
        builder = get_builder(get_resolver())
        resolver = builder.resolver
        if attrs.get("__schema_uri__"):
            schema_uri, schema = resolver.resolve(attrs["__schema_uri__"])
            if '#' not in schema_uri:
                schema_uri += '#'
        if schema:
            # validate schema with its meta-schema
            metaschema = DefaultValidator.META_SCHEMA
            if schema.get("metaclass", "SchemaMetaclass") != "SchemaMetaclass":
                raise ValueError("class should be built with metaclass '%s'." % schema.get('metaclass'))
            if schema.get("$schema"):
                ms_uri, metaschema = resolver.resolve(schema["$schema"])
            meta_validator = DefaultValidator(metaschema, resolver=resolver)
            # with hacked validator, can set a mode to set default values during
            # validation => schema will have its default values set
            def_bak = getattr(DefaultValidator, "_setDefaults", False)
            DefaultValidator._setDefaults = True
            meta_validator.validate(schema)
            DefaultValidator._setDefaults = def_bak

            logger.debug("creating <%s> with schema", clsname)

            # reset resolver and builder to use the schema_uri as base
            resolver = get_resolver(schema_uri)
            builder = get_builder(resolver)
            # building inner definitions
            for nm, defn in iteritems(schema.get("definitions", {})):
                uri = schema_uri + "/definitions/" + nm
                from ngoschema import ProtocolBase
                builder.construct(uri, defn)
        else:
            schema["type"] = "object"

        # add some magic on methods defined in class
        # exception handling, argument conversion/validation, dependencies, etc...
        for k, fn in attrs.items():
            # add declared fields to schema
            if utils.is_class(fn) and issubclass(fn, LiteralValue):
                schema.setdefault(k, fn.__propinfo__['__literal__'])
            if not (utils.is_method(fn) or utils.is_function(fn)):
                continue
            add_logging = attrs.get("__add_logging__", False)
            assert_args = attrs.get("__assert_args__", True)

            if add_logging and k == "__init__":
                logger.debug("decorate <%s>.__init__ with init logger",
                             clsname)
                fn = decorators.log_init(fn)

            # add argument checking
            if assert_args and fn.__doc__:
                fi = FunctionInspector(fn)
                for pos, p in enumerate(fi.parameters):
                    if p.schema:
                        logger.debug(
                            "decorate <%s>.%s with argument %i validity check.",
                            clsname, k, pos)
                        fn = decorators.assert_arg(pos, p.schema)(fn)

            # add exception logging
            if add_logging and not k.startswith("__"):
                logger.debug("decorate <%s>.%s with exception logger", clsname,
                             k)
                fn = decorators.log_exceptions(fn)

            attrs[k] = fn

        uri = schema_uri or clsname
        # remove existing definition
        if uri in builder.resolved:
            cls = builder.resolved.pop(uri)
        cls = builder.construct(
            uri, schema, parent=bases, class_name=clsname, class_attrs=dict(attrs))

        return cls

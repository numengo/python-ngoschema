# *- coding: utf-8 -*-
"""
Schema validators to extend jsonschema library

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 20/05/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import collections
from builtins import str
from datetime import datetime, date, time
from pathlib import Path
import urllib.parse

import six
from arrow import Arrow
import pkgutil
import json
from jsonschema import TypeChecker, Draft6Validator

from jsonschema._format import draft7_format_checker
from jsonschema._types import is_array, is_bool, is_integer, is_object, is_null, is_number, is_string
from jsonschema.compat import iteritems
from jsonschema.exceptions import FormatError
from jsonschema.exceptions import RefResolutionError
from jsonschema.exceptions import ValidationError
from jsonschema.validators import extend
from python_jsonschema_objects import ValidationError
from python_jsonschema_objects.validators import registry

from .. import utils


def _load_schema(name):
    """
    Load a schema from ./schemas/``name``.json and return it.

    """
    data = pkgutil.get_data("ngoschema", "schemas/{0}.json".format(name))
    return json.loads(data.decode("utf-8"), object_pairs_hook=collections.OrderedDict)


def _format_checker(validator):
    return validator.format_checker or draft7_format_checker


def extends_ngo_draft1(validator, extends, instance, schema):
    if validator.is_type(extends, "array"):
        for ref in extends:
            try:
                _format_checker(validator).check(ref, "uri-reference")
                scope, resolved = validator.resolver.resolve(ref)
            except FormatError as er:
                yield ValidationError(str(er), cause=er.cause)
            except RefResolutionError as er:
                yield ValidationError(str(er))


def properties_ngo_draft1(validator, properties, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    if "schema" in instance:
        scope, schema = validator.resolver.resolve(instance["schema"])
        validator.resolver.push_scope(scope)
        properties = schema.get("properties")

    for property, subschema in iteritems(properties):
        if getattr(validator, "_setDefaults", False):
            if "default" in subschema and not isinstance(instance, list):
                instance.setdefault(property, subschema["default"])

        if property in instance:
            for error in validator.descend(
                    instance[property],
                    subschema,
                    path=property,
                    schema_path=property):
                yield error

    if "schema" in instance:
        validator.resolver.pop_scope()


def properties_ngo_draft2(validator, properties, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    if "__schema_uri__" in instance:
        scope, schema = validator.resolver.resolve(instance["__schema_uri__"])
        validator.resolver.push_scope(scope)
        properties = schema.get("properties")

    for property, subschema in iteritems(properties):
        if getattr(validator, "_setDefaults", False):
            if property not in (
                    'definitions', 'properties', 'additionalProperties',
                    'patternProperties', 'uniqueItems', 'readOnly',
                    'abstract', 'items'
            ) and isinstance(
                    subschema,
                    dict) and "default" in subschema and not isinstance(
                        instance, list):
                instance.setdefault(property, subschema["default"])

        if property in instance:
            for error in validator.descend(
                    instance[property],
                    subschema,
                    path=property,
                    schema_path=property):
                yield error

    if "__schema_uri__" in instance:
        validator.resolver.pop_scope()


def ref_ngo_draft1(validator, ref, instance, schema):
    # override reference with schema defined in instance
    if isinstance(instance, collections.Iterable) and "schema" in instance:
        ref = instance["schema"]

    resolve = getattr(validator.resolver, "resolve", None)
    if resolve is None:
        with validator.resolver.resolving(ref) as resolved:
            for error in validator.descend(instance, resolved):
                yield error
    else:
        scope, resolved = validator.resolver.resolve(ref)
        validator.resolver.push_scope(scope)

        try:
            for error in validator.descend(instance, resolved):
                yield error
        finally:
            validator.resolver.pop_scope()


def ref_ngo_draft2(validator, ref, instance, schema):
    # override reference with schema defined in instance
    if isinstance(instance, collections.Iterable) and "__schema_uri__" in instance:
        ref = instance["__schema_uri__"]

    resolve = getattr(validator.resolver, "resolve", None)
    if resolve is None:
        with validator.resolver.resolving(ref) as resolved:
            for error in validator.descend(instance, resolved):
                yield error
    else:
        try:
            scope, resolved = validator.resolver.resolve(ref)
            validator.resolver.push_scope(scope)
        except RefResolutionError as error:
            yield ValidationError("%s. Resolution scope=%s" %
                                  (error, validator.resolver.resolution_scope))
            return

        try:
            for error in validator.descend(instance, resolved):
                yield error
        finally:
            # pass
            validator.resolver.pop_scope()


ngodraft04_type_checker = TypeChecker(
    {
        u"array": is_array,
        u"boolean": is_bool,
        u"integer": lambda checker, instance: (
            is_integer(checker, instance) or
            isinstance(instance, float) and instance.is_integer()
        ),
        u"object": is_object,
        u"null": is_null,
        u"number": is_number,
        u"string": is_string,
        u"importable": lambda checker, instance: utils.is_importable(instance),
        u"uri": lambda checker, instance: (
            is_string(checker, instance) or
            isinstance(instance, urllib.parse.SplitResult)
        ),
        u"path": lambda checker, instance: (
            is_string(checker, instance) or
            isinstance(instance, Path)
        ),
        u"date": lambda checker, instance: (
            is_string(checker, instance) or
            isinstance(instance, Arrow) or
            isinstance(instance, datetime) or
            isinstance(instance, date)
        ),
        u"time": lambda checker, instance: (
            is_string(checker, instance) or
            isinstance(instance, Arrow) or
            isinstance(instance, datetime) or
            isinstance(instance, time)
        ),
        u"datetime": lambda checker, instance: (
            is_string(checker, instance) or
            isinstance(instance, Arrow) or
            isinstance(instance, datetime)
        )
    },
)

NgoDraft05Validator = extend(
    Draft6Validator,
    validators={
        "$ref": ref_ngo_draft2,
        "extends": extends_ngo_draft1,
        "properties": properties_ngo_draft2,
    },
    type_checker=ngodraft04_type_checker)
NgoDraft05Validator._setDefaults = False
NgoDraft05Validator.META_SCHEMA = _load_schema("ngo-draft-05")
DefaultValidator = NgoDraft05Validator


def convert_validate(value, schema):
    from .pjo import converter_registry
    ret = value
    type_ = "enum" if "enum" in schema else schema.get("type", "object")

    converter = converter_registry(type_)
    if converter is not None:
        ret = converter(value, schema)

    if type_ == "array":
        assert isinstance(ret, (list, tuple))
        # validate items
        sch_items = schema.get("items", {})
        if sch_items:
            for i, e in enumerate(ret):
                ret[i] = convert_validate(e, sch_items)
        # validate length
        if "minItems" in schema and len(ret) < schema["minItems"]:
            raise ValidationError(
                "{1} has too few elements. Wanted {0}.".format(
                    schema["minItems"], value))
        if "maxItems" in schema and len(ret) > schema["maxItems"]:
            raise ValidationError(
                "{1} has too many elements. Wanted {0}.".format(
                    schema["maxItems"], value))
        # validate uniqueness
        if "uniqueItems" in schema and len(set(ret)) != len(ret):
            raise ValidationError(
                "{0} has duplicate elements, but uniqueness required".format(
                    value))

    for param, paramval in sorted(
            six.iteritems(schema), key=lambda x: x[0].lower() != "type"):
        validator = registry(param)
        if validator is not None:
            validator(paramval, ret, schema)

    return ret

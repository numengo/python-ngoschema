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
import gettext
from builtins import str

from jsonschema._format import draft7_format_checker
from jsonschema.compat import iteritems
from jsonschema.exceptions import FormatError
from jsonschema.exceptions import RefResolutionError
from jsonschema.exceptions import ValidationError

_ = gettext.gettext


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
                yield ValidationError(str(er), cause=er.cause)


def properties_ngo_draft1(validator, properties, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    if "schema" in instance:
        scope, schema = validator.resolver.resolve(instance["schema"])
        validator.resolver.push_scope(scope)
        properties = schema.get("properties")

    for property, subschema in iteritems(properties):
        if getattr(validator, "_setDefault", False):
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

    if "schemaUri" in instance:
        scope, schema = validator.resolver.resolve(instance["schemaUri"])
        validator.resolver.push_scope(scope)
        properties = schema.get("properties")

    for property, subschema in iteritems(properties):
        if getattr(validator, "_setDefault", False):
            if "default" in subschema and not isinstance(instance, list):
                instance.setdefault(property, subschema["default"])

        if property in instance:
            for error in validator.descend(
                    instance[property],
                    subschema,
                    path=property,
                    schema_path=property):
                yield error

    if "schemaUri" in instance:
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
    if isinstance(instance, collections.Iterable) and "schemaUri" in instance:
        ref = instance["schemaUri"]

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

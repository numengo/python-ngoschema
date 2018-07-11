# *- coding: utf-8 -*-
"""
json-schema validator classes

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from datetime import date
from datetime import datetime
from datetime import time
from pathlib import Path

import six
from arrow import Arrow
from jsonschema._types import TypeChecker
from jsonschema._types import is_array
from jsonschema._types import is_bool
from jsonschema._types import is_integer
from jsonschema._types import is_null
from jsonschema._types import is_number
from jsonschema._types import is_object
from jsonschema._types import is_string
from jsonschema.validators import Draft6Validator
from jsonschema.validators import extend
from python_jsonschema_objects.validators import ValidationError
from python_jsonschema_objects.validators import converter_registry
from python_jsonschema_objects.validators import registry

from . import js_validators as _validators
from .schemas_loader import _load_schema

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

NgoDraft04Validator = extend(
    Draft6Validator,
    validators={
        "$ref": _validators.ref_ngo_draft2,
        "extends": _validators.extends_ngo_draft1,
        "properties": _validators.properties_ngo_draft2,
    },
    type_checker=ngodraft04_type_checker)
NgoDraft04Validator._setDefaults = False
NgoDraft04Validator.META_SCHEMA = _load_schema("ngo-draft-04")

DefaultValidator = NgoDraft04Validator


def convert_validate(value, schema):
    ret = value
    type_ = "enum" if "enum" in schema else schema.get("type", "object")

    converter = converter_registry(type_)
    if converter is not None:
        ret = converter(None, value, schema)

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

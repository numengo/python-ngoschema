# -*- coding: utf-8 -*-
"""
Unit tests for schema validation

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
created on 2018/05/06
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import logging
import os
import pathlib

import pytest
import six
from jsonschema import Draft6Validator
from jsonschema import RefResolver
from python_jsonschema_objects.validators import ValidationError

from ngoschema import decorators
from ngoschema import validators
from ngoschema.resolver import ExpandingResolver
from ngoschema.schemas_loader import get_all_schemas_store
from ngoschema.schemas_loader import load_schema_file
from ngoschema.validators import DefaultValidator

logging.basicConfig(level=logging.INFO)

test_dir = os.path.dirname(os.path.realpath(__file__))
defs_fp = os.path.join(test_dir, "schemas", "ngo-defs-draft-XX.json")
DEFS_URI, DEFS = load_schema_file(defs_fp)
MS_STORE = get_all_schemas_store()

resolver = ExpandingResolver(DEFS_URI, DEFS, MS_STORE)
orig_resolver = RefResolver(DEFS_URI, DEFS, MS_STORE)


def test_validate_extends():
    id, sch = resolver.resolve_by_name("FunctionArgument")
    # FunctionArgument extends 'metadata' which contains property 'title'
    id, sch2 = orig_resolver.resolve(id)

    instance = {
        "title": "RAISE ERROR: METADATA COMING FROM EXTENSION",
        "isArray": False,
        "refVariable": "#/variableGroups/1/Variables/variables/10/u1",
        "isDerivative": False,
        "cppName": "u1",
    }

    v = Draft6Validator(sch2)
    # title is a property from a class refered in "extended"
    with pytest.raises(Exception) as e_info:
        v.validate(instance)
        assert (
            e_info.message ==
            "Additional properties are not allowed (u'title' was unexpected)")

    v = Draft6Validator(sch)
    v.validate(instance)


def test_validate_subschemas():
    id, sch = resolver.resolve_by_name("ComponentDefinition")
    v_orig = Draft6Validator(sch, resolver=resolver)
    v_modif = DefaultValidator(sch, resolver=resolver)

    fp = os.path.join(test_dir, "schemas", "NgoPnodePhase.json")
    with open(fp, "rb") as f:
        instance = json.loads(f.read().decode("utf-8"))

    # even with an expanded schema, derived types are not resolved
    # derived types schemas are redefined with 'schema' field
    # errors should be due to missing properties (additionalProperties=False should raise those errors)
    # instances of errors should have a 'schema' field which override the actual schema with all missing properties
    errors = sorted(v_orig.iter_errors(instance), key=lambda e: e.path)
    for error in errors:
        # print(error.message)
        # print(list(error.path),list(error.schema_path))
        # pprint(error.instance)
        assert error.validator == "additionalProperties"
        assert error.instance.get("schemaUri")

    # NgoDraft4Validator handles derived types and should not raise errors
    v_modif.validate(instance)

    # the error is in the main expanded schema
    # a boolean has been turned to a string
    fp = os.path.join(test_dir, "schemas", "NgoPnodePhase_invalid1.json")
    with open(fp, "rb") as f:
        instance = json.loads(f.read().decode("utf-8"))

    errors = sorted(v_modif.iter_errors(instance), key=lambda e: e.path)
    assert len(errors) == 1
    error = errors[0]
    assert list(error.path) == ["initializeFromInputs"]
    if six.PY2:
        assert error.message == "u'true' is not of type u'boolean'"
    else:
        assert error.message == "'true' is not of type 'boolean'"

    # the error is further down in a subschema
    # the numerical value has been turned to a string
    fp = os.path.join(test_dir, "schemas", "NgoPnodePhase_invalid2.json")
    with open(fp, "rb") as f:
        instance = json.loads(f.read().decode("utf-8"))

    errors = sorted(v_modif.iter_errors(instance), key=lambda e: e.path)
    assert len(errors) == 1
    error = errors[0]
    assert list(error.path) == [
        "variableGroups",
        0,
        "variables",
        0,
        "literals",
        3,
        "numericalValue",
    ]
    if six.PY2:
        assert error.message == "u'4' is not of type u'integer'"
    else:
        assert error.message == "'4' is not of type 'integer'"


def test_convert_validate():
    with pytest.raises(ValidationError):
        validators.convert_validate([1, 2, 3], {
            "type": "array",
            "maxItems": 2
        })

    p = validators.convert_validate(__file__, decorators.SCH_PATH_FILE)
    assert isinstance(p, pathlib.Path)

    with pytest.raises(ValidationError):
        validators.convert_validate(__file__, decorators.SCH_PATH_DIR)

    d = validators.convert_validate("25/05/2018", decorators.SCH_DATE)
    assert isinstance(d, datetime.date)

    e = validators.convert_validate(1, {"enum": ["A", "B", "C"]})
    assert e == "A"


if __name__ == "__main__":
    test_validate_extends()
    test_validate_subschemas()
    test_convert_validate()

# *- coding: utf-8 -*-
"""
json-schema validator classes

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import six
import gettext
from builtins import object
from builtins import str
from pyrsistent import pmap

from jsonschema.validators import Draft6Validator
from jsonschema.validators import extend

from python_jsonschema_objects.validators import registry
from python_jsonschema_objects.validators import converter_registry
from python_jsonschema_objects.validators import ValidationError

from . import js_validators as _validators
from .schemas_loader import _load_schema

_ = gettext.gettext

# useful schemas shortcuts
SCH_STR = pmap({ "type": "string" })
SCH_INT = pmap({ "type": "integer" })
SCH_NUM = pmap({ "type": "number" })
SCH_STR_ARRAY = pmap({ "type": "array", "items": { "type": "string"} })
SCH_PATH = pmap({ "type": "path"})
SCH_PATH_DIR = pmap({ "type": "path", "isPathDir": True})
SCH_PATH_FILE = pmap({ "type": "path", "isPathFile": True})
SCH_PATH_EXISTS = pmap({ "type": "path", "isPathExisting": True})
SCH_DATE = pmap({ "type": "date"})
SCH_TIME = pmap({ "type": "time"})
SCH_DATETIME = pmap({ "type": "datetime"})

NgoDraft01Validator = extend(
    Draft6Validator,
    validators={
        "$ref": _validators.ref_ngo_draft1,
        "extends": _validators.extends_ngo_draft1,
        "properties": _validators.properties_ngo_draft1,
    })

NgoDraft02Validator = extend(
    Draft6Validator,
    validators={
        "$ref": _validators.ref_ngo_draft2,
        "extends": _validators.extends_ngo_draft1,
        "properties": _validators.properties_ngo_draft2,
    })
NgoDraft02Validator.META_SCHEMA = _load_schema('ngo-draft-02')

NgoDraft03Validator = extend(NgoDraft02Validator)
NgoDraft03Validator.META_SCHEMA = _load_schema('ngo-draft-03')

NgoDraft04Validator = extend(NgoDraft03Validator)
NgoDraft04Validator._setDefaults = False
NgoDraft04Validator.META_SCHEMA = _load_schema('ngo-draft-04')

DefaultValidator = NgoDraft04Validator


def convert_validate(value, schema):
    ret = value
    type_ = 'enum' if 'enum' in schema else schema.get('type','object')

    converter  = converter_registry(type_)
    if converter is not None:
        ret = converter(None, value, schema)

    if type_ == 'array':
        assert isinstance(ret,(list,tuple))
        # validate items
        sch_items = schema.get('items',{})
        if sch_items:
            for i, e in enumerate(ret):
                ret[i] = convert_validate(e, sch_items)
        # validate length
        if 'minItems' in schema and len(ret) < schema['minItems']:
            raise ValidationError("{1} has too few elements. Wanted {0}."
                    .format(schema['minItems'], value))
        if 'maxItems' in schema and len(ret) > schema['maxItems']:
            raise ValidationError("{1} has too many elements. Wanted {0}."
                    .format(schema['maxItems'], value))
        # validate uniqueness
        if 'uniqueItems' in schema and len(set(ret)) != len(ret):
            raise ValidationError(
                    "{0} has duplicate elements, but uniqueness required"
                    .format(value))

    for param, paramval in sorted(six.iteritems(schema),
                                  key=lambda x: x[0].lower() != 'type'):
        validator = registry(param)
        if validator is not None:
            validator(paramval, ret, schema)

    return ret

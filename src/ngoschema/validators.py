# *- coding: utf-8 -*-
"""
json-schema validator classes

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import gettext
from builtins import object
from builtins import str

from jsonschema.validators import Draft6Validator
from jsonschema.validators import extend

from . import _js_validators as _validators
from .schemas_loader import _load_schema

_ = gettext.gettext

NgoDraft01Validator = extend(
    Draft6Validator,
    validators={
        "$ref": _validators.ref_ngo_draft1,
        "extends": _validators.extends_ngo_draft1,
        "properties": _validators.properties_ngo_draft1,
    })
NgoDraft01Validator._setDefaults = False

NgoDraft02Validator = extend(
    Draft6Validator,
    validators={
        "$ref": _validators.ref_ngo_draft2,
        "extends": _validators.extends_ngo_draft1,
        "properties": _validators.properties_ngo_draft2,
    })
NgoDraft02Validator._setDefaults = False
NgoDraft02Validator.META_SCHEMA = _load_schema('ngo-draft-02')

NgoDraft03Validator = extend(NgoDraft02Validator)
NgoDraft03Validator.META_SCHEMA = _load_schema('ngo-draft-03')

NgoDraft04Validator = extend(NgoDraft03Validator)
NgoDraft04Validator.META_SCHEMA = _load_schema('ngo-draft-04')

DefaultValidator = NgoDraft04Validator

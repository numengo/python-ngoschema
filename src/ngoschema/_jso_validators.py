# *- coding: utf-8 -*-
""" schema validators to extend jsonschema library

_validators.py - created on 02/01/2018
author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import logging

from builtins import object
from builtins import str
from past.builtins import basestring

import gettext
import collections

from python_jsonschema_objects import validators
from python_jsonschema_objects.validators import ValidationError, registry, type_registry


from ngoschema.exceptions import InvalidValue
from ngoschema._decorators import take_arrays
from ngoschema._utils import import_from_string

_ = gettext.gettext


@registry.register()
def minimum(param, value, type_data):
    if value < param:
        raise ValidationError("{0} is less than {1}".format(value, param))


@registry.register()
def exclusiveMinimum(param, value, type_data):
    if value <= param:
        raise ValidationError("{0} is less than or equal to {1}".format(value, param))


@registry.register()
def maximum(param, value, type_data):
    if value > param:
        raise ValidationError("{0} is greater than {1}".format(value, param))


@registry.register()
def exclusiveMaximum(param, value, type_data):
    if value >= param:
        raise ValidationError("{0} is greater than or equal to {1}".format(value, param))


@type_registry.register(name='boolean')
def check_boolean_type(param, value, _):
    if not isinstance(value, bool):
        raise ValidationError(
            "{0} is not a boolean".format(value))

@type_registry.register(name='integer')
def check_integer_type(param, value, _):
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(
            "{0} is not an integer".format(value))

@type_registry.register(name='number')
def check_number_type(param, value, _):
    if not isinstance(value, six.integer_types + (float,)) or isinstance(value, bool):
        raise ValidationError(
            "{0} is neither an integer nor a float".format(value))

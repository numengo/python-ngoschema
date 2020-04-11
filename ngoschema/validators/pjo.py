# *- coding: utf-8 -*-
""" schema validators to extend jsonschema library

_validators.py - created on 02/01/2018
author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import pathlib
import logging
import itertools
from builtins import str
from decimal import Decimal

import arrow
import six
from ngoschema.utils import is_importable
from past.builtins import basestring
from python_jsonschema_objects import validators
from python_jsonschema_objects.literals import MakeLiteral
from python_jsonschema_objects.validators import ValidationError
from python_jsonschema_objects.validators import ValidatorRegistry
from python_jsonschema_objects.validators import registry
from python_jsonschema_objects.validators import type_registry
from python_jsonschema_objects.pattern_properties import ExtensibleValidator as pjo_ExtensibleValidator

from ngoschema import utils, settings

logger = logging.getLogger(__name__)

validator_registry = registry

converter_registry = ValidatorRegistry()

formatter_registry = ValidatorRegistry()


#additional types
import datetime
import pathlib
import arrow
from past.builtins import basestring

string_types = (basestring, str)
datetime_types = (datetime.datetime, arrow.Arrow)

# validators
############

@registry.register()
def minimum(param, value, type_data):
    if value < param:
        raise ValidationError("{0} is less than {1}".format(value, param))


@registry.register()
def exclusiveMinimum(param, value, type_data):
    if value <= param:
        raise ValidationError("{0} is less than or equal to {1}".format(
            value, param))


@registry.register()
def maximum(param, value, type_data):
    if value > param:
        raise ValidationError("{0} is greater than {1}".format(value, param))


@registry.register()
def exclusiveMaximum(param, value, type_data):
    if value >= param:
        raise ValidationError("{0} is greater than or equal to {1}".format(
            value, param))


@registry.register()
def isPathDir(param, value, type_data):
    if value.is_dir() != param:
        raise ValidationError(
            "{0} is not the path of a directory".format(value))


@registry.register()
def isPathFile(param, value, type_data):
    if value.is_file() != param:
        raise ValidationError("{0} is not the path of a file".format(value))


@registry.register()
def isPathExisting(param, value, type_data):
    if value.exists() != param:
        raise ValidationError("{0} is not an existing path".format(value))


# type checkers
################

BOOLEAN_TRUE_STR_LIST = ['true']
BOOLEAN_FALSE_STR_LIST = ['false']
@type_registry.register(name='boolean')
def check_boolean_type(param, value, _):
    if isinstance(value, string_types):
        if value.lower() in (BOOLEAN_TRUE_STR_LIST + BOOLEAN_FALSE_STR_LIST):
            return
    if not isinstance(value, bool):
        raise ValidationError(
            "{0} is not a boolean".format(value))


@type_registry.register(name="string")
def check_string_type(param, value, _):
    if not isinstance(value, string_types):
        raise ValidationError("{0} is not a string".format(value))


@type_registry.register(name="number")
def check_number_type(param, value, _):
    number_types = six.integer_types + (float, Decimal)
    if not isinstance(value, number_types):
        raise ValidationError("{0} is neither an integer nor a float".format(value))


@type_registry.register(name="path")
def check_path_type(param, value, _):
    if not isinstance(value, pathlib.Path):
        if not utils.is_string(value):
            raise ValidationError("{0} is not a path".format(value))


@type_registry.register(name="date")
def check_date_type(param, value, _):
    if not isinstance(value, datetime.date):
        if not utils.is_string(value):
            raise ValidationError("{0} is not a date".format(value))


@type_registry.register(name="time")
def check_time_type(param, value, _):
    if not isinstance(value, datetime.time):
        if not utils.is_string(value):
            raise ValidationError("{0} is not a time".format(value))


@type_registry.register(name="datetime")
def check_datetime_type(param, value, _):
    if not isinstance(value, datetime.datetime):
        if not utils.is_string(value):
            raise ValidationError("{0} is not a datetime".format(value))

@type_registry.register(name="importable")
def check_importable_type(param, value, _):
    if not is_importable(value):
        raise ValidationError("{0} is not a importable string".format(value))

# converters
############
@converter_registry.register(name="boolean")
def convert_boolean(value, type_data):
    if utils.is_string(value):
        if value.lower() in BOOLEAN_FALSE_STR_LIST:
            return False
        if value.lower() in BOOLEAN_TRUE_STR_LIST:
            return True
    try:
        return bool(value)
    except:
        pass
    return value


@converter_registry.register(name="integer")
def convert_integer(value, type_data):
    try:
        return int(value)
    except:
        pass
    return value


@converter_registry.register(name="number")
def convert_number(value, type_data):
    try:
        return int(value)
    except:
        try:
            return value if isinstance(value, Decimal) else float(value)
        except:
            pass
    return value


@converter_registry.register(name="importable")
def convert_importable(value, type_data):
    if utils.is_string(value):
        if '/' in value:
            from ..classbuilder import get_builder
            return get_builder().resolve_or_construct(value)
        else:
            return utils.import_from_string(value)
    return value


@converter_registry.register(name="array")
def convert_array(value, type_data):
    if not utils.is_sequence(value):
        if utils.is_string(value):
            return [a.strip() for a in value.split(type_data.get('str_delimiter', ','))]
        else:
            return utils.to_list(value)
    return value


@converter_registry.register(name="enum")
def convert_enum(value, type_data):
    if isinstance(value, int) and "enum" in type_data:
        if type_data.get('type') != 'integer':
            if (value - 1) < len(type_data["enum"]):
                return type_data["enum"][value - 1]
    return value


@converter_registry.register(name="date")
def convert_date_type(value, type_data):
    if isinstance(value, datetime_types):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, string_types):
        if value in ('now', 'today'):
            a = arrow.utcnow()
            return a.date()
        try:
            a = arrow.get(value, settings.DATE_FORMATS)
            if a.time() == datetime.time(0, 0):
                return a.date()
        except Exception:
            pass
        try:
            a = arrow.get(value, settings.ALT_DATE_FORMATS)
            if a.time() == datetime.time(0, 0):
                return a.date()
        except Exception:
            pass
    raise ValidationError("{0} is not a date".format(value))


alt_time_fts = [
    "HH:mm:ssZZ",
    "HH:mm:ss ZZ",
    "HH:mm:ss",
    "HH:mm",
    "HH:mm:ss A",
    "HH:mm A",
]


@converter_registry.register(name="time")
def convert_time_type(value, type_data):
    if isinstance(value, datetime.time):
        return value
    if isinstance(value, datetime_types) and value.date() == datetime.date(
            1, 1, 1):
        return value.time()
    if isinstance(value, string_types):
        if value in ('now'):
            a = arrow.utcnow()
            return a.time()
        try:
            a = arrow.get(value, alt_time_fts)
            if a.date() == datetime.date(1, 1, 1):
                return a.time()
        except Exception:
            pass
    raise ValidationError("{0} is not a time".format(value))


@converter_registry.register(name="datetime")
def convert_datetime_type(value, type_data):
    if isinstance(value, arrow.Arrow):
        return value.datetime
    if isinstance(value, datetime.datetime):
        return arrow.get(value).datetime
    if isinstance(value, string_types):
        if value in ('now'):
            a = arrow.utcnow()
            return a
    try:
        return arrow.get(value).datetime
    except Exception:
        pass
    try:
        a_d = arrow.get(value, settings.ALT_DATE_FORMATS)
        a_t = arrow.get(value, settings.ALT_DATE_FORMATS)
        dt = datetime.datetime.combine(a_d.date(), a_t.time())
        return arrow.get(dt).datetime
    except Exception:
        pass
    raise ValidationError("{0} is not a datetime".format(value))


@converter_registry.register(name="path")
def convert_path_type(value, type_data):
    if isinstance(value, pathlib.Path):
        return value
    if isinstance(value, string_types):
        return pathlib.Path(value)
    raise ValidationError("{0} is not a path".format(value))


# formatters
############

@formatter_registry.register(name="path")
def format_path(value, type_data=None):
    return str(value)


@formatter_registry.register(name="date")
def format_date(value, type_data=None):
    if "format" in type_data:
        fmt = type_data["format"]
        return value.strftime(fmt)
    return value.isoformat()


@formatter_registry.register(name="time")
def format_time(value, type_data=None):
    if "format" in type_data:
        fmt = type_data["format"]
        return value.strftime(fmt)
    return value.isoformat()


@formatter_registry.register(name="datetime")
def format_datetime(value, type_data=None):
    if "format" in type_data:
        fmt = type_data["format"]
        return value.format(fmt)
    return str(value)


@formatter_registry.register(name="importable")
def format_importable(value, type_data):
    if not utils.is_string(value) and utils.is_imported(value):
        if hasattr(value, '__schema_uri__'):
            return value.__schema_uri__
        return utils.fullname(value)
    return value


def convert_to_literal(value, type_data=None):
    if type_data:
        typ = type_data.get('type', 'string')
        check = type_registry(typ)
        check(0, value, type_data)
        convert = converter_registry(typ)
        return convert(value, type_data) if convert else value
    else:
        for typ, check in type_registry.registry.items():
            try:
                check(0, value, {})
                convert = converter_registry(typ)
                return convert(value, {})
            except Exception as er:
                pass
        return str(value)

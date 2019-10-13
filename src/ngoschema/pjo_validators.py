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
from builtins import str
from decimal import Decimal

import arrow
import six
from ngoschema.utils import is_importable
from past.builtins import basestring
from python_jsonschema_objects import validators
from python_jsonschema_objects.validators import ValidationError
from python_jsonschema_objects.validators import converter_registry
from python_jsonschema_objects.validators import formatter_registry
from python_jsonschema_objects.validators import registry
from python_jsonschema_objects.validators import type_registry

from . import utils

string_types = (basestring, str)
datetime_types = (datetime.datetime, arrow.Arrow)

NGO_TYPE_MAPPING = (
    ("importable", string_types),
    ("path", string_types + (pathlib.Path, )),
    ("date", string_types + datetime_types + (datetime.date, )),
    ("time", string_types + datetime_types + (datetime.time, )),
    ("datetime", string_types + datetime_types),
)

validators.set_user_type_mapping(NGO_TYPE_MAPPING)

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


@type_registry.register(name="string")
def check_string_type(param, value, _):
    if not isinstance(value, string_types):
        raise ValidationError("{0} is not a string".format(value))


@type_registry.register(name="number")
def check_number_type(param, value, _):
    if not isinstance(value, six.integer_types + (float, Decimal)):
        raise ValidationError(
            "{0} is neither an integer nor a float".format(value))


@type_registry.register(name="path")
def check_path_type(param, value, _):
    if not isinstance(value, pathlib.Path):
        raise ValidationError("{0} is not a path".format(value))


@type_registry.register(name="date")
def check_date_type(param, value, _):
    if not isinstance(value, datetime.date):
        raise ValidationError("{0} is not a date".format(value))


@type_registry.register(name="time")
def check_time_type(param, value, _):
    if not isinstance(value, datetime.time):
        raise ValidationError("{0} is not a time".format(value))


@type_registry.register(name="datetime")
def check_datetime_type(param, value, _):
    if not isinstance(value, datetime.datetime):
        raise ValidationError("{0} is not a datetime".format(value))

@type_registry.register(name="importable")
def check_importable_type(param, value, _):
    if not is_importable(value):
        raise ValidationError("{0} is not a importable string".format(value))


# converters
############

@converter_registry.register(name="integer")
def convert_integer(param, value, detail):
    try:
        return int(value)
    except:
        pass
    return value


@converter_registry.register(name="number")
def convert_number(param, value, detail):
    try:
        return int(value)
    except:
        try:
            return value if isinstance(value, Decimal) else float(value)
        except:
            pass
    return value


@converter_registry.register(name="importable")
def convert_importable(param, value, detail):
    if not utils.is_string(value) and utils.is_imported(value):
        return utils.fullname(value)
    return value


@converter_registry.register(name="array")
def convert_array(param, value, detail):
    if utils.is_sequence(value):
        return value
    return list(value)


@converter_registry.register(name="enum")
def convert_enum(param, value, details):
    if isinstance(value, int) and "enum" in details:
        if (value - 1) < len(details["enum"]):
            return details["enum"][value - 1]
    return value


date_fts = [
    "YYYY-MM-DD", "YYYY/MM/DD", "YYYY.MM.DD", "YYYY-MM", "YYYY/MM", "YYYY.MM"
]
alt_date_fts = [
    "DD-MM-YYYY",
    "DD/MM/YYYY",
    "DD.MM.YYYY",
    "MM-YYYY",
    "MM/YYYY",
    "MM.YYYY",
]


@converter_registry.register(name="date")
def convert_date_type(param, value, detail):
    if isinstance(value, datetime_types):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, string_types):
        if value in ('now', 'today'):
            a = arrow.utcnow()
            return a.date()
        try:
            a = arrow.get(value, date_fts)
            if a.time() == datetime.time(0, 0):
                return a.date()
        except Exception:
            pass
        try:
            a = arrow.get(value, alt_date_fts)
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
def convert_time_type(param, value, _):
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
def convert_datetime_type(param, value, _):
    if isinstance(value, arrow.Arrow):
        return value.datetime
    if isinstance(value, datetime.datetime):
        return arrow.get(value)
    if isinstance(value, string_types):
        if value in ('now'):
            a = arrow.utcnow()
            return a
    try:
        return arrow.get(value).datetime
    except Exception:
        pass
    try:
        a_d = arrow.get(value, alt_date_fts)
        a_t = arrow.get(value, alt_time_fts)
        dt = datetime.datetime.combine(a_d.date(), a_t.time())
        return arrow.get(dt).datetime
    except Exception:
        pass
    raise ValidationError("{0} is not a datetime".format(value))


@converter_registry.register(name="path")
def convert_path_type(param, value, _):
    if isinstance(value, pathlib.Path):
        return value
    if isinstance(value, string_types):
        return pathlib.Path(value)
    raise ValidationError("{0} is not a path".format(value))


# formatters
############

@formatter_registry.register(name="path")
def format_path(param, value, details):
    return str(value)


@formatter_registry.register(name="date")
def format_date(param, value, details):
    if "format" in details:
        frmt = details["format"]
        return value.strftime(frmt)
    return value.isoformat()


@formatter_registry.register(name="time")
def format_time(param, value, details):
    if "format" in details:
        frmt = details["format"]
        return value.strftime(frmt)
    return value.isoformat()


@formatter_registry.register(name="datetime")
def format_arrow(param, value, details):
    if "format" in details:
        frmt = details["format"]
        return value.format(frmt)
    return str(value)

# -*- coding: utf-8 -*-
"""
ngofile.exceptions
-----------------------
All exceptions used in the ngofile code base are defined here.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from jsonschema.exceptions import SchemaError
#from python_jsonschema_objects import ValidationError
from jsonschema.exceptions import FormatError, ValidationError


class ConversionError(ValueError):
    """
    Raised if an invalid value is detected in a validator
    """


class InvalidOperation(Exception):
    """
    Raised if an invalid operation is attempted
    """


class ContextError(ValueError):
    """
    Raised if an error happens during context evaluation
    """


class ExpressionError(ConversionError, ContextError):
    """
    Raised if an error happens during expression evaluation
    """


class InvalidValue(ConversionError, ValidationError):
    """
    Raised if an invalid value is detected in a validator
    """
    def __init__(self, *args, **kwargs):
        ValidationError.__init__(self, *args, **kwargs)

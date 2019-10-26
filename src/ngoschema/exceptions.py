# -*- coding: utf-8 -*-
"""
ngofile.exceptions
-----------------------
All exceptions used in the ngofile code base are defined here.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from jsonschema.exceptions import SchemaError
from python_jsonschema_objects import ValidationError


class InvalidValue(ValueError, ValidationError):
    """
    Raised if an invalid value is detected in a validator
    """

class InvalidOperationException(Exception):
    """
    Raised if an invalid operation is attempted
    """

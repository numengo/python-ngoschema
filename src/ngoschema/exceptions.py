# -*- coding: utf-8 -*-
"""
ngofile.exceptions
-----------------------
All exceptions used in the ngofile code base are defined here.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import str

import jsonschema.exceptions


class NgoSchemaException(Exception):
    """
    Base exception class. All ngofile-specific exceptions should subclass
    this class.
    """


class SchemaError(NgoSchemaException, jsonschema.exceptions.SchemaError):
    """
    Raised if an error is detected in a schema
    """


class InvalidValue(NgoSchemaException, jsonschema.exceptions.ValidationError,
                   ValueError):
    """
    Raised if an invalid value is detected in a validator
    """


class PropertyNotInSchema(NgoSchemaException):
    """
    Raisedfif property is not defined in Schema
    """

    def __init__(self, prop):
        message = ("[%(prop)s] does not exist in schema" % {"prop": str(prop)})
        super(NgoSchemaException, self).__init__(message)


class PropertyUndefined(NgoSchemaException):
    """
    Raised property is not defined in Schema
    """

    def __init__(self, prop):
        message = "[%(prop)s] is not defined" % {"prop": str(prop)}
        super(NgoSchemaException, self).__init__(message)

# -*- coding: utf-8 -*-
import pytest
import logging
logging.basicConfig(level=logging.DEBUG)

from ngoschema import get_builder
from ngoschema import ValidationError


def simple_jsonschema_class():
    """Build a class from a simple json-schema
    Test type validation
    """

    schema = {
        'type': 'object',
        'properties': {
            'myInt': {
                'type': 'integer'
            }
        }
    }

    A = get_builder().construct('A', schema)

    # constructor can be called with keyword arguments
    A = A(myInt=3)
    assert A.myInt == 3

    with pytest.raises(ValidationError):
        A.myInt = "a string"

    A.myExtraProperty = 2


def value_validation_jsonschema_class():
    """Build a class from a schema with value validation
    Test value validation and conversion
    """
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'myInt': {
                'type': 'integer',
                'minimum': 0,
                'maximum': 5
            },
            'myString': {
                'type': 'string',
                'maxLength': 10
            },
            'myStringUpperCased': {
                'type': 'string',
                # can use any filter from inflection library
                # camelize, dasherize, ordinal, ordinalize, parameterize, pluralize, 
                # singularize, tableize, titleize, transliterate, underscore
                'default': '__{{this.myString|upper}}__'
            }
        },
        # readOnly, required and notSerialized are defined at the scope of the object
        'readOnly': ['myStringUpperCased']
    }

    B = get_builder().construct('B', schema)
    b = B()

    b.myInt = 3
    # automatically converts to integer
    b.myInt = "3"
    assert b.myInt == 3
    # raise an exception if out of bounds
    with pytest.raises(ValidationError):
        b.myInt = 10
    with pytest.raises(ValidationError):
        b.myInt = "10"

    b.myString = "a string"    
    with pytest.raises(ValidationError):
        b.myString = "a string exceeding max length"
    assert b.myStringUpperCased == '__A STRING__' 
    b.myString = "another"
    assert b.myStringUpperCased == '__ANOTHER__' 
    # no additional property permitted on this class
    with pytest.raises(AttributeError):
        b.myStringUpperCased = 'read only'


def class_with_complex_types():
    """Build a class from a schema with complex types such a path, date or datetime
    Test value validation and conversion
    """
    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'myPath': {
                'type': 'path',
                # also exists in the vocabulary: isPathDir, isPathFile
                'isPathExisting': True
            },
            'myDate': {
                'type': 'date',
                'format': 'DD/MM/YYYY'
            },
            'myDatetime': {
                'type': 'datetime'
            }
        }
    }

    C = get_builder().construct('C', schema)
    c = C()

    # an always existing path: parent
    c.myPath = ".."
    # member can then be used as a pathlib.Path object
    c.myPath.exists()

    with pytest.raises(ValidationError):
        c.myPath = "a_path_that_does_not_exist"

    c.myDate = "16/02/2013"
    assert c.myDate.day == 16
    from datetime import date
    assert isinstance(c.myDate._value, date)
    # can also be initialized from date
    c.myDate = date(2013,2,16)
    # can also be initialized from datetime but still will be casted
    from datetime import datetime
    c.myDate = datetime(2013,2,16,12,00)
    assert isinstance(c.myDate._value, date)
    assert c.myDate.day == 16

    c.myDatetime = "2013-02-16T12:30"
    # datetime object is accessible
    my_datetime = c.myDatetime.datetime
    assert isinstance(my_datetime, datetime)
    # any naive datetime is automatically localized as utc
    assert my_datetime.tzinfo is not None \
        and my_datetime.tzinfo.utcoffset(my_datetime) is not None
    # datetime is managed by an Arrow object. To replace timezone
    c.myDatetime = c.myDatetime.replace(tzinfo='Europe/Paris')
    # time has not changed
    assert c.myDatetime.datetime.hour == 12
    # datetime is serialized as an iso formatted string (unless specified otherwise)
    assert c.myDatetime.for_json() == '2013-02-16T12:30:00+01:00'


if __name__ == "__main__":
    simple_jsonschema_class()
    value_validation_jsonschema_class()    
    class_with_complex_types()
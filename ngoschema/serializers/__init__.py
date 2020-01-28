from .fields import (
    Field, BoolField, IntField, FloatField, MethodField, StrField)
from .serializer import Serializer, DictSerializer

# from https://github.com/maroux/serpy.git
# credit to Clark DuVall and Aniruddha Maru

__version__ = '0.0.3'
__author__ = 'Clark DuVall'
__license__ = 'MIT'

__all__ = [
    'Serializer',
    'DictSerializer',
    'Field',
    'BoolField',
    'IntField',
    'FloatField',
    'MethodField',
    'StrField',
]

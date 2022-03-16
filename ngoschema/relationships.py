# *- coding: utf-8 -*-
"""
Foreign key component

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 28/01/2019
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from .decorators import classproperty
from .protocols import with_metaclass, SchemaMetaclass, ObjectProtocol
from .types import String
from .types.foreign_key import ForeignKey as ForeignKey_t


class Relationship(with_metaclass(SchemaMetaclass, ForeignKey_t)):
    """
    Class to deal with relationships
    """
    _id = 'https://numengo.org/ngoschema#/$defs/relationships/$defs/Relationship'
    _inheritance = False
    _reverse = False

    def __new__(cls, *args, **kwargs):
        new = super(ObjectProtocol, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        ObjectProtocol.__init__(self, *args, **kwargs)
        ForeignKey_t.__init__(self, *args, **kwargs)

    def set_foreignSchema(self, value):
        return ForeignKey_t.set_foreignSchema(self, value)

    def set_foreignClass(self, value):
        return ForeignKey_t.set_foreignClass(self, value)

    #def resolve(self, keys):
    #    return self._foreignClass.resolve_by_keys(keys)


class ForeignKey(with_metaclass(SchemaMetaclass)):
    """
    Class to deal with relationships
    """
    _id = 'https://numengo.org/ngoschema#/$defs/relationships/$defs/ForeignKey'

    def __new__(cls, *args, **kwargs):
        # to avoid to go through ObjectProtocol.__new__ which uses $schema for subclassing
        new = super(ObjectProtocol, cls).__new__
        if new is object.__new__:
            return new(cls)
        return new(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        Relationship.__init__(self, *args, **kwargs)

    @staticmethod
    def _serialize(self, value, **opts):
        if String.check(value):
            return {'foreignSchema': value}
        return ObjectProtocol._serialize(self, value, **opts)


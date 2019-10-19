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


class Relationship:
    """
    Class to deal with relationships
    """
    __propinfo__ = {}

    @classmethod
    def _propinfo(cls, name, default=None):
        return cls.__propinfo__.get(name, default)

    @classproperty
    def foreignSchema(cls):
        return cls._propinfo('$schema')

    @classproperty
    def fkeys(cls):
        return cls._propinfo('fkeys')

    @classproperty
    def isOne2Many(cls):
        return cls._propinfo('cardinality') == 'one2many'

    @classproperty
    def ordering(cls):
        return cls._propinfo('ordering')

    @classproperty
    def reverse(cls):
        return cls._propinfo('reverse', False)

    _foreignClass = None
    @classproperty
    def foreignClass(cls):
        from .classbuilder import get_builder
        from .keyed_object import KeyedObject
        if not cls._foreignClass and cls.foreignSchema:
            try:
                cls._foreignClass = get_builder().resolve_or_build(cls.foreignSchema)
            except Exception as er:
                cls.logger.error(er)
            if not issubclass(cls._foreignClass, KeyedObject):
                raise ValueError('target class (%r) must implement (%r) interface.' \
                                % (cls._foreignClass, KeyedObject))
        return cls._foreignClass

    def resolve(self, keys):
        return self.foreignClass.resolve_by_keys(keys)

    def __get__(self):
        return self.resolve(self.fkeys)

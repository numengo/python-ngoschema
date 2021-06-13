# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .converter import Converter
from .validator import Validator


class Deserializer(Validator):
    _validator = Validator
    _many = False

    def __init__(self, validator=None, **opts):
        self._validator = validator or self._validator
        self._validator.__init__(self, **opts)
        self._many = opts.get('many', self._many)

    @staticmethod
    def _is_included(key, value=None, excludes=[], only=[], no_defaults=False, **opts):
        if key in excludes:
            return False
        if only and key not in only:
            return False
        if value is not None:
            vk = getattr(value, '_data', value)  # trick to use data dict instead of protocolbased which gets triggered
            if isinstance(key, str):
                if key not in vk:
                    return False
            else:
                if key >= len(vk):
                    return False
            value = vk[key]
        if no_defaults:
            if value is None:
                return False
        return True

    @staticmethod
    def _deserialize(self, value, evaluate=True, **opts):
        value = self._validator._evaluate(self, value, **opts) if evaluate else value
        return value

    def __call__(self, value, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        value = self._deserialize(self, value, **opts)
        return value

    @classmethod
    def deserialize(cls, value, evaluate=True, **opts):
        opts['context'] = cls.create_context(**opts)
        #value = cls._deserialize(cls, value, evaluate=evaluate, **opts)
        value = cls._deserialize(cls, value, evaluate=False, **opts)
        value = cls._validator._evaluate(cls, value, **opts) if evaluate else value
        return value


class Serializer(Deserializer):
    _deserializer = Deserializer

    def __init__(self, deserializer=None, **opts):
        self._deserializer = deserializer or self._deserializer
        self._deserializer.__init__(self, **opts)

    @staticmethod
    def _serialize(self, value, deserialize=True, **opts):
        value = self._deserializer._deserialize(self, value, **opts) if deserialize else value
        return value

    def __call__(self, value, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        return self._serialize(self, value, **opts)

    @classmethod
    def serialize(cls, value, **opts):
        #opts['context'] = cls.create_context(**opts)
        opts.setdefault('context', cls._context)
        return cls._serialize(cls, value, **opts)


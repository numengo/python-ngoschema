# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .serializer import Serializer, Deserializer


class Loader(Deserializer):
    _deserializer = Deserializer
    _instanceClass = None

    def __init__(self, deserializer=None, instanceClass=None, **opts):
        from ..types.symbols import Symbol
        self._deserializer = deserializer or self._deserializer
        self._deserializer.__init__(self, **opts)
        self._instanceClass = Symbol.convert(instanceClass or self._instanceClass)

    @staticmethod
    def _load(self, value, many=False, deserialize=True, **opts):
        from ..types import Symbol, Array
        instance_class = Symbol.convert(opts.get('instance_class', self._instanceClass))
        if many:
            value = Array.deserialize(value, split_string=True)
            value = [self._deserializer._deserialize(self, v, evaluate=False, **opts) if deserialize else v
                     for v in value]
            return [instance_class(d, **opts) if instance_class else d for d in value]
        else:
            value = self._deserializer._deserialize(self, value, evaluate=False, **opts) if deserialize else value
            return instance_class(value, **opts) if instance_class else value

    def __call__(self, value, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        raise self._load(self, value, **opts)

    #@classmethod
    def load(self, value, **opts):
        #opts['context'] = cls.create_context(**opts)
        opts.setdefault('context', self._context)
        return self._load(self, value, **opts)


class Saver(Serializer, Loader):
    _serializer = Serializer
    _loader = Loader

    def __init__(self, serializer=None, loader=None, **opts):
        self._loader = loader or self._loader
        self._loader.__init__(self, **opts)
        self._serializer = serializer or self._serializer
        self._serializer.__init__(self, **opts)

    @staticmethod
    def _save(self, value, load=False, serialize=True, **opts):
        value = self._loader._load(self, value, **opts) if load else value
        value = self._serializer._serialize(self, value, **opts) if serialize else value
        return value

    def __call__(self, value, load=False, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        raise self._save(self, value, **opts)

    #@classmethod
    def save(self, value, **opts):
        #opts['context'] = cls.create_context(**opts)
        opts.setdefault('context', self._context)
        return self._save(self, value, **opts)

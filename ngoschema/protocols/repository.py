# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .validator import Validator
from .serializer import Serializer
from .loader import Loader, Saver
from ..registries import repositories_registry


class Repository(Saver):
    _saver = Saver
    _session = None
    _content = None

    def __init__(self, saver=None, session=None, **opts):
        from ..protocols.array_protocol import ArrayProtocol
        self._saver = saver or self._saver
        self._saver.__init__(self, **opts)
        self._session = session or self._session
        if self._many:
            self._content = []

    @staticmethod
    def _commit(self, value, save=True, **opts):
        """ optionally load the value (at least validate it) and add it to content """
        value = self._saver._save(self, value, **opts) if save else value
        if self._many:
            self._content.extend(value)
        else:
            self._content = value
        return self._content

    def dump(self, **opts):
        """ serialize repository content """
        return self._saver._save(self, self._content, **opts)

    def __call__(self, value, **opts):
        opts['context'] = self.create_context(**opts)
        return self._commit(self, value, **opts)

    @classmethod
    def commit(cls, value, load=True, **opts):
        opts['context'] = cls.create_context(**opts)
        return cls._commit(cls, value, **opts)

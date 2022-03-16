# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .validator import Validator
from .serializer import Serializer
from .loader import Loader, Saver
from ..session import default_session
from ..types.object import Object
from ..registries import repositories_registry


class Repository(Saver):
    _saver = Saver
    _session = default_session
    _content = None

    def __init__(self, saver=None, session=None, **opts):
        from ..protocols.array_protocol import ArrayProtocol
        self._saver = saver or self._saver
        self._saver.__init__(self, **opts)
        self._session = session or self._session
        self._session.bind_repo(self)
        if self._many:
            self._content = []

    @staticmethod
    def _deserialize(self, value, **opts):
        return Object._deserialize(self, value, **opts)

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
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        return self._commit(self, value, **opts)

    def commit(self, value, **opts):
        opts.setdefault('context', self._context)
        return self._commit(self, value, **opts)

    def __contains__(self, item):
        return item in self._content

    def query(self, *attrs, **attrs_value):
        from ..query import Query
        return Query(self._content).get(*attrs, **attrs_value)

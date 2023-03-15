# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext

from .validator import Validator
from .serializer import Serializer
from .loader import Loader, Saver
from ..session import default_session
from ..datatypes.object import Object
from ..registries import repositories_registry

_ = gettext.gettext


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

    @property
    def session(self):
        return self._session

    @staticmethod
    def _deserialize(self, value, **opts):
        return Object._deserialize(self, value, **opts)

    @staticmethod
    def _commit(self, value, save=True, **opts):
        _("""Optionally load the value (at least validate it) and add it to content """)
        value = self._saver._save(self, value, **opts) if save else value
        if self._many:
            self._content.extend(value)
        else:
            self._content = value
        return self._content

    def dump(self, **opts):
        _("""Serialize repository content.""")
        return self._saver._save(self, self._content, **opts)

    def __call__(self, value, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        return self._commit(self, value, **opts)

    def commit(self, value, **opts):
        opts.setdefault('context', self._context)
        return self._commit(self, value, **opts)

    def __contains__(self, item):
        return item in self.index

    @property
    def index(self):
        ic = self._instanceClass
        pks = ic._primaryKeys
        return [c.identity_keys if len(pks) > 1 else c.identity_keys[0] for c in self._content]

    def get_by_id(self, *identity_keys):
        return self.resolve_fkey(identity_keys)

    def query(self, *attrs, **attrs_value):
        from ..query import Query
        return Query(self._content).get(*attrs, **attrs_value)

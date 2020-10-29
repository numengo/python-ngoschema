# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from ..protocols.loader import Loader, Saver
from ..protocols.repository import Repository
from ..registries import repositories_registry
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol


class MemoryRepository(with_metaclass(SchemaMetaclass, Repository)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/MemoryRepository'

    def __init__(self, value=None, **opts):
        from ..protocols.array_protocol import ArrayProtocol
        Repository.__init__(self, **opts)
        ObjectProtocol.__init__(self, value, **opts)
        self._content = ArrayProtocol(items=self._instanceClass, maxItems=1 if not self._many else None)(content)

    def get(self, identity_keys, **opts):
        if self._content:
            return self._content.get(identity_keys, **opts)

    @staticmethod
    def _commit(self, value, save=False, **opts):
        """ optionally load the value (at least validate it) and add it to content """
        value = self._saver._save(self, value, **opts) if save else value
        if self._many:
            self._content.extend(value)
        else:
            self._content = self._content(value)
        return self._content

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict

from ..protocols.loader import Loader, Saver
from ..protocols.repository import Repository
from ..registries import repositories_registry
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol


class MemoryRepository(with_metaclass(SchemaMetaclass, Repository)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/MemoryRepository'
    _catalog = None

    def __init__(self, value=None, meta_opts=None, **opts):
        from ..types import Array
        #from ..protocols.array_protocol import ArrayProtocol
        ObjectProtocol.__init__(self, **opts)
        Repository.__init__(self, **(meta_opts or {}), **self)
        self._catalog = OrderedDict()
        self._content = Array(items=self._instanceClass, maxItems=1 if not self._many else None)(value)

    def __repr__(self):
        return f'{self.qualname()}[{len(self._catalog)}]'

    def __str__(self):
        return f'{self.qualname()}[{len(self._catalog)}]'

    def __contains__(self, item):
        return item in self._catalog

    def resolve_fkey(self, identity_keys):
        return self._catalog[identity_keys]

    @staticmethod
    def _commit(self, value, save=False, **opts):
        """ optionally load the value (at least validate it) and add it to content """
        value = self._saver._save(self, value, **opts) if save else value
        if self._many:
            # check/set identity keys
            pk = value.identityKeys
            for i, k in enumerate(pk):
                iks = [c.identityKeys[i] for c in self._content]
                if k is None:
                    k = max([-1] + iks) + 1
                    value._set_data(value.primaryKeys[i], k)
            pk = value.identityKeys
            self._catalog[value._identityKeys] = value
            for i, c in enumerate(self._content):
                if pk == c.identityKeys:
                    self._content[i] = value
                    break
            else:
                self._content.append(value)
        else:
            self._content = self._content(value)
        return self._content

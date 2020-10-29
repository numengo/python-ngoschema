# *- coding: utf-8 -*-
"""
Foreign key component

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 28/01/2019
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from future.utils import with_metaclass

from .. import settings
from ..decorators import memoized_property, depend_on_prop
from ..protocols import SchemaMetaclass, ObjectProtocol, ArrayProtocol, Context
from ..contexts import InstanceContext, EntityContext

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class Instance(with_metaclass(SchemaMetaclass, InstanceContext)):
    _id = "https://numengo.org/ngoschema#/$defs/instances/$defs/Instance"

    def __str__(self):
        if self._str is None:
            cn = self._canonicalName
            a = ([cn] if cn else []) + [f'{k}={str(self._data_validated[k] or self._data[k])}' for k in self._required]
            self._str = '<%s %s>' % (self.qualname(), ' '.join(a))
        return self._str

    @depend_on_prop('name')
    def get_canonicalName(self):
        return self._canonicalName

    def get_parentInstance(self):
        return self._parentInstance  # set in context

    @property
    def _canonicalName(self):
        # one that does not trigger lazyloading
        pi = self._parentInstance
        n = self._data_validated.get('name') or self._data.get('name')
        return f'{pi._canonicalName}.{n}' if pi else n


class InstanceList(with_metaclass(SchemaMetaclass, ArrayProtocol, InstanceContext)):
    _id = "https://numengo.org/ngoschema#/$defs/instances/$defs/InstanceList"


class Entity(with_metaclass(SchemaMetaclass, EntityContext)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _id = "https://numengo.org/ngoschema#/$defs/instances/$defs/Entity"
    _primaryKeys = ('canonicalName', )
    _identityKeys = None

    def __init__(self, value=None, primaryKeys=None, *opts):
        self._primaryKeys = primaryKeys or self._primaryKeys
        Instance.__init__(self, value, *opts)

    def get_primaryKeys(self):
        return self._primaryKeys

    def get_identityKeys(self):
        self._identityKeys = tuple(self[k] for k in self._primaryKeys)
        return self._identityKeys

    def _serialize(self, value, root_entity=False, **opts):
        use_identity_keys = opts.get('useIdentityKeys', False)
        use_entity_keys = opts.get('useEntityKeys', False)
        if not root_entity:
            if use_identity_keys:
                ik = value.identityKeys
                return ik[0] if len(ik) == 1 else ik
            if use_entity_keys:
                keys = self.primaryKeys
                assert len(keys) == 1, keys
                return {(keys[0] if keys[0] != '$id' else '$ref'): self.identityKeys[0]}
        return ObjectProtocol._serialize(self, value, **opts)


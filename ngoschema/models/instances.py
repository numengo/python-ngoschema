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
from collections import Mapping

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
            a = ([cn] if cn else []) + [f'{k}={str(self._dataValidated[k] or self._data[k])}' for k in self._required]
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
        n = self._dataValidated.get('name') or self._data.get('name')
        return f'{pi._canonicalName}.{n}' if pi is not None else n


class InstanceList(with_metaclass(SchemaMetaclass, ArrayProtocol, InstanceContext)):
    _id = "https://numengo.org/ngoschema#/$defs/instances/$defs/InstanceList"


class Entity(with_metaclass(SchemaMetaclass, EntityContext)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _id = "https://numengo.org/ngoschema#/$defs/instances/$defs/Entity"
    _primaryKeys = tuple()
    _identityKeys = None

    def __new__(cls, *args, **kwargs):
        if args and args[0] and not isinstance(args[0], Mapping):
            context = kwargs.get('context')
            session = context._session if context else None
            session = session or cls._session
            inst = session.resolve_fkey(args, cls)
            cls = inst.__class__
        return ObjectProtocol.__new__(cls, *args, **kwargs)

    def __init__(self, value=None, primaryKeys=None, **opts):
        self._primaryKeys = primaryKeys or self._primaryKeys
        if value and not isinstance(value, Mapping):
            context = opts.get('context')
            session = context._session if context else None
            session = session or self._session
            value = session.resolve_fkey(value, self.__class__)
        Instance.__init__(self, value, **opts)
        self.identityKeys

    def __str__(self):
        if self._str is None:
            ks = [str(k) for k in self._identityKeys]
            self._str = '<%s %s>' % (self.qualname(), ', '.join(ks))
        return self._str

    def get_primaryKeys(self):
        return self._primaryKeys

    def get_identityKeys(self):
        self._identityKeys = tuple(self[k] for k in self._primaryKeys)
        return self._identityKeys

    @staticmethod
    def _serialize(self, value, root_entity=False, **opts):
        use_identity_keys = opts.get('use_identity_keys', False)
        use_entity_keys = opts.get('use_entity_keys', False)
        add_identity_keys = opts.get('add_identity_keys', False)
        if value and not root_entity:
            if use_identity_keys:
                ik = value.identityKeys
                return ik[0] if len(ik) == 1 else ik
            if use_entity_keys:
                keys = self.primaryKeys
                assert len(keys) == 1, keys
                return {(keys[0] if keys[0] != '$id' else '$ref'): self.identityKeys[0]}
        data = ObjectProtocol._serialize(self, value, **opts)
        if add_identity_keys:
            for k in self._primaryKeys:
                pk = value[k]
                if pk is not None:
                    data[k] = value[k]
        return data

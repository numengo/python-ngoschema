# *- coding: utf-8 -*-
"""
Foreign key component

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 28/01/2019
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
from future.utils import with_metaclass
from collections import Mapping

from .. import settings
from ..exceptions import ConversionError
from ..decorators import memoized_property, depend_on_prop
from ..protocols import SchemaMetaclass, ObjectProtocol, ArrayProtocol, Context
from ..contexts import InstanceContext, EntityContext
from ..utils import to_list

_ = gettext.gettext
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


class Entity(with_metaclass(SchemaMetaclass, EntityContext)):
    _("""
    Object referenced by a list of keys of a foreign schema
    """)
    _id = "https://numengo.org/ngoschema#/$defs/instances/$defs/Entity"
    _primaryKeys = tuple()
    _identityKeys = None

    def __new__(cls, *args, **kwargs):
        if args and args[0] and not isinstance(args[0], Mapping):
            context = kwargs.get('context')
            session = context._session if context else None
            if session:
                inst = session.resolve_fkey(args, cls)
                cls = inst.__class__
        return ObjectProtocol.__new__(cls, *args, **kwargs)

    def __init__(self, value=None, primaryKeys=None, **opts):
        from ngoschema.session import default_session
        self._primaryKeys = primaryKeys or self._primaryKeys
        if value and not isinstance(value, Mapping):
            context = opts.get('context')
            session = context._session if context else None
            session = session or getattr(self._context, '_session', default_session)
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
        self._identityKeys = tuple(self.items_serialize(k) for k in self._primaryKeys)
        #self._identityKeys = tuple(self[k] for k in self._primaryKeys)
        return self._identityKeys

    @staticmethod
    def _convert(self, value, **opts):
        _(""" method to overload locally for extra check. Allows to associate a message to check failure.""")
        if isinstance(value, self._pyType):
            return value
        if isinstance(value, Mapping):
            return Instance._convert(self, value)
        # interpret value as identiy keys
        pks = self._primaryKeys
        pks_type = [self._items_type(self, pk) for pk in pks]
        ids = to_list(value)
        if len(ids) == len(pks_type):
            if all([pk_type.check(v) for pk_type, v in zip(pks_type, ids)]):
                ids = tuple(pk_type.convert(v, **opts) for pk_type, v in zip(pks_type, ids))
                return ids
        raise ConversionError('Impossible to get proper identity keys for %s from %s.' % (self.__class__, value))

    @staticmethod
    def _check(self, value, **opts):
        _(""" method to overload locally for extra check. Allows to associate a message to check failure.""")
        pks = self._primaryKeys
        pks_type = [self._items_type(self, pk) for pk in pks]
        try:
            return [pk_type._check(pk_type, v, **opts) for pk_type, v in zip(pks_type, to_list(value))]
        except Exception as er:
            return Instance._check(self, value)

    @staticmethod
    def _serialize(self, value, root_entity=False, **opts):
        _("""
        root_entity: flag to signal the object is the root entity to serialize
        use_identity_keys: serialize only the identity keys (if not root)
        use_entity_keys: returns a dict of identity keys values (if not root)
        add_identity_keys: ensure the identity keys are serialized
        """)
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

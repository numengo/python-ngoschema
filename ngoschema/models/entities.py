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
import sys
import weakref

from .. import settings
from ..decorators import memoized_property
from ..resolver import UriResolver, resolve_uri
from ..types import ObjectMetaclass, ObjectProtocol
from ..types.foreign_key import Ref, ForeignKey
from ..types.type_builder import TypeBuilder
from ngoschema.resolver import scope
from .metadata import NamedObject, Metadata

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class Entity(with_metaclass(ObjectMetaclass)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _schema_id = "https://numengo.org/ngoschema#/$defs/entities/$defs/Entity"
    _schema_id = "https://numengo.org/ngoschema2#/$defs/entities/$defs/Entity"
    _schema_id = "https://numengo.org/ngoschema#/$defs/entities/$defs/Entity"

    def __init__(self, *args, **kwargs):
        data = args[0] if args else kwargs
        if '$ref' in data:
            data.update(resolve_uri(scope(data.pop('$ref'), self._id)))
        if 'foreignKeys' in kwargs:
            data.update(ForeignKey(**self._schema).resolve(data.pop('foreignKeys')))
        ObjectProtocol.__init__(self, *args, **kwargs)

    def get_primaryKeys(self):
        return self._primary_keys

    @memoized_property
    def identity_keys(self):
          return tuple(self[k] for k in self._primary_keys)

    def do_serialize(self, root_entity=False, use_identity_keys=False, use_entity_ref=False, **opts):
        if not root_entity:
            if use_identity_keys:
                ik = self.identity_keys
                return ik[0] if len(ik) == 1 else ik
            if use_entity_ref:
                keys = self._primary_keys
                assert len(keys) == 1, keys
                return {(keys[0] if keys[0] != '$id' else '$ref'): self.identity_keys[0]}
        return ObjectProtocol.do_serialize(self, use_identity_keys=use_identity_keys, use_entity_ref=use_entity_ref, **opts)


class NamedEntity(with_metaclass(ObjectMetaclass, NamedObject)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _schema_id = "https://numengo.org/ngoschema#/$defs/NamedEntity"
    _schema_id = "https://numengo.org/ngoschema2#/$defs/entities/$defs/NamedEntity"
    _schema_id = "https://numengo.org/ngoschema#/$defs/entities/$defs/NamedEntity"

    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)


class CanonicalNamedEntity(with_metaclass(ObjectMetaclass, NamedEntity)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _schema_id = "https://numengo.org/ngoschema#/$defs/CanonicalNamedEntity"
    _schema_id = "https://numengo.org/ngoschema2#/$defs/entities/$defs/CanonicalNamedEntity"
    _schema_id = "https://numengo.org/ngoschema#/$defs/entities/$defs/CanonicalNamedEntity"

    def __init__(self, *args, **kwargs):
        NamedEntity.__init__(self, *args, **kwargs)


class EntityWithMetadata(with_metaclass(ObjectMetaclass, CanonicalNamedEntity, Metadata)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _schema_id = "https://numengo.org/ngoschema#/$defs/entities/$defs/EntityWithMetadata"
    _schema_id = "https://numengo.org/ngoschema2#/$defs/entities/$defs/EntityWithMetadata"
    _schema_id = "https://numengo.org/ngoschema#/$defs/entities/$defs/EntityWithMetadata"

    def __init__(self, *args, **kwargs):
        NamedEntity.__init__(self, *args, **kwargs)

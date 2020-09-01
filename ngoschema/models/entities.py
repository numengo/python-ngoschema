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
from ..protocols import SchemaMetaclass, ObjectProtocol
from ngoschema.resolver import scope
from .metadata import NamedObject, Metadata

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class Entity(with_metaclass(SchemaMetaclass)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _id = "https://numengo.org/ngoschema#/$defs/entities/$defs/Entity"

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


class NamedEntity(with_metaclass(SchemaMetaclass)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _id = "https://numengo.org/ngoschema#/$defs/entities/$defs/NamedEntity"

    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)


class CanonicalNamedEntity(with_metaclass(SchemaMetaclass)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _id = "https://numengo.org/ngoschema#/$defs/entities/$defs/CanonicalNamedEntity"

    def __init__(self, *args, **kwargs):
        NamedEntity.__init__(self, *args, **kwargs)


class EntityWithMetadata(with_metaclass(SchemaMetaclass)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _id = "https://numengo.org/ngoschema#/$defs/entities/$defs/EntityWithMetadata"

    def __init__(self, *args, **kwargs):
        NamedEntity.__init__(self, *args, **kwargs)

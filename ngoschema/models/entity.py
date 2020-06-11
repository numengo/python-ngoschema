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
from ..decorators import classproperty, depend_on_prop
from ..resolver import UriResolver, resolve_uri
from ..types import ObjectMetaclass, ObjectProtocol
from ..types.foreign_key import Ref, ForeignKey
from ..types.type_builder import TypeBuilder, scope
from .metadata import NamedObject, ObjectMetadata

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class Entity(with_metaclass(ObjectMetaclass)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    _schema_id = "https://numengo.org/ngoschema/draft-06#/$defs/Entity"

    def __init__(self, *args, **kwargs):
        data = args[0] if args else kwargs
        if '$ref' in data:
            data.update(resolve_uri(scope(data.pop('$ref'), self._id)))
        if 'foreignKeys' in kwargs:
            data.update(ForeignKey(**self._schema).resolve(data.pop('foreignKeys')))
        ObjectProtocol.__init__(self, *args, **kwargs)

    @classproperty
    def _primaryKeys(cls):
        return cls._schema.get('primaryKeys') or cls._schema['properties']['primaryKeys'].get('default', [])

    _keys = None
    @property
    def identity_keys(self):
        if self._keys is None:
            self._keys = tuple(self[k] for k in self.primaryKeys)
        return self._keys

    def do_serialize(self, use_entity_ref=False, **opts):
        if use_entity_ref:
            keys = self.primaryKeys
            assert len(keys) == 1, keys
            return {(keys[0] if keys[0] != '$id' else '$ref'): self.identity_keys[0]}
        else:
            return ObjectProtocol.do_serialize(self, **opts)


class NamedEntity(with_metaclass(ObjectMetaclass, NamedObject)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _schema_id = "https://numengo.org/ngoschema/draft-06#/$defs/NamedEntity"

    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)


class EntityWithMetadata(with_metaclass(ObjectMetaclass, NamedEntity, ObjectMetadata)):
    """
    Class to deal with metadata and parents/children relationships
    """
    _schema_id = "https://numengo.org/ngoschema/draft-06#/$defs/EntityWithMetadata"

    def __init__(self, *args, **kwargs):
        NamedEntity.__init__(self, *args, **kwargs)

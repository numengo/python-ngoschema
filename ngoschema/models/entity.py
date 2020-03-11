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

from ngoschema import SchemaMetaclass, ProtocolBase
from ngoschema.mixins import HasCanonicalName

from ngoschema.protocol_base import ProtocolBase
from ngoschema.schema_metaclass import SchemaMetaclass

from ngoschema.decorators import classproperty


class Entity(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Object referenced by a list of keys of a foreign schema
    """
    __schema_uri__ = "http://numengo.org/ngoschema/draft-05#/definitions/Entity"

    _keys = None
    @property
    def identity_keys(self):
        if self._keys is None:
            self._keys = {(str(k) if k != '$id' else '$ref'): getattr(self, str(k)).for_json() for k in self.primaryKeys}
        return self._keys

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, *args, **kwargs)


class NamedEntity(with_metaclass(SchemaMetaclass, HasCanonicalName, Entity)):
    """
    Class to deal with metadata and parents/children relationships
    """
    __schema_uri__ = "http://numengo.org/ngoschema/draft-05#/definitions/NamedEntity"

    def __init__(self, *args, **kwargs):
        #HasCanonicalName.__init__(self)
        Entity.__init__(self, *args, **kwargs)

    @classproperty
    def _primaryKeys(cls):
        return cls.__schema__.get('primaryKeys') or ['canonicalName']

    def set_name(self, value):
        HasCanonicalName.set_name(self, value)

    def get_canonicalName(self):
        return self._get_prop_value('canonicalName') or self._cname

    #def set_canonicalName(self, value):
    #    value = value.replace('-', '_')
    #    cn = str(value) if value else None
    #    self._cname = cn
    #    self._set_prop_value('canonicalName', cn)


class EntityWithMetadata(with_metaclass(SchemaMetaclass, NamedEntity)):
    """
    Class to deal with metadata and parents/children relationships
    """
    __schema_uri__ = "http://numengo.org/ngoschema/draft-05#/definitions/EntityWithMetadata"

    def __init__(self, *args, **kwargs):
        NamedEntity.__init__(self, *args, **kwargs)

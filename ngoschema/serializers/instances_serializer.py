# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import collections
from inflection import underscore

from ..datatypes.object import Serializer, ObjectSerializer, ObjectDeserializer, Object
from ..datatypes import Symbol


class InstanceDeserializer(ObjectDeserializer):
    _tag = None
    _elements_tag = None
    _instanceClass = None

    def __init__(self, instance_class=None, **opts):
        ObjectDeserializer.__init__(self, **opts)
        self._tag = opts.get('tag', self._tag)
        self._elements_tag = opts.get('elements_tag', self._elements_tag)
        instance_class = Symbol.convert(instance_class or self._instanceClass)
        self._instanceClass = instance_class
        if instance_class is not None:
            if not self._tag and not self._many:
                self._tag = underscore(instance_class.__name__)
            elif not self._elements_tag and self._many:
                self._elements_tag = underscore(instance_class.__name__)

    def _deserialize(self, value, many=False, deserialize_instances=True, with_tags=False, **opts):
        if with_tags:
            tag = opts.get('tag', self._tag)
            if tag in value:
                value =  value[tag]
                if many:
                    elements_tag = opts.get('elements_tag', self._elements_tag)
                    if elements_tag in value:
                        value = value[elements_tag]
        instance_class = opts.get('instance_class', self._instanceClass)
        if deserialize_instances:
            if instance_class:
                value = [instance_class._deserialize(instance_class, v, **opts) for v in value] if many\
                    else instance_class._deserialize(instance_class, value, **opts)
            else:
                value = ObjectDeserializer._deserialize(self, value, many=many, **opts)
        return value


class InstanceSerializer(ObjectSerializer, InstanceDeserializer):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/InstanceSerializer'

    def __init__(self, **opts):
        InstanceDeserializer.__init__(self, **opts)
        ObjectSerializer.__init__(self, **opts)

    def _serialize(self, value, many=False, with_tags=False, excludes=[], **opts):
        instance_class = opts.get('instance_class', self._instanceClass)
        if instance_class:
            excludes = list(instance_class._notSerialized.union(excludes))
            value = [instance_class._serialize(instance_class, v, excludes=excludes, **opts) for v in value] if many\
                else instance_class._serialize(instance_class, value, excludes=excludes, **opts)
        else:
            value = ObjectSerializer._serialize(self, value, many=many, excludes=excludes, **opts)
        if with_tags:
            tag = opts.get('tag', self._tag)
            elements_tag = opts.get('elements_tag', self._elements_tag)
            if many:
                value = {tag: {elements_tag: value}}
            else:
                value = {tag: value}
        return value


class EntityDeserializer(InstanceDeserializer):
    _useIdentityKeys = None
    _useEntityKeys = None

    def __init__(self, **opts):
        InstanceDeserializer.__init__(self, **opts)
        self._useIdentityKeys = opts.get('useIdentityKeys', self._useIdentityKeys)
        self._useEntityKeys = opts.get('useEntityKeys', self._useEntityKeys)


class EntitySerializer(InstanceSerializer, EntityDeserializer):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/EntitySerializer'

    def __init__(self, **opts):
        EntityDeserializer.__init__(self, **opts)
        InstanceSerializer.__init__(self, **opts)

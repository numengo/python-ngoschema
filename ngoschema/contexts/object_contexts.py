# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from ..protocols import with_metaclass, SchemaMetaclass, ObjectProtocol, TypeProtocol, value_opts
from .context import ContextMixin


class ContextMixin(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/contexts/$defs/ContextMixin'


class NsManagerMixin(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/contexts/$defs/NsManagerMixin'
    _ns_mgr = None

    def set_context(self, context=None, *extra_contexts):
        from ..managers.namespace_manager import NamespaceManager, default_ns_manager
        ContextMixin.set_context(self, context, *extra_contexts)
        self._ns_mgr = next((m for m in self._context.maps if isinstance(m, NamespaceManager)), default_ns_manager)
        self._set_data_validated('_nsMgr', self._ns_mgr)


class ObjectMixin(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/contexts/$defs/ObjectMixin'
    _parent = None
    _root = None

    def set_context(self, context=None, *extra_contexts):
        from ..models.metadata import NamedObject
        NsManagerMixin.set_context(self, context, *extra_contexts)
        ctx = self._context
        # _parent and _root are declared readonly in inspect.mm and it raises an error
        self._parent = next((m for m in ctx.maps if isinstance(m, ObjectProtocol) and m is not self), None)
        self._root = next((m for m in reversed(ctx.maps) if isinstance(m, ObjectProtocol) and m is not self), None)
        self._set_data_validated('_parentObject', self._parent)
        self._set_data_validated('_rootObject', self._root)


class ParentNamedMixin(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/contexts/$defs/ParentNamedMixin'
    _parent_named = None

    def set_context(self, context=None, *extra_contexts):
        from ..models.metadata import NamedObject
        ObjectMixin.set_context(self, context, *extra_contexts)
        self._parent_named = next((m for m in self._context.maps
                                   if isinstance(m, NamedObject) and m is not self), None)
        self._set_data_validated('_parentNamed', self._parent_named)


class ParentDefinitionMixin(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/contexts/$defs/ParentDefinitionMixin'
    _parent_def = None

    def set_context(self, context=None, *extra_contexts):
        from ..models.types.collections import Definition
        ParentNamedMixin.set_context(self, context, *extra_contexts)
        self._parent_def = next((m for m in self._context.maps
                                   if isinstance(m, Definition) and m is not self), None)
        self._set_data_validated('_parentDefinition', self._parent_def)

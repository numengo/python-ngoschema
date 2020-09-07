# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol, ArrayProtocol, TypeProtocol
from ...managers import NamespaceManager, default_ns_manager
from ...types import String as String_t, Boolean as Boolean_t, Object as Object_t
from ...decorators import memoized_property, depend_on_prop


class Uri(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/uri/$defs/Uri'


class Id(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/uri/$defs/Id'
    _lazy_loading = False

    def _check(self, value, **opts):
        if not ObjectProtocol._check(self, value, **opts):
            if String_t.check(value):
                return True  # $ref
            return False
        return True

    def set_context(self, context=None, *extra_contexts):
        ObjectProtocol.set_context(self, context, *extra_contexts)
        ctx = self._context
        self._ns_mgr = next((m for m in ctx.maps if isinstance(m, NamespaceManager)), None)
        self._ns_mgr = self._ns_mgr or default_ns_manager

    def set_ref(self, value):
        if value and '#' not in value:
            self._data['uri'] = value + '#'

    @depend_on_prop('uri')
    def get_canonicalName(self):
        ref = self._data_validated['uri']
        if ref:
            return self._ns_mgr.get_id_cname(ref) if getattr(self, '_ns_mgr') else None
        return getattr(self, 'name', None)

    @memoized_property
    def json_schema(self):
        return self.uri


class Path(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/uri/$defs/Path'


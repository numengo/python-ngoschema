# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .ns_manager_context import NsManagerContext


class ObjectProtocolContext(NsManagerContext):
    _parent = None

    def set_context(self, context, **opts):
        from ..protocols.object_protocol import ObjectProtocol
        NsManagerContext.set_context(self, context, **opts)
        ctx = self._context
        # _parent and _root are declared readonly in inspect.mm and it raises an error
        self._parent = next((m for m in ctx.maps if isinstance(m, ObjectProtocol) and m is not self), None)
        if '_parent' in self._properties:
            self._set_dataValidated('_parent', self._parent)

    @property
    def _root(self):
        return self._parent._root if self._parent else self


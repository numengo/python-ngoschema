# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from ..managers.namespace_manager import NamespaceManager, default_ns_manager
from ..protocols import Context


def find_ns_mgr(context):
    from ..managers.namespace_manager import NamespaceManager, default_ns_manager
    return next((m for m in context.maps if isinstance(m, NamespaceManager)), default_ns_manager)


class NsManagerContext(Context):
    _ns_mgr = None

    def set_context(self, context, **opts):
        Context.set_context(self, context, **opts)
        self._ns_mgr = find_ns_mgr(self._context)
        if '_nsMgr' in self._properties:
            self._set_dataValidated('_nsMgr', self._ns_mgr)

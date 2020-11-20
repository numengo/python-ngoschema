# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .instance_context import InstanceContext


class EntityContext(InstanceContext):
    _repository = None

    def set_context(self, context, **opts):
        from ..repositories import Repository
        InstanceContext.set_context(self, context, **opts)

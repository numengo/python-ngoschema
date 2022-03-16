# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .instance_context import InstanceContext


class EntityContext(InstanceContext):
    _repository = None

    def set_context(self, context, session, **opts):
        from ..repositories import Repository
        self._repository = session.get_or_create_repo_by_class(self.__class__)
        InstanceContext.set_context(self, context, **opts)

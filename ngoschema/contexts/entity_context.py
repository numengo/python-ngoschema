# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .instance_context import InstanceContext


class EntityContext(InstanceContext):
    _repository = None

    def set_context(self, context, session=None, **opts):
        from ..repositories import Repository
        from ..session import default_session
        session = session or context._session or default_session
        self._repository = session.get_or_create_repo_by_class(self.__class__)
        InstanceContext.set_context(self, context, **opts)

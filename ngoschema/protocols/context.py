# *- coding: utf-8 -*-
"""
Context for type evaluation

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import copy
from pathlib import Path
import datetime

from ngoschema.utils.utils import Context
from ngoschema import settings

from ..decorators import assert_arg

DEFAULT_CONTEXT = Context(settings.DEFAULT_CONTEXT, today=datetime.date.today())


class Context:
    _context = DEFAULT_CONTEXT

    def __init__(self, context=None, **opts):
        self._context = context or self._context

    def __call__(self, **opts):
        return self._create_context(self, **opts)

    @classmethod
    def create_context(cls, *parents, **opts):
        return cls._create_context(cls, *parents, **opts)

    @staticmethod
    def _create_context(self, *parents, context=None, **local):
        context = context or self._context
        # create a new today at every context creation, will update the DEFAULT_CONTEXT value
        ctx = context.create_child(*parents, today=datetime.date.today(), **local)
        ctx._session = getattr(context, '_session', None)
        return ctx

    def set_context(self, context, session=None, **opts):
        self._context = context
        self._context._session = session or self._context._session

    @property
    def session(self):
        return self._context._session

# *- coding: utf-8 -*-
"""
Context for type evaluation

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import copy

from ngoschema.utils.utils import Context
from ngoschema import settings

DEFAULT_CONTEXT = Context(**settings.DEFAULT_CONTEXT)


class Context:
    _context = DEFAULT_CONTEXT

    def __init__(self, context=None, **opts):
        self._context = context or self._context

    def __call__(self, **opts):
        return self._create_context(self, **opts)

    @classmethod
    def create_context(cls, **opts):
        return cls._create_context(cls, **opts)

    @staticmethod
    def _create_context(self, *parents, context=None, **local):
        context = context or self._context
        return context.create_child(*parents, **local)

    def set_context(self, *parents, **local):
        self._context = self._create_context(self, *parents, **local)

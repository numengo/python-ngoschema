# *- coding: utf-8 -*-
"""
Context for type evaluation

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import copy

from ..utils.utils import ReadOnlyChainMap
from .. import settings


class Context(ReadOnlyChainMap):

    def __init__(self, *parents, **local):
        self._local = local
        self._parents = parents
        ReadOnlyChainMap.__init__(self, local, *parents)

    def __enter__(self):
        return copy.deepcopy(self)

    def __exit__(self, type, value, traceback):
        pass

    def __repr__(self):
        return repr(list(self._maps))

    def create_child(self, *parents, **local):
        'Make a child context, inheriting enable_nonlocal unless specified'
        if not parents and not local:
            return self
        if local:
            parents = (local, ) + parents
        return Context(*parents, *self._maps)

    def prepend(self, mapping):
        self._maps.insert(0, mapping)

    def append(self, mapping):
        self._maps.append(mapping)

    def find_instance(self, cls, default=None, exclude=None, reverse=False):
        gen = (m for m in self.maps if isinstance(m, cls) and m is not exclude)
        if reverse:
            gen = reversed(gen)
        return next(gen, default)

    def find_file_repository(self):
        from ..protocols import CollectionProtocol
        from ..repositories import FileRepository
        for m in self.maps:
            if isinstance(m, CollectionProtocol):
                repo = getattr(m, '_repo')
                if isinstance(repo, FileRepository):
                    return repo

    def __hash__(self):
        return hash(repr(sorted(self.merged.items())))


DEFAULT_CONTEXT = Context(**settings.DEFAULT_CONTEXT)


class ContextMixin:
    _context = DEFAULT_CONTEXT

    def create_context(self, context=None, *extra_contexts):
        ctx = context if context is not None else self._context
        return ctx.create_child(*extra_contexts)

    def set_context(self, context=None, *extra_contexts):
        ctx = self.create_context(context, *extra_contexts)
        self._context = ctx


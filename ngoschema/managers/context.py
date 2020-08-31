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

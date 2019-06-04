# *- coding: utf-8 -*-
"""
Project definition and main actions

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from weakref import WeakValueDictionary

class HasCache:
    
    def __init__(self, *args, **kwargs):
        self._dirty = True
        self._inputs = WeakValueDictionary()
        self._outputs = WeakValueDictionary()
    
    def _set_inputs(self, **deps):
        self._inputs = WeakValueDictionary(deps)

    def _add_inputs(self, **deps):
        self._inputs.update(deps)

    def _set_outputs(self, **deps):
        self._outputs = WeakValueDictionary(**deps)

    def _add_outputs(self, **deps):
        self._outputs.update(**deps)

    def is_dirty(self):
        return self._dirty or any((d().is_dirty() for d in self._inputs.valuerefs() if d()))

    def set_clean(self, recursive=False):
        self._dirty = False
        #if recursive:
        #    for o in self._outputs:
        #        o.set_clean()
    
    def touch(self, recursive=False):
        if not self._dirty:
            self._dirty = True
            if recursive:
                for d in self._outputs.valuerefs():
                    if d():
                        d().touch()

    def validate_if_dirty(self, recursive=True):
        try:
            if recursive:
                for d in self._inputs.valuerefs():
                    _d = d()
                    if _d:
                        _d.validate_if_dirty(recursive)
            if self._dirty:
                from .wrapper_types import ArrayWrapper
                if not isinstance(self, ArrayWrapper):
                    self.set_clean()
                try:
                    self.validate()
                except Exception as er:
                    raise er
            self.set_clean()
        except Exception as er:
            raise er

    def force_validate(self, recursive=True):
        if recursive:
            for d in self._inputs.valuerefs():
                _d = d()
                if _d:
                    _d.force_validate(recursive)
        self.validate()
        self.set_clean()

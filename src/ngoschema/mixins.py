# *- coding: utf-8 -*-
"""
Project definition and main actions

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals
import logging

from . import utils
from weakref import WeakValueDictionary

class HasCache:
    _inputs = WeakValueDictionary()
    _outputs = WeakValueDictionary()
    
    def __init__(self, *args, **kwargs):
        self._dirty = True
    
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


class HasLogger:
    logger = None

    @classmethod
    def init_class_logger(cls):
        cls.logger = logging.getLogger(utils.fullname(cls))
        #cls.logger.level = cls.logger.parent.level
        #cls.logger.handlers = cls.logger.parent.handlers
        #cls.logger.propagate = True

    @classmethod
    def set_logLevel(cls, logLevel):
        level = logging.getLevelName(logLevel)
        cls.logger.setLevel(level)

class HasShortRepr:
    _short_repr_ = True

    def __repr__(self):
        if not self._short_repr_:
            return super().__repr__(self)
        repr = self.__class__.__name__
        return "<%s id=%i>" % (repr, id(self))

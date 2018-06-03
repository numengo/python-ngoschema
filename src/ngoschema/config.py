# *- coding: utf-8 -*-
"""
Utilities for config files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
import logging
from dpath.util import merge
from backports import configparser2
import copy
from builtins import object
from builtins import str

from .deserializers import Deserializer

_ = gettext.gettext

class ConfigParser(Deserializer):
    logger = logging.getLogger(__name__)

    def loads(self, stream, **kwargs):
        config = configparser2.ConfigParser()
        config.readfp(stream)
        return config

class ConfigManager(object):
    _instance = None
    _registry = {}
    _sections = {}

    def __new__(cls, *args, **kwargs):
        if self._instance is None:
            self._instance = super(ConfigManager, cls).__new__(cls, *args,
                                                               **kwargs)
        return self._instance

    def add_config(self, configFilepath):
        cfg = ConfigParser.load(configFilePath)
        self._registry[str(configFilepath)] = cfg

        for name, options in dict(cfg._sections).items():
            section = self._sections if name in self._sections else {}
            new_section = copy.copy(cfg._defaults)
            merge(new_section,section)
            merge(new_section,options)
            self._sections[name] = new_section

    def section(self, name):
        return pmap(self._sections[name])

    def get_defaults(self, sname, keys):
        sname = sname.lower()
        if sname in self._sections:
            section = self._sections[sname]
            return { k: section[v.lower()] for k in keys if k.lower() in section}
        return {}

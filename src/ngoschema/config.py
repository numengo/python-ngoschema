# *- coding: utf-8 -*-
"""
Utilities for config files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import logging
from dpath.util import merge
from backports import configparser2
from pyrsistent import pmap
import copy
from builtins import object
from builtins import str

from .deserializers import Deserializer
from .str_utils import CaseInsensitiveDict

_ = gettext.gettext


class ConfigParser(Deserializer):
    logger = logging.getLogger(__name__)

    def loads(self, stream, **kwargs):
        config = configparser2.ConfigParser()
        config.read_string(stream)
        return config


class ConfigLoader(object):
    """
    Object to deal with multiple config files and merge them.

    Singleton mode allow to have one instance shared among all objects.
    When requesting a section, user retrieves a merged version of all section of
    same name in the different loaded files, including DEFAULT section, and
    inherited sections (using : as a separator between subsections).

    The returned dictionary is case insensitive. User can use get_defaults
    and provide a set of keys (with proper casing), it will return the
    corresponding dictionary with keys properly cased.
    """

    _instance = None
    _registry = {}
    _sections = {}

    def __new__(cls, *args, **kwargs):
        singleton = kwargs.pop("singleton", False)
        if not singleton:
            instance = super(ConfigLoader, cls).__new__(cls)
            instance._registry = {}
            instance._sections = {}
            return instance
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        """
        User can supply a list of config files to merge
        """
        for f in args:
            self.add_config(f)

    def add_config(self, configFilepath):
        """
        Add a config file to registry
        """
        cfg = ConfigParser().load(configFilepath)
        self._registry[str(configFilepath)] = cfg

        for name, options in dict(cfg._sections).items():
            section = self._sections if name in self._sections else {}
            new_section = copy.copy(cfg._defaults)
            merge(new_section, section)
            merge(new_section, options)
            self._sections[name] = new_section

    def _section(self, name):
        parents = name.split(":")
        name = parents.pop(0)
        cfg = copy.copy(self._sections.get(name, {}))
        while parents:
            name += ":" + parents.pop(0)
            cfg.update(self._sections.get(name, {}))
        return CaseInsensitiveDict(cfg)

    def section(self, name):
        """
        Retrieve a section as a case insensitive dictionary, merging defaults
        and inherited sections.
        """
        return self._section(name)

    def get_values(self, sname, keys):
        """
        Method to retrieve the values in found in the given section of config
        files for the given set of keys

        :rtype: dict
        """
        section = self._section(sname)
        return {k: section[k] for k in keys if k in section}

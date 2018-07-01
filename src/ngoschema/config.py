# *- coding: utf-8 -*-
"""
Utilities for config files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import copy
import gettext
import logging
import appdirs
import pathlib
import six

from builtins import object
from builtins import str

from backports import configparser2
from dpath.util import merge
from ngofile.pathlist import PathList

from .deserializers import Deserializer
from .str_utils import CaseInsensitiveDict

_ = gettext.gettext


def search_app_config_files(appname=None, appauthor=None, version=None):
    pl = PathList()
    cdirs = (appdirs.user_config_dir(appname, appauthor, version),
             appdirs.site_config_dir(appname, appauthor, version))
    for cdir in cdirs:
        if pathlib.Path(cdir).exists():
            pl.add(cdir)
    return list(pl.list_files(['*.cfg', '*.ini']))


class ConfigParser(Deserializer):
    logger = logging.getLogger(__name__)

    def loads(self, stream, **kwargs):
        config = configparser2.ConfigParser()
        config.read_string(stream)
        return config


class ConfigLoader(object):
    """
    Object to deal with multiple config files and merge them.

    When requesting a section, user retrieves a merged version of all section of
    same name in the different loaded files, including DEFAULT section, and
    inherited sections (using : as a separator between subsections).

    The returned dictionary is case insensitive. User can use get_defaults
    and provide a set of keys (with proper casing), it will return the
    corresponding dictionary with keys properly cased.
    """

    def __init__(self, *args, **kwargs):
        """
        User can supply a list of config files to merge
        """
        self._registry = {}
        self._sections = {}
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

    def __iter__(self):
        return six.iterkeys(self._sections)
    
    def __getitem__(self, key):
        try:
            return self.section(key)
        except AttributeError:
            raise KeyError(key)

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

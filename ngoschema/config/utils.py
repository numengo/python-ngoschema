# *- coding: utf-8 -*-
"""
Utilities for config files

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import copy
import logging, logging.config
import pathlib

from ruamel.yaml import YAML
import appdirs

from ngofile.pathlist import PathList

from ngoschema.types import PathFileExists
from ngoschema.decorators import assert_arg


def search_app_config_files(appname=None, appauthor=None, version=None):
    pl = PathList()
    cdirs = (appdirs.user_config_dir(appname, appauthor, version),
             appdirs.site_config_dir(appname, appauthor, version))
    for cdir in cdirs:
        if pathlib.Path(cdir).exists():
            pl.add(cdir)
    return pl.list_files(['*.cfg', '*.json', '*.yaml'])


@assert_arg(0, PathFileExists)
def load_log_config(filepath):
    from . import settings
    yaml = YAML(typ="safe")
    cfg = copy.deepcopy(settings.LOGGING)
    with filepath.open('r') as f:
        cfg2 = yaml.load(f.read())
    cfg.update(cfg2)
    logging.config.dictConfig(cfg)
    return cfg


def load_default_app_config(app_name, app_author=None):
    from simple_settings import LazySettings
    settings_list = [str(p.resolve()) for p in search_app_config_files(app_name, app_author)]\
                  + ['%s_.environ' % app_name.upper()]
    settings = LazySettings(*settings_list)
    return settings.as_dict()


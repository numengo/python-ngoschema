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

from ngoschema.decorators import assert_arg, SCH_PATH_FILE_EXISTS


def search_app_config_files(appname=None, appauthor=None, version=None):
    pl = PathList()
    cdirs = (appdirs.user_config_dir(appname, appauthor, version),
             appdirs.site_config_dir(appname, appauthor, version))
    for cdir in cdirs:
        if pathlib.Path(cdir).exists():
            pl.add(cdir)
    return pl.list_files(['*.cfg', '*.ini'])


@assert_arg(0, SCH_PATH_FILE_EXISTS)
def load_log_config(filepath):
    from . import settings
    yaml = YAML(typ="safe")
    cfg = copy.deepcopy(settings.LOGGING)
    with filepath.open('r') as f:
        cfg2 = yaml.load(f.read())
    cfg.update(cfg2)
    logging.config.dictConfig(cfg)
    return cfg



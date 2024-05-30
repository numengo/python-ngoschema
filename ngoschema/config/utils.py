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
import codecs
import json

from ruamel.yaml import YAML
import appdirs
from simple_settings import LazySettings as SimpleLazySettings

from ngofile.pathlist import PathList

from ngoschema.datatypes import PathFileExists
from ngoschema.decorators import assert_arg


def search_app_config_files(appname=None, appauthor=None, version=None):
    pl = PathList()
    cdirs = (appdirs.user_config_dir(appname, appauthor, version),
             appdirs.site_config_dir(appname, appauthor, version))
    for cdir in cdirs:
        if pathlib.Path(cdir).exists():
            pl.add(cdir)
    return [str(f.resolve()) for f in pl.list_files(['*.cfg', '*.json', '*.yaml'])]


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
    settings_list = [p for p in search_app_config_files(app_name, app_author)]\
                  + ['%s_.environ' % app_name.upper()]
    settings = LazySettings(*settings_list)
    return settings.as_dict()


class SettingsLoadStrategyPythonSecrets:
    """
    This is the strategy used to read secret settings from a secrets.json file managed by python-secrets
    """
    name = 'python_secrets'

    @staticmethod
    def is_valid_file(file_name):
        return file_name == 'python_secrets'

    @staticmethod
    def load_settings_file(settings_file):
        from psec.secrets_environment import SecretsEnvironment
        e = SecretsEnvironment()
        if e.secrets_file_path_exists():
            e.read_secrets_and_descriptions()
            return dict(e.items())


class LazySettings(SimpleLazySettings):
    """LazySettings extension allowing to update or merge other settings """

    def __init__(self, *settings_list):
        SimpleLazySettings.__init__(self, *settings_list)

    def update(self, *other_settings):
        # other_settings List[SimpleLazySettings]
        as_dict = self.as_dict()
        keys = set(as_dict.keys())
        for other_setting in other_settings:
            other_as_dict = other_setting.as_dict()
            other_update = {k: as_dict[k] for k in keys.intersection(other_as_dict.keys())}
            other_setting.configure(**other_update)

    def merge(self, *other_settings, only_keys=True):
        # other_settings List[SimpleLazySettings]
        as_dict = self.as_dict()
        keys = set(as_dict.keys())
        for other_setting in other_settings:
            other_as_dict = other_setting.as_dict()
            if only_keys:
                merge = {k: other_as_dict[k] for k in keys.intersection(other_as_dict.keys())}
            else:
                merge = other_as_dict
            self.configure(**other_update)

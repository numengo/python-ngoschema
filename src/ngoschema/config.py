# *- coding: utf-8 -*-
""" utilities, prototypes and classes of parsers

_schemas.py - created on 02/01/2018
author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
import logging
from builtins import object
from builtins import str

import configparser2
from appdirs import site_config_dir
from appdirs import user_config_dir
from past.builtins import basestring

from .string_utils import CaseInsensitiveDict
from ._de_serializer import De_Serializer
from ._schemas import ObjectManager

_ = gettext.gettext


class ConfigParser(De_Serializer):
    logger = logging.getLogger(__name__)
    extensions = ['.ini', '.cfg']

    def loads(self, stream, **kwargs):
        config = configparser2.ConfigParser()
        config.readfp(stream)
        return config

    def dumps(self, data, **opts):
        pass


class ConfigManager(ObjectManager):
    extensions = ['.ini', '.cfg']
    parsers = [ConfigParser]
    recursive = False

    def __init__(self, *args, **kwargs):
        pl = [
            '.',
            # os.path.expanduser('~'),
            user_config_dir('config', 'numengo'),
            site_config_dir('config', 'numengo')
        ]
        pl = [p for p in pl if p.exists()]
        pl = kwargs.get('pathlist', None) or pl

        ObjectManager.__init__(self,
                              objectClass= configparser2.ConfigParser,
                              pathlist=pl,
                              **kwargs)

        if not self.loaded:
            self.update_from_files()

    @staticmethod
    def _to_ci_dict(dict):
        return CaseInsensitiveDict({k: v for k, v in dict.items()}

    def defaults(self):
        ret = {}
        for id, cfg in self.items():
            ret.update(cfg._defaults)
        return self._to_ci_dict(ret)

    def config(self, cfg_name):
        ret = {}
        for cfg in self.configFiles(cfg_name):
            ret.update(cfg[cfg_name])
        return self._to_ci_dict(ret)

    def configFiles(self, cfg_name):
        ret = []
        for id, cfg in list(self.items()):
            if cfg_name in cfg:
                ret.append(cfg)
        return ret

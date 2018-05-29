# *- coding: utf-8 -*-
"""
Json de/serializer wrapper using standard json library

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
from ruamel.yaml import YAML
import logging
from builtins import object
from builtins import str

from ._de_serializer import De_Serializer

_ = gettext.gettext

class Yaml(De_Serializer):
    logger = logging.getLogger(__name__)
    extensions = ['.yaml', '.yml', '.ngoy']

    def __init__(self, **kwargs):
        # default, if not specfied, is 'rt' (round-trip)
        self._yaml = YAML(typ='safe', **kwargs)

    def loads(self, stream, **opts):
        data = self._yaml.load(stream, **opts)
        return data

    def dumps(self, data, **opts):
        self._yaml.dumps(data, **opts)


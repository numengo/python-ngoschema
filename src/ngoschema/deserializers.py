# *- coding: utf-8 -*-
"""
de/serializer meta class

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
import logging
import io
import json
from ruamel.yaml import YAML
from abc import ABCMeta
from builtins import object
from builtins import str

from future.utils import with_metaclass, abstractmethod

from .utils import is_sequence, is_mapping, GenericRegistry

_ = gettext.gettext

class Deserializer(with_metaclass(ABCMeta)):
    objectClass = None
    logger = logging.getLogger(__name__)

    def load(self, path, **opts):
        """
        Deserialize a file like object and returns the object

        :param path: file path containing the object
        :type path: path
        :param opts: can be 'protocol' (default is 'r')
        """
        ptcl = opts.get('protocol', 'r')
        enc = opts.get('encoding', 'utf-8')
        if objectClass:
            self.logger.info(_('LOAD %r from file %s' % (self.objectClass, path)))
        else:
            self.logger.info(_('LOAD content from file %s' % (path)))
        return self.loads(codecs.open(str(path), ptcl, enc), opts)

    @abstractmethod
    def loads(self, stream, **opts):
        """
        Deserialize a string and returns the object

        :param stream: data stream
        :type stream: string
        :param opts: can be 'protocol' (default is 'r')
        """
        pass

deserializer_registry = utils.GenericRegistry()

@deserializer_registry.register()
class JsonDeserializer(Deserializer):
    logger = logging.getLogger(__name__+'.JsonDeserializer')

    def loads(self, stream, **opts):
        data = json.load(stream, **opts)
        data  = utils.process_collection(data, **opts)
        return data

@deserializer_registry.register()
class YamlDeserializer(Deserializer):
    logger = logging.getLogger(__name__+'.YamlDeserializer')

    def __init__(self, **kwargs):
        # default, if not specfied, is 'rt' (round-trip)
        self._yaml = YAML(typ='safe', **kwargs)

    def loads(self, stream, **opts):
        data = self._yaml.load(stream, **opts)
        data  = utils.process_collection(data, **opts)
        return data



# *- coding: utf-8 -*-
"""
de/serializer meta class

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
import logging
import json
import codecs
import sys
from ruamel.yaml import YAML
from abc import ABCMeta
from abc import abstractmethod
from builtins import object
from builtins import str

from future.utils import with_metaclass

from . import utils
from .utils import process_collection, GenericRegistry
from . import decorators
from . import validators

_ = gettext.gettext

class Deserializer(with_metaclass(ABCMeta)):
    objectClass = None
    logger = logging.getLogger(__name__)

    @decorators.log_exceptions
    @decorators.assert_arg(1, validators.SCH_PATH_FILE)
    def load(self, path, **opts):
        """
        Deserialize a file like object and returns the object

        :param path: file path containing the object
        :type path: path
        :param opts: dictionary of options, as protocol(=r) , encoding=(utf-8), objectClass=None
        """
        ptcl = opts.get('protocol', 'r')
        enc = opts.get('encoding', 'utf-8')
        self.logger.info(_('LOAD from file %s' % (path)))
        #with codecs.open(str(path), ptcl, enc) as f:
        #    return self.loads(f, **opts)
        with codecs.open(str(path), ptcl, enc) as f:
            try:
                return self.loads(f.read(), **opts)
            except Exception as er:
               type, value, traceback = sys.exc_info()
               raise IOError, "Problem occured loading file %s.\n%s" % (path,
                         value), sys.exc_info()[2]

    @abstractmethod
    def loads(self, stream, **opts):
        """
        Deserialize a string and returns the object

        :param stream: data stream
        :type stream: string
        :param opts: dictionary of options, as protocol(=r) , encoding=(utf-8), objectClass=None
        """
        pass

deserializer_registry = utils.GenericRegistry()

@deserializer_registry.register()
class JsonDeserializer(Deserializer):
    logger = logging.getLogger(__name__+'.JsonDeserializer')

    def loads(self, stream, **opts):
        data = json.loads(stream
                         #,encoding=opts.get('encoding', 'utf-8')
                         )
        data  = utils.process_collection(data, **opts)
        return data

@deserializer_registry.register()
class YamlDeserializer(Deserializer):
    logger = logging.getLogger(__name__+'.YamlDeserializer')

    def __init__(self, **kwargs):
        # default, if not specfied, is 'rt' (round-trip)
        self._yaml = YAML(typ='safe', **kwargs)

    def loads(self, stream, **opts):
        data = self._yaml.load(stream)
        assert len(data.values())==1, "format not handled"
        data = list(data.values())[0]
        data  = utils.process_collection(data, **opts)
        return data



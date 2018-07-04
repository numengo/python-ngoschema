# *- coding: utf-8 -*-
"""
de/serializer meta class

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import gettext
import json
import logging
import sys
from abc import ABCMeta
from abc import abstractmethod
from builtins import str

from future.utils import with_metaclass
from ruamel.yaml import YAML
from six import reraise as raise_

from . import decorators
from . import utils

_ = gettext.gettext


class Deserializer(with_metaclass(ABCMeta)):
    logger = logging.getLogger(__name__)

    #@decorators.assert_arg(1, decorators.SCH_PATH_FILE)
    @classmethod
    def load(self, path, only=(), but=(), many=False, **opts):
        """
        Deserialize a file like object and returns the object

        :param path: file path containing the object
        :type path: path
        :param only: only keys to keep
        :param but: keys to exclude
        :param many: process collection as a list/sequence. if collection is
        a dictionary and many=True, values are processed
        :param opts: dictionary of options, as protocol(=r) , encoding=(utf-8), object_class=None
        """
        ptcl = opts.get("protocol", "r")
        enc = opts.get("encoding", "utf-8")

        # with codecs.open(str(path), ptcl, enc) as f:
        #    return self.loads(f, **opts)
        with codecs.open(str(path.resolve()), ptcl, enc) as f:
            try:
                obj = self.loads(f.read(), only=only, but=but, many=many, **opts)
                self.logger.info(_("LOAD file %s" % (path)))
                self.logger.debug(_("data:\n%r " % (obj)))
                return obj
            except Exception as er:
                type, value, traceback = sys.exc_info()
                msg = "Problem occured loading file %s.\n%s" % (path, value)
                raise_(IOError, msg, traceback)

    @abstractmethod
    def loads(self, string, only=(), but=(), many=False, **opts):
        """
        Deserialize a string and returns the object
        IMPORTANT: this is class method, override it with @classmethod!

        :param string: data string
        :type string: string
        :param only: only keys to keep
        :param but: keys to exclude
        :param many: process collection as a list/sequence. if collection is
        a dictionary and many=True, values are processed
        :param opts: dictionary of options, as protocol(=r) , encoding=(utf-8), object_class=None
        """


deserializer_registry = utils.GenericRegistry()


@deserializer_registry.register()
class JsonDeserializer(Deserializer):
    logger = logging.getLogger(__name__ + ".JsonDeserializer")

    @classmethod
    def loads(self, string, only=(), but=(), many=False, **opts):
        __doc__ = Deserializer.loads.__doc__
        data = json.loads(string
                          # ,encoding=opts.get('encoding', 'utf-8')
                          )
        data = utils.process_collection(data, only, but, many, **opts)
        return data


@deserializer_registry.register()
class YamlDeserializer(Deserializer):
    logger = logging.getLogger(__name__ + ".YamlDeserializer")
    _yaml = YAML(typ="safe")

    @classmethod
    def loads(self, string, only=(), but=(), many=False, **opts):
        __doc__ = Deserializer.loads.__doc__
        data = self._yaml.load(string)
        data = utils.process_collection(data, only, but, many, **opts)
        return data

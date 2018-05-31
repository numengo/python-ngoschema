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
import six
from abc import ABCMeta
from builtins import object
from builtins import str

from future.utils import with_metaclass, abstractmethod

from . import utils
import is_sequence, is_mapping, GenericRegistry

_ = gettext.gettext


class Serializer(with_metaclass(ABCMeta)):
    objectClass = None
    logger = logging.getLogger(__name__)

    def dump(self, obj, path, overwrite=False, **opts):
        """
        Serialize an object to a file like object string

        :param obj: object to serialize
        :param path: file path containing the object
        :type path: path
        :param overwrite: overwrites existing file
        :param opts: dictionary of option, as protocol(=w) , encoding=(utf-8)
        """
        ptcl = opts.get('protocol', 'w')
        enc = opts.get('encoding', 'utf-8')

        self.logger.info(_('DUMP %r to file %s' % (data, path)))

        if path.exists() and not overwrite:
            raise IOError(_('file %s already exists' % str(path)))
        with io.open(str(path), ptcl, encoding=enc) as outfile:
            stream = self.dumps(data, **opts)
            stream = six.text_type(stream)
            outfile.write(stream)

    @abstractmethod
    def dumps(self, obj, **opts):
        """
        Serialize an object to a string

        :param obj: object to serialize
        :param opts: dictionary of options, as protocol(=w) , encoding=(utf-8), objectClass=None
        """
        pass


serializer_registry = utils.GenericRegistry()

@serializer_registry.register()
class JsonSerializer(Serializer):
    logger = logging.getLogger(__name__+'.JsonDeserializer')

    def dumps(self, obj, **opts):
        data = obj.as_dict() if hasattr(obj,'has_dict') else obj
        data  = utils.process_collection(data, **opts)
        return json.dumps(data, **opts)


@serializer_registry.register()
class YamlSerializer(Serializer):
    logger = logging.getLogger(__name__+'.YamlDeserializer')

    def __init__(self, **kwargs):
        # default, if not specfied, is 'rt' (round-trip)
        self._yaml = YAML(typ='safe', **kwargs)

    def dumps(self, obj, **opts):
        data = obj.as_dict() if hasattr(obj,'has_dict') else obj
        data  = utils.process_collection(data, **opts)
        return self._yaml.dumps(data, **opts)

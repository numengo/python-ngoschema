# *- coding: utf-8 -*-
"""
de/serializer meta class

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import io
import json
import logging
from abc import ABCMeta
from abc import abstractmethod
from builtins import str

import six
from future.utils import with_metaclass
from ruamel import yaml
from ruamel.yaml import YAML

from . import decorators
from . import utils

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

_ = gettext.gettext


class Serializer(with_metaclass(ABCMeta)):
    logger = logging.getLogger(__name__)

    def dump(self, obj, path, only=(), but=(), many=False, overwrite=False, **opts):
        """
        Serialize an object to a file like object string

        :param obj: object(s) to serialize
        :param path: file path containing the object
        :type path: path
        :param only: only keys to keep
        :param but: keys to exclude
        :param many: process collection as a list/sequence. if collection is
        :param overwrite: overwrites existing file
        :param opts: dictionary of option, as protocol(=w) , encoding=(utf-8)
        """
        ptcl = opts.get("protocol", "w")
        enc = opts.get("encoding", "utf-8")

        self.logger.info(_("DUMP file %s" % (path)))
        self.logger.debug(_("data:\n%r " % (obj)))

        if path.exists() and not overwrite:
            raise IOError(_("file %s already exists" % str(path)))
        with io.open(str(path), ptcl, encoding=enc) as outfile:
            stream = self.dumps(obj, **opts)
            stream = six.text_type(stream)
            outfile.write(stream)

    @abstractmethod
    def dumps(self, obj, only=(), but=(), many=False, **opts):
        """
        Serialize an object to a string

        :param obj: object(s) to serialize
        :param only: only keys to keep
        :param but: keys to exclude
        :param many: process collection as a list/sequence. if collection is
        :param opts: dictionary of options, as protocol(=w) , encoding=(utf-8), object_class=None
        """


serializer_registry = utils.GenericRegistry()


@serializer_registry.register()
class JsonSerializer(Serializer):
    """
    Default settings for dumping are:
    indent: 2
    ensure_ascii: False
    """

    logger = logging.getLogger(__name__ + ".JsonDeserializer")

    def dumps(self, obj, only=(), but=(), many=False, **opts):
        __doc__ = Serializer.dumps.__doc__

        if many:
            datas = list(obj) if utils.is_sequence(obj) else obj.values()
            datas = [d.as_dict() if hasattr(d, "as_dict") else d for d in datas]
            data = [utils.process_collection(d, only, but, **opts) for d in datas]
        else:
            data = obj.as_dict() if hasattr(obj, "as_dict") else obj
            data = utils.process_collection(data, only, but, **opts)

        return json.dumps(
            data,
            indent=opts.get("indent", 2),
            ensure_ascii=opts.get("ensure_ascii", False),
            separators=opts.get("separators", None),
            # encoding=opts.get('encoding','utf-8'),
            default=opts.get("default", None),
        )


@serializer_registry.register()
class YamlSerializer(Serializer):
    logger = logging.getLogger(__name__ + ".YamlDeserializer")

    def __init__(self, **kwargs):
        # default, if not specfied, is 'rt' (round-trip)
        self._yaml = YAML(typ="safe", **kwargs)
        self._yaml = yaml

    def dumps(self, obj, only=(), but=(), many=False, **opts):
        __doc__ = Serializer.dumps.__doc__

        if many:
            datas = list(obj) if utils.is_sequence(obj) else obj.values()
            datas = [d.as_dict() if hasattr(d, "as_dict") else d for d in datas]
            data = [utils.process_collection(d, only, but, **opts) for d in datas]
        else:
            data = obj.as_dict() if hasattr(obj, "as_dict") else obj
            data = utils.process_collection(data, only, but, **opts)

        self._yaml.indent = opts.get("indent", 2)
        self._yaml.allow_unicode = opts.get("encoding", "utf-8") == "utf-8"

        output = StringIO()
        self._yaml.safe_dump(data, output, default_flow_style=False)
        return output.getvalue()

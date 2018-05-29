# *- coding: utf-8 -*-
"""
de/serializer meta class

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
import logging
import copy
import io
from abc import ABCMeta
from builtins import object
from builtins import str

from future.utils import with_metaclass, abstractmethod

from .utils import is_sequence, is_mapping

_ = gettext.gettext

class De_Serializer(with_metaclass(ABCMeta)):
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
        data = self.loads(codecs.open(str(path), ptcl, enc))
        self.logger.info(_('loads from file %s object %r' % (path, data)))
        return data

    @abstractmethod
    def loads(self, stream, **opts):
        """
        Deserialize a string and returns the object

        :param stream: data stream
        :type stream: string
        :param opts: can be 'protocol' (default is 'r')
        """
        pass

    def dump(self, obj, path, overwrite=True, **opts):
        """
        Serialize an object to a file like object string

        :param obj: object to serialize
        :param path: file path containing the object
        :type path: path
        :param overwrite: overwrites existing file
        :param opts: can be 'fields' to only extract certain fields, or 'protocol' (default is 'w')
        """
        ptcl = opts.get('protocol', 'w')
        enc = opts.get('encoding', 'utf-8')
        fields = set(opts.pop('fields', []))
        data = obj
        if fields:
            data = copy.deepcopy(obj)
            def delete_fields_not_of(container, fields):
                if is_mapping(container):
                    to_del = fields.difference(set(container.keys()))
                    left = fields.intersection(set(container.keys()))
                    for k in to_del:
                        del container[k]
                    for k in left:
                        delete_fields_not_of(container[k], fields)
                elif is_sequence(container):
                    for k in container:
                        delete_fields_not_of(k, fields)
            delete_fields_not_of(data, fields)

        self.logger.info(_('dumps to file %s object %r' % (path, data)))

        if path.exists() and not overwrite:
            raise IOError(_('file %s already exists' % str(path)))
        with io.open(str(path), ptcl, encoding=enc) as outfile:
            stream = self.dumps(data, **opts)
            # convert to unicode
            if is_basestring(stream):
                stream = str(stream)
            outfile.write(stream)

    @abstractmethod
    def dumps(self, obj, **opts):
        """
        Serialize an object to a string

        :param obj: object to serialize
        :param opts: can be 'fields' to only extract certain fields, or 'protocol' (default is 'w')
        """
        pass



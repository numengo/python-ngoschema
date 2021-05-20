# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import collections

import six
import os
import codecs
import logging

from ..decorators import assert_arg
from ..utils import file_link_format
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ..registries import serializers_registry
from ..models.files import File
from ..protocols.file_loader import FileSaver


@serializers_registry.register('file')
class FileSerializer(with_metaclass(SchemaMetaclass, FileSaver)):
    _id = 'https://numengo.org/ngoschema#/$defs/serializers/$defs/FileSerializer'

    def __init__(self, **opts):
        FileSaver.__init__(self, **opts)

    def set_filepath(self, filepath):
        return FileSaver.set_filepath(self, filepath)

    #@staticmethod
    #def _write_file(self, value, filepath, **opts):
    #    overwrite = self.overwrite
    #    if filepath.exists() and not overwrite:
    #        self._logger.info("File '%s' already exists. Not overwriting.", file_link_format(filepath))
    #    return FileSaver._write_file(self, value, filepath, **opts)

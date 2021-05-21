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
from ..types.uri import Path, PathFile, PathFileExists
from .serializer import Serializer
from .loader import Loader, Saver

#logger = logging.getLogger(__name__)


class FileLoader(Loader):
    _logger = logging.getLogger(__name__)
    _encoder = Serializer
    _filepath = None
    _binary = False
    _charset = 'utf-8'

    def __init__(self, encoder=None, filepath=None, binary=False, charset='utf-8', **opts):
        Loader.__init__(self, **opts)
        self._encoder = encoder or self._encoder
        self._encoder.__init__(self, **opts)
        self.set_filepath(filepath)
        self._binary = binary
        self._charset = charset

    def set_filepath(self, filepath):
        self._filepath = filepath = PathFileExists.convert(filepath, resolve=True) if filepath else None
        return filepath

    @staticmethod
    def _open_file(self, filepath, mode='r', **opts):
        filepath = FileLoader.set_filepath(self, filepath)
        charset = opts.get('charset', self._charset)
        binary = opts.get('binary', self._binary)
        fp = str(filepath)
        if binary:
            return open(fp, mode=mode)
        return codecs.open(fp, mode, charset)

    @staticmethod
    def _read_file(self, filepath, **opts):
        binary = opts.get('binary', self._binary)
        mode = 'rb' if binary else 'r'
        with FileLoader._open_file(self, filepath, mode=mode, **opts) as f:
            return f.read()

    @staticmethod
    def _deserialize(self, filepath, **opts):
        #filepath = opts.get('filepath', self._filepath)
        return self._read_file(self, filepath, **opts)
        #return Serializer._deserialize(self, read, **opts)

    @staticmethod
    def _load_file(self, filepath, **opts):
        filepath = FileLoader.set_filepath(self, filepath)
        content = FileLoader._deserialize(self, filepath, **opts)
        parsed = self._encoder.deserialize(content, evaluate=False, **opts)
        return Loader._load(self, parsed, **opts)

    @staticmethod
    def _load(self, filepath=None, **opts):
        filepath = filepath or self._filepath
        return self._load_file(self, filepath, **opts)

    #@classmethod
    def open_file(self, filepath, **opts):
        return self._open_file(self, filepath, **opts)

    #@classmethod
    def read_file(self, filepath, **opts):
        return self._read_file(self, filepath, **opts)

    #@classmethod
    def load_file(self, filepath, **opts):
        return self._load_file(self, filepath, **opts)

    def load(self, filepath=None, **opts):
        filepath = filepath or self.filepath
        return FileLoader._load(self, filepath, **opts)


class FileSaver(Saver, FileLoader):
    _loader = FileLoader
    _append = False
    _checkContent = True

    def __init__(self, append=False, **opts):
        Saver.__init__(self, **opts)
        FileLoader.__init__(self, **opts)
        self._append = append

    #def set_filepath(self, filepath):
    #    self._filepath = filepath = Path.convert(filepath) if filepath else None
    #    return filepath

    @staticmethod
    @assert_arg(2, Path)
    def _write_file(self, value, filepath, **opts):
        filepath = FileLoader.set_filepath(self, filepath)
        binary = opts.pop('binary', self._binary)
        mode = 'wb' if binary else 'w'
        if not filepath.parent.exists():
            self._logger.info("creating missing directory '%s'", file_link_format(filepath.parent))
            os.makedirs(str(filepath.parent))
        if filepath.exists():
            content = self.read_file(filepath)
            if value == content:
                self._logger.info("File '%s' already exists with same content. Not overwriting.", file_link_format(filepath))
                return value
        with self._open_file(self, filepath, mode=mode, **opts) as f:
            return f.write(value)

    @staticmethod
    @assert_arg(2, PathFileExists)
    def _append_file(self, value, filepath, **opts):
        filepath = FileLoader.set_filepath(self, filepath)
        binary = opts.pop('binary', self._binary)
        mode = 'ab' if binary else 'a'
        with self._open_file(self, filepath, mode=mode, **opts) as f:
            return f.write(value)

    @staticmethod
    @assert_arg(2, Path)
    def _save_file(self, value, filepath, **opts):
        filepath = FileLoader.set_filepath(self, filepath)
        value = Saver._save(self, value, **opts)
        append = opts.pop('append', self._append)
        if append:
            FileSaver._append_file(self, value, filepath, **opts)
        else:
            FileSaver._write_file(self, value, filepath, **opts)
        return value

    @staticmethod
    def _save(self, value, filepath=None, **opts):
        filepath = filepath or self._filepath
        return FileSaver._save_file(self, value, filepath, **opts)

    #@classmethod
    def write_file(self, value, filepath, **opts):
        self.filepath = filepath
        return FileSaver._write_file(self, value, self.filepath, **opts)

    #@classmethod
    def append_file(self, value, filepath, **opts):
        self.filepath = filepath
        return FileSaver._append_file(self, value, self.filepath, **opts)

    #@classmethod
    def save_file(self, value, filepath, **opts):
        self.filepath = filepath
        return FileSaver._save_file(self, value, self.filepath, **opts)

    def save(self, value, filepath=None, **opts):
        filepath = filepath or self.filepath
        return FileSaver._save_file(self, value, filepath, **opts)

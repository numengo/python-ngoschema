# -*- coding: utf-8 -*-
"""
utilities and stores to resolve canonical names in models

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import os

import arrow
import six
import itertools

from future.utils import with_metaclass
from ngofile.list_files import list_files
from six.moves.urllib.request import urlopen
from collections import Mapping, ChainMap

#from ngoschema import utils, get_builder
#from ..protocol_base import ProtocolBase
#from ..decorators import SCH_PATH_DIR
#from ..decorators import SCH_PATH_FILE
from ..types import PathDir, PathFile, String
from ..decorators import assert_arg, depend_on_prop
from ..protocols import SchemaMetaclass, ObjectProtocol
from ..protocols.serializer import Serializer
from ..protocols.file_loader import FileSaver
from ..query import Query
from ..types.uri import Uri, Path
from ..resolvers.uri_resolver import UriResolver
from ..models.instances import Entity


class File(with_metaclass(SchemaMetaclass, FileSaver, Entity)):
    """
    Document model which can be loaded from a filepath or a URL.
    Document can be loaded in memory, and deserialized (parsed) using provided
    deserializers or using the deserializers registered in memory
    """
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/File'

    def __init__(self, value=None, meta_opts=None, **opts):
        Entity.__init__(self, value, **opts)
        meta_opts = meta_opts or {}
        meta_opts.setdefault('binary', self.binary)
        FileSaver.__init__(self, **meta_opts)

    def set_filepath(self, filepath):
        return FileSaver.set_filepath(self, filepath)

    def set_binary(self, binary):
        self._binary = binary

    @depend_on_prop('filepath')
    def get_contentRaw(self):
        fp = self.filepath
        if fp and fp.exists():
            return FileSaver._load_file(self, fp)

    #@staticmethod
    #def _load(self, filepath, **opts):
    #    self.filepath = filepath
    #    return FileSaver._load_file(self, filepath, **opts)


class FileInfo(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/FileInfo'
    _lazyLoading = True

    def __init__(self, file=None, filepath=None, **opts):
        file = file or File(filepath)
        ObjectProtocol.__init__(self, file=file, **opts)

    def get_dateCreated(self):
        return arrow.get(self.file.filepath.stat().st_ctime)

    def get_dateModified(self):
        return arrow.get(self.file.filepath.stat().st_mtime)

    def get_contentSize(self):
        return self.file.filepath.stat().st_size

    def get_mimetype(self):
        import magic
        return magic.Magic(mime=True).from_file(str(self.file.filepath))

    @depend_on_prop('contentSize')
    def get_contentSizeHuman(self):
        num = int(self.contentSize)
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        return num

    def get_sha1(self):
        import hashlib
        sha = hashlib.sha1()
        fp = self.file.filepath if self.file else None
        if fp:
            with open(str(fp), 'rb') as source:
                block = source.read(2 ** 16)
                while len(block) != 0:
                    sha.update(block)
                    block = source.read(2 ** 16)
        elif self.uri:
            response = urlopen(str(self.uri))
            block = response.read(2 ** 16)
            while len(block) != 0:
                sha.update(block)
                block = response.read(2 ** 16)
        return sha.hexdigest()


class UriFile(with_metaclass(SchemaMetaclass, UriResolver)):
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/UriFile'

    def __init__(self, **opts):
        File.__init__(self, **opts)

    @depend_on_prop('uri')
    def get_contentRaw(self):
        if self.uri:
            return UriResolver._resolve(self, self.uri)
        return File.get_contentRaw(self)

    @staticmethod
    def _resolve(self, uri, **opts):
        self.uri = uri
        return UriResolver._resolve(self, self.uri.geturl(), **opts)


class Document(with_metaclass(SchemaMetaclass, UriFile)):
    """
    Document model which can be loaded from a filepath or a URL.
    Document can be loaded in memory, and deserialized (parsed) using provided
    deserializers or using the deserializers registered in memory
    """
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/Document'
    #_content = None
    #_contentRaw = None
    #_loaded = False
    _lazyLoading = True
    _encoder = Serializer

    _identifier = None

    def __init__(self, encoder=None, **opts):
        UriFile.__init__(self, **opts)
        self._encoder = encoder or self._encoder
        self._encoder.__init__(self, **opts)

    @depend_on_prop('uri', 'filepath')
    def get_contentRaw(self):
        if self.filepath:
            return FileSaver._load_file(self, self.filepath)
        if self.uri:
            return UriResolver._resolve(self, self.uri)

    @depend_on_prop('filepath', 'uri')
    def get_identifier(self):
        self._identifier = self.filepath or self.uri
        return self._identifier

    def get_file_info(self):
        return FileInfo(file=self, context=self._context)

    @depend_on_prop('content')
    def get_doc_id(self):
        content = self.content
        if content:
            return content.get('$id')

    @depend_on_prop('contentRaw')
    def get_content(self):
        if not self.binary:
            try:
                return self._encoder._deserialize(self, self.contentRaw)
            except Exception as er:
                self._logger.error(er, exc_info=True)

    def del_file(self):
        if not self.filepath:
            raise AttributeError('no filepath defined.')
        if not self.filepath.exists():
            raise ValueError('%s does not exist.' % self.filepath)
        os.remove(str(self.filepath))

    def _serialize(self, value, **opts):
        self._encoder._serialize(self, value, **opts)

    def load(self):
        doc_id = self.doc_id
        if doc_id:
            UriResolver.register_doc(self.content, doc_id)

    @property
    def loaded(self):
        return bool(self._content)

    def unload(self):
        # remove reference from main registry
        if self.id:
            UriResolver.unregister_doc(self.id)
        self.contentRaw = self.content = None

    def write(self, content, append=False, **opts):
        if self.filepath:
            if append:
                self._append_file(self, content, self.filepath, **opts)
            else:
                self._write_file(self, content, self.filepath, **opts)
        elif self.uri:
            raise Exception('impossible to write on a URL referenced document')

    @property
    def filename(self):
        return self.filepath.name if self.filepath else self.uri.split('/')[-1]


_default_document_registry = None


def get_document_registry():
    """
    Return the default document registry
    """
    global _default_document_registry
    if _default_document_registry is None:
        _default_document_registry = DocumentRegistry()
    return _default_document_registry


class DocumentRegistry(Mapping):
    def __init__(self):
        from ..repositories import JsonFileRepository
        self._fp_catalog = JsonFileRepository(instanceClass='ngoschema.models.document.Document', primaryKeys=['filepath'])
        self._url_catalog = JsonFileRepository(instanceClass='ngoschema.models.document.Document', primaryKeys=['uri'])
        self._chained = ChainMap(self._fp_catalog._catalog,
                                 self._url_catalog._catalog)

    def __getitem__(self, key):
        return self._chained[key]

    def __iter__(self):
        return six.iterkeys(self._chained)

    def __len__(self):
        return len(self._chained)

    @assert_arg(1, PathFile)
    def register_from_file(self, fp):
        """
        Register a document from a filepath

        :param fp: path of document to register
        """
        fp.resolve()
        if str(fp) not in self._fp_catalog._catalog:
            # no need for lazy loading as deserialize will load it anyway            doc =
            self._fp_catalog.register(Document(filepath=fp))
        doc = self._fp_catalog.get_instance(str(fp))
        return doc

    @assert_arg(1, String, type="string", format="uri-reference")
    def register_from_url(self, url):
        """
        Register a document from an URL

        :param url: url of document to register
        :param deserialize: flag to deserialize document in memory
        :param deserializers: list of deserializers to try to use if `deserialize`=True
        :param deserializers_opts: dictionary of options for deserializers
        """
        if str(url) not in self._url_catalog:
            self._url_catalog.add(Document(url=url))
        doc = self._url_catalog[str(url)]
        return doc

    @assert_arg(1, PathDir)
    def register_from_directory(self,
                                src,
                                includes=["*"],
                                excludes=[],
                                recursive=False):
        """
        Register documents from a search in a directory

        :param src: directory containing files to register
        :param includes: pattern or list of patterns (*.py, *.txt, etc...)
        :param excludes: pattern or patterns to exclude
        :param recursive: list files recursively
        """
        # no need to assert_args in regiser_from_file as list_files return a file
        return [
            self.register_from_file(fp) for fp in list_files(
                    src, includes, excludes, recursive, folders=0)
        ]

    def query(self, *attrs, order_by=False, **attrs_value):
        """
        Make a `Query` on registered documents
        """
        __doc__ = Query.filter.__doc__
        wow = list(self._chained.values())
        return Query(self._chained.values()).filter(
            *attrs, order_by=order_by, **attrs_value)

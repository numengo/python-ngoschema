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
import gettext
import arrow
import six
import itertools
import requests

from future.utils import with_metaclass
from ngofile.list_files import list_files
from six.moves.urllib.request import urlopen
from collections import ChainMap
from collections.abc import Mapping

#from ngoschema import utils, get_builder
#from ..protocol_base import ProtocolBase
#from ..decorators import SCH_PATH_DIR
#from ..decorators import SCH_PATH_FILE
from ..datatypes import PathDir, PathFile, String
from ..decorators import assert_arg, depend_on_prop
from ..protocols import SchemaMetaclass, ObjectProtocol
from ..protocols.serializer import Serializer
from ..protocols.file_loader import FileSaver
from ..query import Query
from ..datatypes.uri import Uri, Path
from ..resolvers.uri_resolver import UriResolver
from ..models.instances import Entity

_ = gettext.gettext


class Filepath(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/Filepath'

    def get_dateCreated(self):
        filepath = self.filepath
        if filepath:
            return arrow.get(filepath.stat().st_ctime)

    def get_dateModified(self):
        filepath = self.filepath
        if filepath:
            return arrow.get(filepath.stat().st_mtime)


class Folder(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/Folder'
    _lazyLoading = True

    def get_files(self):
        return [File(filepath=f) for f in list_files(self.filepath, recursive=False)]

    def get_subfolders(self):
        return [Folder(filepath=f) for f in list_files(self.filepath, recursive=False, folders=2)]

    def get_parent(self):
        return Folder(filepath=self.filepath.parent)


class File(with_metaclass(SchemaMetaclass, FileSaver)):
    _("""
    Document model which can be loaded from a filepath or a URL.
    Document can be loaded in memory, and deserialized (parsed) using provided
    deserializers or using the deserializers registered in memory
    """)
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/File'
    _lazyLoading = True

    def __init__(self, value=None, meta_opts=None, **opts):
        ObjectProtocol.__init__(self, value, **opts)
        meta_opts = meta_opts or {}
        meta_opts.setdefault('binary', self.binary)
        FileSaver.__init__(self, **meta_opts)

    def set_filepath(self, filepath):
        return FileSaver.set_filepath(self, filepath)

    def set_binary(self, binary):
        self._binary = binary

    @depend_on_prop('filepath')
    def get_contentRaw(self):
        value = self._data['contentRaw']
        if value is None:
            fp = self.filepath
            if fp and fp.exists():
                return FileSaver._load_file(self, fp, deserialize_instances=False, load_instances=False)
        return value

    #@staticmethod
    #def _load(self, filepath, **opts):
    #    self.filepath = filepath
    #    return FileSaver._load_file(self, filepath, **opts)


class UriFile(with_metaclass(SchemaMetaclass, UriResolver)):
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/UriFile'

    def __init__(self, **opts):
        File.__init__(self, **opts)

    def get_uri(self):
        uri = self._data['uri']
        if uri is None:
            uri = self._dataValidated['filepath'].resolve().as_uri()
        return uri

    @depend_on_prop('uri', 'filepath')
    def get_contentRaw(self):
        ret = self._data['contentRaw']
        if not ret:
            fp = self.filepath
            if fp:
                return FileSaver._load_file(self, fp)
            uri = self.uri
            if uri:
                r = requests.get(uri.geturl())
                if r.status_code == 200:
                    ret = r.text
                    self._set_dataValidated('encoding', r.encoding)
        return ret

    @staticmethod
    def _resolve(self, uri, **opts):
        self.uri = uri
        return UriResolver._resolve(self, self.uri.geturl(), **opts)

    @staticmethod
    def _serialize(self, value, excludes=[], **opts):
        if value.filepath:
            excludes = excludes + ['uri']
        return ObjectProtocol._serialize(self, value, excludes=excludes, **opts)


class Document(with_metaclass(SchemaMetaclass, UriFile)):
    _("""
    Document model which can be loaded from a filepath or a URL.
    Document can be loaded in memory, and deserialized (parsed) using provided
    deserializers or using the deserializers registered in memory
    """)
    _id = 'https://numengo.org/ngoschema#/$defs/files/$defs/Document'
    #_content = None
    #_contentRaw = None
    #_loaded = False
    _lazyLoading = True
    _encoder = Serializer

    #_identifier = None

    def __init__(self, encoder=None, **opts):
        UriFile.__init__(self, **opts)
        self._encoder = encoder or self._encoder
        self._encoder.__init__(self, **opts)

    #@depend_on_prop('filepath', 'uri')
    #def get_identifier(self):
    #    self._identifier = self.filepath or self.uri
    #    return self._identifier

    #def get_file_info(self):
    #    return FileInfo(file=self, context=self._context)

    #@depend_on_prop('content')
    #def get_doc_id(self):
    #    content = self.content
    #    if content:
    #        return content.get('$id')

    @depend_on_prop('contentRaw')
    def get_content(self):
        if not self.binary:
            try:
                return self._encoder._deserialize(self, self.contentRaw)
            except Exception as er:
                self._logger.error(er, exc_info=True)

    def _serialize(self, value, **opts):
        self._encoder._serialize(self, value, **opts)

#    def load(self):
#        doc_id = self.doc_id
#        if doc_id:
#            UriResolver.register_doc(self.content, doc_id)

    @property
    def loaded(self):
        return bool(self._content)

#    def unload(self):
#        # remove reference from main registry
#        if self.id:
#            UriResolver.unregister_doc(self.id)
#        self.contentRaw = self.content = None

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


#_default_document_registry = None
#
#
#def get_document_registry():
#    _("""
#    Return the default document registry
#    """)
#    global _default_document_registry
#    if _default_document_registry is None:
#        _default_document_registry = DocumentRegistry()
#    return _default_document_registry
#
#
#class DocumentRegistry(Mapping):
#    def __init__(self):
#        from ..repositories import JsonFileRepository
#        self._fp_catalog = JsonFileRepository(instanceClass='ngoschema.models.document.Document', primaryKeys=['filepath'])
#        self._url_catalog = JsonFileRepository(instanceClass='ngoschema.models.document.Document', primaryKeys=['uri'])
#        self._chained = ChainMap(self._fp_catalog._catalog,
#                                 self._url_catalog._catalog)
#
#    def __getitem__(self, key):
#        return self._chained[key]
#
#    def __iter__(self):
#        return six.iterkeys(self._chained)
#
#    def __len__(self):
#        return len(self._chained)
#
#    @assert_arg(1, PathFile)
#    def register_from_file(self, fp):
#        _("""
#        Register a document from a filepath
#
#        :param fp: path of document to register
#        """)
#        fp.resolve()
#        if str(fp) not in self._fp_catalog._catalog:
#            # no need for lazy loading as deserialize will load it anyway            doc =
#            self._fp_catalog.register(Document(filepath=fp))
#        doc = self._fp_catalog.get_instance(str(fp))
#        return doc
#
#    @assert_arg(1, String, type="string", format="uri-reference")
#    def register_from_url(self, url):
#        _("""
#        Register a document from an URL
#
#        :param url: url of document to register
#        :param deserialize: flag to deserialize document in memory
#        :param deserializers: list of deserializers to try to use if `deserialize`=True
#        :param deserializers_opts: dictionary of options for deserializers
#        """)
#        if str(url) not in self._url_catalog:
#            self._url_catalog.add(Document(url=url))
#        doc = self._url_catalog[str(url)]
#        return doc
#
#    @assert_arg(1, PathDir)
#    def register_from_directory(self,
#                                src,
#                                includes=["*"],
#                                excludes=[],
#                                recursive=False):
#        _("""
#        Register documents from a search in a directory
#
#        :param src: directory containing files to register
#        :param includes: pattern or list of patterns (*.py, *.txt, etc...)
#        :param excludes: pattern or patterns to exclude
#        :param recursive: list files recursively
#        """)
#        # no need to assert_args in regiser_from_file as list_files return a file
#        return [
#            self.register_from_file(fp) for fp in list_files(
#                    src, includes, excludes, recursive, folders=0)
#        ]
#
#    def query(self, *attrs, order_by=False, **attrs_value):
#        """
#        Make a `Query` on registered documents
#        """
#        __doc__ = Query.filter.__doc__
#        wow = list(self._chained.values())
#        return Query(self._chained.values()).filter(
#            *attrs, order_by=order_by, **attrs_value)
#

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

from ngoschema import utils
from ..protocol_base import ProtocolBase
from ..decorators import SCH_PATH_DIR
from ..decorators import SCH_PATH_FILE
from ..decorators import assert_arg
from ..query import Query
from ..schema_metaclass import SchemaMetaclass
from ..resolver import register_doc_with_uri_id, unregister_doc_with_uri_id


class Document(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Document model which can be loaded from a filepath or a URL.
    Document can be loaded in memory, and deserialized (parsed) using provided
    deserializers or using the deserializers registered in memory
    """
    __schema__ = r'http://numengo.org/ngoschema/document#/definitions/Document'
    __add_logging__ = False
    __assert_args__ = False
    __attr_by_name__ = False
    _contentRaw = None
    _content = None
    _loaded = False

    _identifier = None

    def __init__(self, *args, **props):
        ProtocolBase.__init__(self, *args, **props)

    @property
    def _id(self):
        if self._content:
            return self._content.get('$id')

    @property
    def identifier(self):
        if self._identifier is None:
            self._identifier = self.filepath or self.url
        return str(self._identifier) if self._identifier else ''

    def load(self):
        """
        Load document in memory

        :param encoding: character encoding
        """
        content = None
        encoding = str(self.charset)
        if self.filepath:
            if not self.binary:
                with codecs.open(str(self.filepath), 'r', encoding) as f:
                    content = f.read()
            else:
                with open(str(self.filepath), mode='rb') as f:
                    content = f.read()
        elif self.url:
            response = urlopen(str(self.url))
            content = response.read().decode(encoding)
        if content is None:
            raise IOError("Impossible to load %s." % self.identifier)
        self._contentRaw = content
        self._loaded = True

    def delete_file(self):
        if not self.filepath:
            raise AttributeError('no filepath defined.')
        if not self.filepath.exists():
            raise ValueError('%s does not exist.' % self.filepath)
        os.remove(str(self.filepath))

    @property
    def loaded(self):
        return self._loaded

    def unload(self):
        # remove reference from main registry
        if self._id:
            unregister_doc_with_uri_id(self._id)
        self._contentRaw = self._content = None

    def write(self, content, mode='w'):
        if self.filepath:
            if not self.binary:
                enc = str(self.charset)
                with codecs.open(str(self.filepath), mode, enc) as f:
                    f.write(content)
            else:
                with open(str(self.filepath), mode+'b') as f:
                    f.write(content)
            self._contentRaw = content if mode != 'a' else self._contentRaw + content
        elif self.url:
            raise Exception('impossible to write on a URL referenced document')

    def _deserialize(self, load_function, **kwargs):
        import json
        if not self.loaded:
            self.load()
        try:
            self._content = load_function(self._contentRaw, **kwargs)
        except Exception as er:
            raise Exception('impossible to deserialize %s: %s' % (self.identifier, er))
        if self._id:
            register_doc_with_uri_id(self._content, self._id)
        return self._content

    @property
    def contentRaw(self):
        return self._contentRaw

    def get_dateCreated(self):
        return arrow.get(self.filepath.stat().st_ctime)

    def get_dateModified(self):
        return arrow.get(self.filepath.stat().st_mtime)

    def get_contentSize(self):
        return self.filepath.stat().st_size if self.filepath else None

    def get_contentSizeHuman(self):
        num = int(self.contentSize)
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    def get_mimetype(self):
        import magic
        magic.Magic(mime=True).from_file(str(self.filepath))

    def get_uri(self):
        return self.filepath.as_uri() if self.filepath else None

    def get_content(self):
        return self._content or self._contentRaw

    content = property(get_content)


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
        self._fp_registry = JsonFileRepository(objectClass='ngoschema.models.document.Document', fkeys=['filepath'])
        self._url_registry = JsonFileRepository(objectClass='ngoschema.models.document.Document', fkeys=['uri'])
        self._chained = ChainMap(self._fp_registry._registry,
                                 self._url_registry._registry)

    def __getitem__(self, key):
        return self._chained[key]

    def __iter__(self):
        return six.iterkeys(self._chained)

    def __len__(self):
        return len(self._chained)

    @assert_arg(1, SCH_PATH_FILE)
    def register_from_file(self, fp):
        """
        Register a document from a filepath

        :param fp: path of document to register
        """
        fp.resolve()
        if str(fp) not in self._fp_registry._registry:
            # no need for lazy loading as deserialize will load it anyway            doc =
            self._fp_registry.register(Document(filepath=fp))
        doc = self._fp_registry.get_instance(str(fp))
        return doc

    @assert_arg(1, {"type": "string", "format": "uri-reference"})
    def register_from_url(self, url):
        """
        Register a document from an URL

        :param url: url of document to register
        :param deserialize: flag to deserialize document in memory
        :param deserializers: list of deserializers to try to use if `deserialize`=True
        :param deserializers_opts: dictionary of options for deserializers
        """
        if str(url) not in self._url_registry:
            self._url_registry.add(Document(url=url))
        doc = self._url_registry[str(url)]
        return doc

    @assert_arg(1, SCH_PATH_DIR)
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

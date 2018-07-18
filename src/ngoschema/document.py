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

import arrow
import magic
import six
from future.utils import with_metaclass
from ngofile.list_files import list_files
from six.moves.urllib.request import urlopen

from . import utils
from .canonical_name import CN_ID
from .canonical_name import register_document_with_cname
from .canonical_name import resolve_cname
from .classbuilder import ProtocolBase
from .decorators import SCH_PATH_DIR
from .decorators import SCH_PATH_FILE
from .decorators import assert_arg
from .deserializers import deserializer_registry
from .query import Query
from .schema_metaclass import SchemaMetaclass
from .uri_identifier import URI_ID
from .uri_identifier import register_document_with_uri_id
from .uri_identifier import resolve_uri


class Document(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Document model which can be loaded from a filepath or a URL.
    Document can be loaded in memory, and deserialized (parsed) using provided
    deserializers or using the deserializers registered in memory
    """
    schemaUri = r"http://numengo.org/ngoschema/Document#definitions/document"
    __add_logging__ = False
    __assert_args__ = False
    __attr_by_name__ = False
    _contentRaw = None
    _loaded = False
    _deserialized = False

    _identifier = None

    @property
    def identifier(self):
        if self._identifier is None:
            self._identifier = self.filepath or self.url
        return str(self._identifier) if self._identifier else ''

    def load(self, encoding="utf-8"):
        """
        Load document in memory

        :param encoding: character encoding
        """
        content = None
        if self.filepath:
            with codecs.open(str(self.filepath), 'r', encoding) as f:
                content = f.read()
        elif self.url:
            response = urlopen(str(self.url))
            content = response.read().decode(encoding)
        if content is None:
            raise IOError("Impossible to load %s." % self.identifier)
        self._contentRaw = content
        self._loaded = True

    @property
    def loaded(self):
        return self._loaded

    @property
    def contentRaw(self):
        return self._contentRaw

    def deserialize(self, deserializers=[], **deserializer_opts):
        """
        Deserialize document using provided deserializers (or registered one if none 
        provided)

        :param deserializers: list of deserializers to try to deserialize document
        :param deserializers_opts: dictionary of options for deserializer
        """
        if not self.loaded:
            self.load()
        ds = deserializers  # alias
        ds = ds if isinstance(ds, list) else [ds]
        # if no deserializer provided, try all registered ones
        ds = ds if ds else deserializer_registry.registry.values()
        for deserializer in ds:
            try:
                doc = deserializer.loads(self.contentRaw, **deserializer_opts)
                break
            except Exception as er:
                pass
        else:
            raise IOError("Impossible to load %s with deserializers %s." %
                          (self.identifier, ds))
        self._content = doc
        self._deserialized = True
        if CN_ID in doc:
            register_document_with_cname(doc, doc[CN_ID])
        if URI_ID in doc:
            register_document_with_uri_id(doc, doc[URI_ID])
        return doc

    @property
    def deserialized(self):
        return self._deserialized

    def get_dateCreated(self):
        return arrow.get(self.filepath.stat().st_ctime)

    def get_dateModified(self):
        return arrow.get(self.filepath.stat().st_mtime)

    def get_contentSize(self):
        return self.filepath.stat().st_size

    def get_contentSizeHuman(self):
        num = int(self.contentSize)
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    def get_mimetype(self):
        magic.Magic(mime=True).from_file(str(self.filepath))

    def get_uri(self):
        return self.filepath.as_uri()

    def get_content(self):
        return self._content

    _id = None

    @property
    def get_id(self):
        if self._id is None and self.content:
            self._id = self.content['id']
        return self._id


_default_document_registry = None


def get_document_registry():
    """
    Return the default document registry
    """
    global _default_document_registry
    if _default_document_registry is None:
        _default_document_registry = DocumentRegistry()
    return _default_document_registry


class DocumentRegistry(object):
    def __init__(self):
        self.registry = {}

    @assert_arg(1, SCH_PATH_FILE)
    def register_from_file(self,
                           fp,
                           assert_args=True,
                           deserialize=False,
                           deserializers=[],
                           deserializers_opts={}):
        """
        Register a document from a filepath

        :param fp: path of document to register
        :param assert_args: flag to check/convert argument types
        :param deserialize: flag to deserialize document in memory
        :param deserializers: list of deserializers to try to use if `deserialize`=True
        :param deserializers_opts: dictionary of options for deserializers
        """
        fp.resolve()
        if str(fp) not in self.registry:
            # no need for lazy loading as deserialize will load it anyway
            self.registry[str(fp)] = Document(filepath=fp)
        doc = self.registry[str(fp)]
        if deserialize and not doc.deserialized:
            doc.deserialize(deserializers=deserializers, **deserializers_opts)
        return doc

    @assert_arg(1, {"type": "string", "format": "uri-reference"})
    def register_from_url(self,
                          url,
                          assert_args=True,
                          deserialize=False,
                          deserializers=[],
                          deserializers_opts={}):
        """
        Register a document from an URL

        :param url: url of document to register
        :param assert_args: flag to check/convert argument types
        :param deserialize: flag to deserialize document in memory
        :param deserializers: list of deserializers to try to use if `deserialize`=True
        :param deserializers_opts: dictionary of options for deserializers
        """
        if str(url) not in self.registry:
            self.registry[str(url)] = Document(url=url)
        doc = self.registry[str(url)]
        if deserialize and not doc.deserialized:
            doc.deserialize(deserializers=deserializers, **deserializers_opts)
        return doc

    @assert_arg(1, SCH_PATH_DIR)
    def register_from_directory(self,
                                src,
                                includes=["*"],
                                excludes=[],
                                recursive=False,
                                assert_args=True,
                                deserialize=False,
                                deserializers=[],
                                deserializers_opts={}):
        """
        Register documents from a search in a directory
       
        :param src: directory containing files to register
        :param includes: pattern or list of patterns (*.py, *.txt, etc...)
        :param excludes: pattern or patterns to exclude
        :param recursive: list files recursively
        :param assert_args: flag to check/convert argument types
        :param deserialize: flag to deserialize document in memory
        :param deserializers: list of deserializers to try to use if `deserialize`=True
        :param deserializers_opts: dictionary of options for deserializers
        """
        # no need to assert_args in regiser_from_file as list_files return a file
        return [
            self.register_from_file(
                fp,
                assert_args=False,
                deserialize=deserialize,
                deserializers=deserializers,
                deserializers_opts=deserializers_opts) for fp in list_files(
                    src, includes, excludes, recursive, folders=0)
        ]

    def query(self, order_by=False, *attrs, **attrs_value):
        """
        Make a `Query` on registered documents
        """
        __doc__ = Query.filter.__doc__
        return Query(self.registry.values()).filter(
            order_by=order_by, *attrs, **attrs_value)

    def __iter__(self):
        return six.itervalues(self.registry)


def resolve_ref(ref):
    if not utils.is_string(ref):
        ref = str(ref)
    if '/' in ref:
        return resolve_uri(ref)
    else:
        return resolve_cname(ref)

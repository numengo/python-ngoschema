# *- coding: utf-8 -*-
"""
Utilities and classes to resolve schemas enabling inheritance.

The resolver expand a schema adding all the properties of the bases mentionned
in the 'extends' field

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created: 01/05/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import copy
import functools
import posixpath
from os import path
from urllib.parse import unquote, urlparse

import dpath.util
import requests
import inflection
from jsonschema.validators import urldefrag, lru_cache, urljoin
from jsonschema.validators import RefResolver

from ..exceptions import InvalidValue
from ..utils import UriDict, ReadOnlyChainMap as ChainMap
from ..utils import apply_through_collection
from ..utils import is_string, is_sequence
#from ..protocols.resolver import Resolver
from .. import settings

logger = logging.getLogger(__name__)


def domain_uri(name, domain=None):
    from ngoschema.managers.namespace_manager import clean_for_uri
    domain = domain or settings.MS_DOMAIN
    return "%s%s#" % (domain, clean_for_uri(name))


@functools.lru_cache(128)
def resolve_doc(uri_id, remote=False):
    uri, frag = urldefrag(uri_id)
    ret = UriResolver._doc_store.get(uri)
    if ret is not None:
        return ret
    if remote:
        # we could load the resource
        doc = requests.get(uri).json()
        UriResolver.register_doc(doc, uri)
        return doc
    raise Exception('Unresolvable uri %s' % uri_id)


def resolve_fragment(doc, fragment):
    fragment = fragment.lstrip(u'/')
    parts = unquote(fragment).split(u"/") if fragment else []
    for i, part in enumerate(parts):
        try:
            part = part.replace(u"~1", u"/").replace(u"~0", u"~")
            if is_sequence(doc):
                part = int(part)
            doc = doc[part]
        except:
            raise InvalidValue("Impossible to find fragment '%s' in document." % ('/'.join(parts[:i+1])))
    return doc


def resolve_uri(uri_id, doc=None, remote=False):
    uri, frag = urldefrag(uri_id)
    if doc is None:
        doc = resolve_doc(uri, remote)
    try:
        return resolve_fragment(doc, frag)
    except Exception as er:
        raise InvalidValue("Impossible to resolve uri %s. %s" % (uri_id, str(er)))


def relative_url(target, base):
    base = urlparse(base)
    target = urlparse(target)
    if base.netloc != target.netloc:
        raise ValueError('target and base netlocs do not match')
    base_dir = '.' + posixpath.dirname(base.path)
    target = '.' + target.path
    return posixpath.relpath(target, start=base_dir)


class UriResolver(RefResolver):
    _doc_store = UriDict()

    @staticmethod
    def get_doc_store():
        return UriResolver._doc_store

    @staticmethod
    def unregister_doc(uri_id):
        try:
            del UriResolver._doc_store[uri_id]
        except KeyError:
            logger.warning("no %s uri in URI registry", uri_id)

    @staticmethod
    def register_doc(doc, uri_id):
        UriResolver._doc_store[uri_id] = doc

    def __init__(
        self,
        base_uri,
        referrer,
        store=None,
        cache_remote=True,
        handlers=(),
        urljoin_cache=None,
        remote_cache=None,
    ):
        if urljoin_cache is None:
            urljoin_cache = functools.lru_cache(1024)(urljoin)
        if remote_cache is None:
            remote_cache = functools.lru_cache(1024)(self.resolve_from_url)

        self.referrer = referrer
        self.cache_remote = cache_remote
        self.handlers = dict(handlers)

        self._scopes_stack = [base_uri]
        self.store = store or UriResolver._doc_store
        self.store[base_uri] = referrer

        self._urljoin_cache = urljoin_cache
        self._remote_cache = remote_cache

    @staticmethod
    def create(uri=None, schema=None):
        uri = uri or settings.DEFAULT_MS_URI
        doc_uri, frag = urldefrag(uri)
        if doc_uri in UriResolver._doc_store:
            return UriResolver(doc_uri, UriResolver._doc_store[doc_uri])
        # not in doc store, create a resolver with a copy
        if schema is None:
            schema = resolve_uri(uri)
        return UriResolver(uri, schema, store=dict(UriResolver._doc_store))

    def _expand(self, uri, schema, doc_scope):
        """ expand a schema to add properties of all definitions it extends
        if a URI is given, it will be used to identify the schema in a cache store.
        If no resolver is given, use a resolver with local schema store, with the
        URI as referring document.

        :param schema: schema definition
        :type schema: dict
        :param uri: schema uri
        :type uri: string
        :param doc_scope: current doc uri
        :type doc_scope: string
        :rtype: dict
        """
        uri = self._urljoin_cache(self.resolution_scope, uri)

        schema_scope, frag = urldefrag(uri)

        ref = schema.pop('$ref', None)

        if ref:
            ref = self._urljoin_cache(doc_scope, ref)
            uri_, schema_ = RefResolver.resolve(self, ref)
            sch = self._expand(uri_, schema_, doc_scope)
            schema.update(sch)

        if 'items' in schema and '$ref' in schema['items']:
            ref = schema['items'].pop('$ref')
            uri_, schema_ = RefResolver.resolve(self, ref)
            schema['items'].update(schema_)

        for k, v in schema.get('properties', {}).items():
            if '$ref' in v:
                uri_, schema_ = RefResolver.resolve(self, v.pop('$ref'))
                schema['properties'][k].update(schema_)

        extends = [RefResolver.resolve(self, e)[1] for e in schema.pop("extends", [])]
        schema['properties'] = ChainMap(schema.get('properties', {}), *[e.get('properties', {}) for e in extends])
        if not schema['properties']:
            del schema['properties']

        return schema

    @staticmethod
    def _resolve(self, value, remote=False, **opts):
        uri, frag = urldefrag(value)
        doc = UriResolver._doc_store.get(uri)
        if doc is not None:
            return resolve_fragment(doc, frag) if frag else doc
        try:
            if remote:
                # we could load the resource
                if not frag:
                    return requests.get(uri).content
                doc = requests.get(uri).json()
                UriResolver.register_doc(doc, uri)
                return resolve_fragment(doc, frag)
        except Exception as er:
            raise InvalidValue("Impossible to resolve uri %s. %s" % (value, str(er)))


def scope(uri, base_id):
    return f'{uri.split("#")[0] or base_id.split("#")[0]}#{uri.split("#")[1]}' if '#' in uri else uri

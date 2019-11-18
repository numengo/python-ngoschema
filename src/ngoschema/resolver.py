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
from jsonschema.compat import urldefrag
from jsonschema.validators import RefResolver

from .utils import UriDict
from .utils import apply_through_collection
from .utils import is_string, is_sequence

logger = logging.getLogger(__name__)

def domain_uri(name, domain=None):
    from . import settings
    from .classbuilder import _clean_ns_name
    domain = domain or settings.MS_DOMAIN
    return "%s%s" % (domain, _clean_ns_name(name))


_uri_doc_store = UriDict()


def get_uri_doc_store():
    return _uri_doc_store

def unregister_doc_with_uri_id(uri_id):
    try:
        del _uri_doc_store[uri_id]
    except KeyError:
        logger.warning("no %s uri in URI registry", uri_id)


def register_doc_with_uri_id(doc, uri_id):
    _uri_doc_store[uri_id] = doc


_resolver = None


def get_resolver(base_uri=None):
    """
    Return a resolver set with the main loaded schema store
    with a base URI and the corresponding referred document.
    If no base_uri is defined, DEFAULT_MS_URI is used

    :param base_uri: base_uri to use for resolver
    :type base_uri: string
    """
    from . import settings
    base_uri = base_uri or settings.MS_URI
    global _resolver
    ms = get_uri_doc_store()
    base_uri, dummy = urldefrag(base_uri)
    if base_uri not in ms:
        raise IOError("%s not found in loaded documents (%s)" %
                      (base_uri, ", ".join(ms.keys())))
    referrer = ms[base_uri]
    if _resolver is None:
        _resolver = RefResolver(base_uri, referrer, ms)
        # rebuild store using our UriDict which deals with lowercase urls
        _resolver.store = ms
    if not set(ms.keys()).issubset(_resolver.store.keys()):
        _resolver.store.update(ms)
    if base_uri != _resolver.base_uri:
        _resolver.push_scope(base_uri)
    return _resolver


@functools.lru_cache(30)
def resolve_doc(uri_id, remote=False):
    uri, frag = urldefrag(uri_id)
    ret = _uri_doc_store.get(uri)
    if ret:
        return ret
    if remote:
        # we could load the resource
        doc = requests.get(uri).json()
        _uri_doc_store[uri] = doc
        return doc
    raise Exception('Unresolvable uri %s' % uri_id)


def resolve_fragment(doc, fragment):
    fragment = fragment.lstrip(u'/')
    parts = unquote(fragment).split(u"/") if fragment else []
    for part in parts:
        try:
            part = part.replace(u"~1", u"/").replace(u"~0", u"~")
            if is_sequence(doc):
                part = int(part)
            doc = doc[part]
        except:
            raise KeyError(part)
    return doc


def resolve_uri(uri_id, doc=None, remote=False):
    uri, frag = urldefrag(uri_id)
    if doc is None:
        doc = resolve_doc(uri, remote)
    return resolve_fragment(doc, frag)


def qualify_ref(ref, base):
    if ref[0] == "#":
        # Local ref
        return base.rsplit("#", 1)[0] + ref
    else:
        return ref


def relative_url(target, base):
    base = urlparse(base)
    target = urlparse(target)
    if base.netloc != target.netloc:
        raise ValueError('target and base netlocs do not match')
    base_dir = '.' + posixpath.dirname(base.path)
    target = '.' + target.path
    return posixpath.relpath(target, start=base_dir)


class ExpandingResolver(RefResolver):
    __doc__ = (""" 
    Resolver expanding the resolved document according to the 'extends' field
    (array of uri-reference). The returned document is a deep merge of all
    corresponding documents.
    The merge is done according to the order of 'extends' (properties can be
    overwritten).The original resolved document is merged at the end.
    """ + RefResolver.__doc__)
    _def_store = dict()
    _expanding = True

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

        ref = schema.get("$ref")

        if ref:
            ref = self._urljoin_cache(doc_scope, ref)
            uri_, schema_ = RefResolver.resolve(self, ref)
            ret = self._def_store.get(uri_)
            if ret:
                return ret
            sch = self._expand(uri_, schema_, doc_scope)
            self._def_store[uri_] = sch
            return sch

        ret = self._def_store.get(uri)
        if ret:
            return ret

        schema_exp = {}

        extends = schema.get("extends", [])
        for i, ref in enumerate(extends):
            ref = self._urljoin_cache(doc_scope, ref)
            uri_, schema_ = RefResolver.resolve(self, ref)
            extends[i] = uri_
            sch = self._expand(uri_, schema_, doc_scope)
            # sch is returned from _expand and is already "a copy", no need to deepcopy it
            dpath.util.merge(schema_exp, sch, flags=dpath.util.MERGE_REPLACE)

        schema_copy = copy.deepcopy(schema)

        def replace_relative_uris(coll, key, level):
            val = coll[key]
            if is_string(val) and val.startswith('#/'):
                coll[key] = self._urljoin_cache(schema_scope, val)

        apply_through_collection(schema_copy, replace_relative_uris, recursive=True)

        dpath.util.merge(schema_exp, schema_copy, flags=dpath.util.MERGE_REPLACE)

        extends = schema.get("extends", [])
        extends_ = []
        [extends_.append(x) for x in extends if x not in extends_]
        schema_exp["extends"] = extends_

        # self._def_store[uri] = schema_exp
        return schema_exp

    @functools.lru_cache(50)
    def resolve_from_url(self, url, expand=True):
        """
        Resolve a reference and returns its URI and the corresponding schema.

        :param url: reference to look for
        :type url: string
        :param expand: expand result if schema extends others
        :rtype: [string, dict]
        """
        schema = RefResolver.resolve_from_url(self, url)
        if expand:
            url_scoped = self._urljoin_cache(self.resolution_scope, url)
            res_scope, frag = urldefrag(url_scoped)
            schema = self._expand(url, schema, res_scope)
        return schema

    def resolve_by_name(self, name, expand=True):
        """
        Resolve a definition by name from the schema store.
        Return a tuple (uri,schema) or a list of tuple

        :param name: definition name
        :type name: string
        :rtype: tuple
        """
        res_scope, _ = urldefrag(self.resolution_scope)
        uris = list(self.store.keys())
        uris.remove(res_scope)
        uris.insert(0, res_scope)

        for uri in uris:
            s = self.store[uri]
            for p, d in dpath.util.search(
                s.get("definitions", {}), "**/%s" % name, yielded=True):
                id = "%s#/definitions/%s" % (uri, p)
                if expand:
                    self.push_scope(uri)
                    d = self._expand(id, d, res_scope)
                    self.pop_scope()
                return id, d

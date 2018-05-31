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

import copy
import gettext
import logging
from builtins import object
from builtins import str

import dpath.util
from jsonschema.compat import urldefrag
from jsonschema.compat import urljoin
from jsonschema.compat import urlsplit
from jsonschema.validators import RefResolver

from .schemas_loader import _get_all_schemas_store

_ = gettext.gettext

DEFAULT_MS_URI = 'http://numengo.org/draft-04/schema'
DEFAULT_DEFS_URI = 'http://numengo.org/draft-04/defs-schema'

_def_store = dict()


class ExpandingResolver(RefResolver):
    __doc__ = """ 
    Resolver expanding the resolved document according to the 'extends' field
    (array of uri-reference). The returned document is a deep merge of all
    corresponding documents.
    The merge is done according to the order of 'extends' (properties can be
    overwritten).The original resolved document is merged at the end.
    """ + RefResolver.__doc__

    _expanding = True

    def _expand(self, uri, schema):
        """ expand a schema to add properties of all definitions it extends 
        if a URI is given, it will be used to identify the schema in a cache store.
        If no resolver is given, use a resolver with local schema store, with the
        URI as referring document.
        
        :param schema: schema definition
        :type schema: dict 
        :param uri: schema uri
        :type uri: string
        :param resolver: resolver to use instead of default resolver.
        :rtype: dict
        """
        uri = self._urljoin_cache(self.resolution_scope, uri)
        if uri in _def_store:
            return _def_store[uri]

        doc_scope, frag = urldefrag(uri)

        ref = schema.get('$ref')

        if ref:
            ref = self._urljoin_cache(doc_scope, ref)
            uri_, schema_ = RefResolver.resolve(self, ref)
            sch = self._expand(uri_, schema_)
            _def_store[uri] = sch
            return sch

        schema_exp = {}

        extends = schema.get('extends', [])
        for ref in extends:
            ref = self._urljoin_cache(doc_scope, ref)
            uri_, schema_ = RefResolver.resolve(self, ref)
            sch = self._expand(uri_, schema_)
            dpath.util.merge(schema_exp, copy.deepcopy(sch))

        dpath.util.merge(schema_exp, copy.deepcopy(schema))

        extends = schema.get('extends', [])
        if extends:
            extends_ = []
            for e in extends:
                if e not in extends_:
                    extends_.append(e)
            schema_exp['extends'] = extends_

        _def_store[uri] = schema_exp
        return schema_exp

    def resolve_no_expand(self, ref):
        """
        Resolve reference without expanding result.
        """
        return self.resolve(ref, False)

    def resolve(self, ref, expand=True):
        """
        Resolve a reference and returns its URI and the corresponding schema.

        :param ref: reference to look for
        :type ref: string
        :param expand: expand result if schema extends others
        :rtype: [string, dict]
        """
        __doc__ = RefResolver.__doc__
        url, schema = RefResolver.resolve(self, ref)
        if expand:
            schema = self._expand(url, schema)
        return url, schema

    def resolve_by_name(self, name, expand=True):
        """
        Resolve a definition by name from the schema store.
        Return a tuple (uri,schema) or a list of tuple
        
        :param name: definition name
        :type name: string
        :rtype: tuple
        """
        uris = list(self.store.keys())
        uris.remove(self.resolution_scope)
        uris.insert(0, self.resolution_scope)

        for uri in uris:
            s = self.store[uri]
            for p, d in dpath.util.search(
                    s.get('definitions', {}), '**/%s' % name, yielded=True):
                id = '%s#/definitions/%s' % (uri, p)
                if expand:
                    self.push_scope(uri)
                    d = self._expand(id, d)
                    self.pop_scope()
                return id, d


_resolver = None


def get_resolver(base_uri=DEFAULT_MS_URI):
    """
    Return a resolver set with the main loaded schema store
    with a base URI and the corresponding referred document.
    If no base_uri is defined, DEFAULT_MS_URI is used
    
    :param base_uri: base_uri to use for resolver
    :type base_uri: string
    """
    global _resolver
    base_uri, dummy = urldefrag(base_uri)
    ms = _get_all_schemas_store()
    if base_uri not in ms:
        raise IOError(
            _('%s not found in loaded schemas (%s)' % (base_uri,
                                                       ', '.join(ms.keys()))))
    referrer = ms[base_uri]
    if not _resolver:
        _resolver = ExpandingResolver(base_uri, referrer, ms)
    if base_uri != _resolver.base_uri:
        _resolver.push_scope(base_uri)
    return _resolver

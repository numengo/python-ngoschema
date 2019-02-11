# -*- coding: utf-8 -*-
""" 
utilities and stores to resolve canonical names in models

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  
"""
from __future__ import print_function
from __future__ import unicode_literals

import requests
from six.moves.urllib.parse import urlparse
import sys
import posixpath
from jsonschema._utils import URIDict
from jsonschema.compat import urldefrag
from six.moves.urllib.parse import unquote

from . import utils

_doc_id_store = URIDict()

URI_ID = '$id'


def norm_uri(uri):
    # use method of URI dict
    return _doc_id_store.normalize(uri)


def register_document_with_uri_id(doc, uri_id):
    _doc_id_store[norm_uri(uri_id)] = doc


def resolve_doc(uri_id, remote=False):
    uri, frag = urldefrag(uri_id)
    if uri in _doc_id_store:
        return _doc_id_store[uri]
    if remote:
        # we could load the resource
        doc = requests.get(uri).json()
        _doc_id_store[uri] = doc
        return doc
    raise Exception('Unresolvable uri %s' % uri_id)


def resolve_fragment(doc, fragment):
    fragment = fragment.lstrip(u'/')
    parts = unquote(fragment).split(u"/") if fragment else []
    for part in parts:
        try:
            part = part.replace(u"~1", u"/").replace(u"~0", u"~")
            if utils.is_sequence(doc):
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

def relative_url(target, base):
    base=urlparse(base)
    target=urlparse(target)
    if base.netloc != target.netloc:
        raise ValueError('target and base netlocs do not match')
    base_dir='.'+posixpath.dirname(base.path)
    target='.'+target.path
    return posixpath.relpath(target,start=base_dir)
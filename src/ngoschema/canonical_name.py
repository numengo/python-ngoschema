# -*- coding: utf-8 -*-
""" 
utilities and stores to resolve canonical names in models

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  
"""
from __future__ import print_function
from __future__ import unicode_literals

from python_jsonschema_objects.util import lazy_format

from . import utils
from .uri_identifier import resolve_uri

_document_cn_store = dict()
_doc_cn_store = dict()

CN_KEY = 'name'
CN_ID = 'canonicalName'

def register_document_with_cname(document, cname):
    _document_cn_store[cname] = document
    _doc_cn_store[cname] = document.content

def register_document_with_cname(doc, cname):
    _doc_cn_store[cname] = doc


def resolve_cname_path(cn, parent=None, cn_key=CN_KEY):
    """
    Resolve a document and a path from a canonical name.
    Return a tuple of the parent document as a dict, and the path to the element
    as a list

    :param cn: canonical name, given as a string (ex: 'package.group.component')
    or a path ['package', 'group', 'component'].
    :param parent: parent document as a dict (ie a document), or a canonical name
    identifier to look for in a document store. Document should have been registered
    using `register_document` or `register file`. If no document is provided, then
    the document store is walked through to look for all documents with canonical names
    corresponding to the beginning of the required input canonical name. The best match
    is used.
    :param cn_key: key to use to build canonical name (default is CN_KEY='name')
    """
    cn_path = cn if utils.is_sequence(cn) else cn.strip('#').strip('.').split('.')
    cur_cn = []

    #  parent document is provided, just convert cn to list path
    if isinstance(parent, dict):
        parent_doc = parent
    else:
        # find parent document if not provided
        if parent is None:
            parents = [
                _cn for _cn in _doc_cn_store.keys() if cn.startswith(_cn)
            ]
            if parents:
                parents.sort(reverse=True)
                parent = parents[0]
            else:
                raise Exception('no parent found for cn %s' % cn)
        parent_doc = _doc_cn_store[parent]
        cur_cn = parent.split('.')[:-1]

    if set(parent_doc) == set(['$ref']):
        parent_doc = resolve_uri(parent_doc['$ref'])


    if cn_path[:-1] == cur_cn and parent_doc.get(cn_key) == cn_path[-1]:
        return parent_doc, [] # cur path is empty as we are at the root

    # use generators because of 'null' which might lead to different paths
    def _resolve_cname(cn, cur, cur_cn, cur_path, cn_key=CN_KEY):
        cn = [e.replace('<anonymous>', 'null') for e in cn]
        # empty path, yield current path and doc
        if not cn:
            yield cur, cn, cur_path
        if isinstance(cur, dict):
            if set(cur) == set(['$ref']):
                cur = resolve_uri(cur['$ref'])
            cn2 = cur_cn + [cur.get(cn_key, 'null')]
            if cn2 == cn[0:len(cn2)]:
                if cn2 == cn:
                    yield cur, cn, cur_path
                for k, v in cur.items():
                    if isinstance(v, dict) or isinstance(v, list):
                        for _ in _resolve_cname(cn, v, cn2, cur_path + [k], cn_key):
                            yield _
        if isinstance(cur, list):
            for i, v in enumerate(cur):
                for _ in _resolve_cname(cn, v, cur_cn, cur_path + [i], cn_key):
                    yield _

    # first search without last element, as last one might not be a named object
    # but the name of an attribute
    for d, c, p in _resolve_cname(cn_path[:-1], parent_doc, cur_cn, [], cn_key):
        if cn_path[-1] in d or d.get(cn_key) == cn_path[-1]:
            p.append(cn_path[-1])
            return parent_doc, p
        # we can continue the search from last point. we remove the last element of the
        # canonical name which is going to be read again
        for d2, c2, p2 in _resolve_cname(cn_path, d, c[:-1], p, cn_key):
            return parent_doc, p2
    raise Exception(lazy_format("Unresolvable canonical name '{0}' in '{1}'", cn, parent))


def resolve_cname(cn, parent=None, cn_key=CN_KEY):
    """
    Returns the element resolved by `resolve_cname_path`
    """
    parent_doc, path = resolve_cname_path(cn, parent, cn_key)
    cur = parent_doc
    for p in path:
        cur = cur[p]
    return cur


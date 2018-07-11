# -*- coding: utf-8 -*-
""" 
utilities and stores to resolve canonical names in models

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  
"""
from __future__ import print_function
from __future__ import unicode_literals

from . import utils

_doc_cn_store = dict()

CN_KEY = 'name'
CN_ID = 'canonicalName'


def register_document_with_cname(doc, cname):
    _doc_cn_store[cname] = doc


def resolve_cname(cn, parent=None, cn_key=CN_KEY):
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
    #  parent document is provided, just convert cn to list path
    if isinstance(parent, dict):
        parent_doc = parent
        cn_path = cn if utils.is_sequence(cn) else cn.strip('#').strip(
            '.').split('.')
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
        fragment = cn.split(parent)[-1].strip('.')
        cn_path = fragment.split('.')
        parent_doc = _doc_cn_store[parent]
    cur = parent_doc
    path = []
    for i, p in enumerate(cn_path):
        found = False
        # last element: can take element directly in collection
        if i == (len(cn_path) - 1) and p in cur:
            found = True
            path.append(p)
            break
        # go through collection and look for element with key corresponding to path elem
        for k, v in cur.items():
            if isinstance(v, dict) and v.get(cn_key) == p:
                found = True
                path.append(k)
                cur = v
                break
            elif isinstance(v, list):
                for i2, v2 in enumerate(v):
                    if isinstance(v2, dict) and v2.get(cn_key) == p:
                        found = True
                        path.append(k)
                        path.append(i2)
                        cur = v2
                        break
        if not found:
            raise Exception(
                'Unresolvable canonical name %s in %s' % (cn, parent))
    return parent_doc, path


def get_cname(cn, parent=None, cn_key=CN_KEY):
    """
    Returns the element resolved by `resolve_cname`
    """
    cur, path = resolve_cname(cn, parent, cn_key)
    for p in path:
        cur = cur[p]
    return cur

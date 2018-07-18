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
    cn_path = cn if utils.is_sequence(cn) else cn.strip('#').strip(
            '.').split('.')
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

    # use generators because of 'null' which might lead to different paths
    def _search_path(cn, cur, cur_cn, cur_path):
        if isinstance(cur, dict):
            cn2 = cur_cn+[cur.get(cn_key, 'null')]
            if cn2 == cn[0:len(cn2)]:
                if cn2 == cn:
                    yield cur, cn2, cur_path
                for k, v in cur.items():
                    if isinstance(v, dict) or isinstance(v, list):
                        for _ in _search_path(cn, v, cn2, cur_path+[k]):
                            yield _
        if isinstance(cur, list):
            for i, v in enumerate(cur):
                for _ in _search_path(cn, v, cur_cn, cur_path+[i]):
                    yield _
                
    # first search without last element, as last one might not be a named object
    # but the name of an attribute
    for d, c, p in _search_path(cn_path[:-1], parent_doc, cur_cn, []):
        if d.get(cn_key) == cn_path[-1]:
            return parent_doc, p.append(cn_path[-1])
        # we can continue the search from last point. we remove the last element of the
        # canonical name which is going to be read again
        for  d2, c2, p2 in _search_path(cn_path, d, c[:-1], p):
            return parent_doc, p2
    raise Exception('Unresolvable canonical name %s in %s' % (cn, parent))

def resolve_cname(cn, parent=None, cn_key=CN_KEY):
    """
    Returns the element resolved by `resolve_cname_path`
    """
    cur, path = resolve_cname_path(cn, parent, cn_key)
    for p in path:
        cur = cur[p]
    return cur

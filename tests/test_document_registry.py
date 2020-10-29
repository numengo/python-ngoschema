# -*- coding: utf-8 -*-
"""
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import print_function
from __future__ import unicode_literals

import json
import time

from ngofile.list_files import list_files

#from ngoschema.canonical_name import _doc_cn_store
from ngoschema.models.documents import Document
from ngoschema.models.documents import get_document_registry
from ngoschema.resolvers.uri_resolver import _uri_doc_store

dirpath = "/Users/cedric/Devel/python/python-ngomf/ngomf/models/Ngo"

def test_DocumentRegistry2():
    s = time.time()
    ls = list(
        list_files(
            dirpath,
            includes='*.json',
            recursive=True))
    print('list_files', time.time() - s, len(ls))
    s = time.time()
    os = [
        Document(filepath=f, validate=True) for f in list_files(
            dirpath,
            recursive=True)
    ]
    print('list_files no lazy', time.time() - s, len(os))
    s = time.time()
    os = [
        Document(filepath=f, validate=False)
        for f in list_files(
            dirpath,
            recursive=True)
    ]
    print('list_files lazy no validation', time.time() - s, len(os))
    s = time.time()
    os = [
        Document(filepath=f, validate=False) for f in list_files(
            dirpath,
            recursive=True)
    ]
    print('list_files lazy', time.time() - s, len(os))

    s = time.time()
    doc_reg = get_document_registry()
    doc_reg.register_from_directory(
        dirpath,
        includes='*.json',
        recursive=True,
    )
    print(len(doc_reg.registry.values()))
    print('register', time.time() - s)
    doc = list(doc_reg.registry.values())[0]
    assert doc.loaded == False
    doc.deserialize()
    assert doc.loaded == True
    s = time.time()
    [doc.deserialize(deserializers=json) for doc in doc_reg]
    print('load', time.time() - s)
    print('uri store', len(_uri_doc_store))


def test_DocumentRegistry():
    s = time.time()
    doc_reg = get_document_registry()
    doc_reg.register_from_directory(
        dirpath,
        includes='*.json',
        recursive=True)
    print('register and load', time.time() - s)
    print('uri store', len(_uri_doc_store))
    query = doc_reg.query(filepath__name='NGOMED00.json')[:]
    assert len(query) == 1


if __name__ == "__main__":
    #test_DocumentRegistry2()
    test_DocumentRegistry()


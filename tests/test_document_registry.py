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

from ngoschema.canonical_name import _doc_cn_store
from ngoschema.document import Document
from ngoschema.document import get_document_registry
from ngoschema.uri_identifier import _doc_id_store


def test_DocumentRegistry2():
    s = time.time()
    ls = list(
        list_files(
            r'D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo',
            includes='*.json',
            recursive=True))
    print('list_files', time.time() - s, len(ls))
    s = time.time()
    os = [
        Document(filepath=f, _lazy_loading=False) for f in list_files(
            r'D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo',
            recursive=True)
    ]
    print('list_files no lazy', time.time() - s, len(os))
    s = time.time()
    os = [
        Document(filepath=f, _lazy_loading=True, _validate_lazy=False)
        for f in list_files(
            r'D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo',
            recursive=True)
    ]
    print('list_files lazy no validation', time.time() - s, len(os))
    s = time.time()
    os = [
        Document(filepath=f, _lazy_loading=True) for f in list_files(
            r'D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo',
            recursive=True)
    ]
    print('list_files lazy', time.time() - s, len(os))

    s = time.time()
    doc_reg = get_document_registry()
    doc_reg.register_from_directory(
        r'D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo',
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
    print('cn store', len(_doc_cn_store))
    print('uri store', len(_doc_id_store))


def test_DocumentRegistry():
    s = time.time()
    doc_reg = get_document_registry()
    doc_reg.register_from_directory(
        r'D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo',
        includes='*.json',
        recursive=True,
        deserialize=True,
        deserializers=json)
    print('register and load', time.time() - s)
    print('cn store', len(_doc_cn_store))
    print('uri store', len(_doc_id_store))
    query = doc_reg.query(filepath__name='NGOMED00.json')[:]
    assert len(query) == 1


if __name__ == "__main__":
    #test_DocumentRegistry2()
    test_DocumentRegistry()

#from ngofile.list_files import list_files
#
#from ngoschema.deserializers import JsonDeserializer
#from ngoschema.document_loader import get_cname
#from ngoschema.document_loader import register_document
#
#all_docs = {}
#
#start = time.time()
#for f in list_files(
#        r'D:\CODES\python-ngomf\src\ngomf\models\draft-05',
#        '*.json',
#        recursive=True):
#    all_docs[str(f)] = JsonDeserializer.load(f, no_assert_arg=True)
#    #with f.open('r') as f2:
#    #    all_docs[str(f)] = json.load(f2)
#end = time.time()
#print(end - start)
#print(len(all_docs))
#
#
#register_document(r"D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo\MoistAir\PhaseChange\MACND00.json")
#register_document(r"D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo\MoistAir.json")
#register_document(r"D:\CODES\python-ngomf\src\ngomf\models\draft-05\Ngo\Fluid.json")
#
#def test_get_cname():
#    v = get_cname("Ngo.MoistAir.PhaseChange.MACND00.Parameters.PhaseChange.doFlash.YES")
#    assert v['numericalValue'] == 1
#
#if __name__ == "__main__":
#    test_get_cname()
#

# -*- coding: utf-8 -*-
"""

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from ngoschema.object_factory import ObjectFactory
from ngoschema.object_loader import ObjectLoader

doc1 = {
    "filepath": r"D:\CODES\projects.ngoprj",
    "author": "doc1",
    "description": "a description",
    "keywords": ["cpp"]
}

doc2 = {
    "filepath": r"D:\CODES\ngoci.py.ngocc",
    "author": "doc2",
    "description": "a description",
    "keywords": ["python", "ci"]
}

doc3 = {
    "filepath": r"D:\CODES\ngoschema.py.ngocc",
    "author": "_doc3",
    "keywords": ["schemas", "json"]
}


def test_factory_and_query():
    doc_loader = ObjectLoader(objectClass='ngoschema.document.Document')
    objs = doc_loader.create([doc1, doc2, doc3], many=True)

    assert len(doc_loader.filter(keywords__size__ge=2, load_lazy=True)) == 2
    assert len(doc_loader.filter_any_of(filepath__suffix=".ngoprj", author__endswith="2", load_lazy=True)) == 2, doc_loader.filter_any_of(filepath__suffix=".ngoprj", author__endswith="2")
    assert len(doc_loader.filter(keywords__intersects=["schemas", "python"])) == 2
    with pytest.raises(TypeError):
        assert len(doc_loader.filter(keywords__intersects="python")) == 2
    assert len(doc_loader.exclude(filepath__suffix=".ngoprj")) == 2
    assert len(doc_loader.filter(filepath__suffix=".ngoprj")) == 1
    assert len(doc_loader.filter(filepath__suffix__not=".ngoprj")) == 2
    assert len(doc_loader.filter(filepath__suffix__not=".ngoprj", author__istartswith="doc")) == 1
    assert len(doc_loader.filter(author__istartswith="doc")) == 2
    assert len(doc_loader.filter(author__icontains="doc")) == 3
    assert len(doc_loader.filter("description")) == 2
    assert len(doc_loader.exclude("description")) == 1
    assert len(doc_loader.filter_any_of("description", filepath__suffix__not=".ngoprj")) == 3
    assert len(doc_loader.exclude_any_of(filepath__suffix=".ngoprj", author__endswith="2", load_lazy=True)) == 1
    assert len(doc_loader.exclude_any_of("description", filepath__suffix=".ngoprj", author__endswith="3")) == 0


if __name__ == "__main__":
    test_factory_and_query()
import os.path
import pathlib
from datetime import date
from datetime import datetime
from datetime import time

from ngoschema.metadata import Metadata

def test_fkey_relationship():

    A = Metadata(name="A")
    B = Metadata(name="B")
    C = Metadata(name="C")

    assert str(A.canonicalName) == 'A'
    assert str(B.canonicalName) == 'B'

    A.parent = B
    assert A.parent.ref is B

    assert str(A.canonicalName) == 'B.A'
    assert str(B.canonicalName) == 'B'

    assert B.children
    assert B.children[0].ref is A

    B.name = 'BB'
    assert str(B.name) == 'BB' 
    assert B.iname == 'BB'
    assert str(A.parent) == 'BB', str(A.parent)
    assert str(B.canonicalName) == 'BB'
    assert str(A.canonicalName) == 'BB.A'

    C.parent = B
    assert len(B.children)==2

    return
    del C
    assert len(B.children)==1

    del B
    assert A.parent.ref is None

if __name__ == "__main__":
    test_fkey_relationship()

import os.path
import pathlib
from datetime import date
from datetime import datetime
from datetime import time
import sys

from ngoschema.metadata import Metadata

def test_fkey_relationship():

    A = Metadata(name="A")
    B = Metadata(name="B")
    C = Metadata(name="C")

    assert str(A.canonicalName) == 'A'
    assert str(B.canonicalName) == 'B'

    # set a child through parent member
    B.parent = A
    assert B.parent.ref is A
    # check canonical names
    assert str(A.canonicalName) == 'A'
    assert str(B.canonicalName) == 'A.B'
    # check children
    assert len(A.children)==1
    assert A.children[0].ref is B

    # set another child through parent member
    C.parent = A
    assert len(A.children)==2
    assert len(B.children)==0
    assert len(C.children)==0

    # remove reference
    C.parent = None
    assert len(A.children)==1

    # test adding a children
    A.children.append(C)
    assert len(A.children)==2
    assert C.parent.ref is A

    # change name and check propagation
    A.name = 'AA'
    assert str(A.name) == 'AA' 
    assert A.iname == 'AA'
    assert str(B.parent) == 'AA', str(B.parent)
    assert str(A.canonicalName) == 'AA'
    assert str(B.canonicalName) == 'AA.B'

    # check override of canonical name and its propagation
    A.canonicalName = 'AAA.AA'
    assert B.canonicalName == 'AAA.AA.B'

    del C
    #assert len(A.children)==1

    del A
    assert B.parent.ref is None
    assert B.canonicalName == 'B'

if __name__ == "__main__":
    test_fkey_relationship()

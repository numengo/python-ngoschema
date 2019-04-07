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
    import weakref
    print(weakref.getweakrefcount(C))

    assert str(A.canonicalName) == 'A', str(A.canonicalName)
    assert str(B.canonicalName) == 'B', str(B.canonicalName)

    # set a child through parent member
    B.parent = A
    assert B.parent.ref is A, B.parent.ref
    # check canonical names
    assert str(A.canonicalName) == 'A', str(A.canonicalName)
    assert str(B.canonicalName) == 'A.B', str(B.canonicalName)
    # check children
    assert len(A.children)==1, len(A.children)
    assert A.children[0].ref is B, A.children[0].ref

    # set another child through parent member
    C.parent = A
    print(weakref.getweakrefcount(C))
    assert len(A.children)==2
    assert len(B.children)==0
    assert len(C.children)==0

    # remove reference
    C.parent = None
    assert len(A.children)==1
    print(weakref.getweakrefcount(C))

    # test adding a children
    #A.children.append(C)
    C.parent = A
    print(weakref.getweakrefcount(C))
    assert len(A.children)==2
    assert C.parent.ref is A
    print(weakref.getweakrefcount(C))

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
    # DOESN'T WORK, only .parent = None
    #assert len(A.children)==1, len(A.children)

    del A
    assert B.parent.ref is None
    assert B.canonicalName == 'B'

if __name__ == "__main__":
    test_fkey_relationship()

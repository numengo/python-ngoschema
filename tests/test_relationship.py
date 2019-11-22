from ngoschema.models import EntityWithMetadata


def test_fkey_relationship():

    A = EntityWithMetadata(name="A")
    B = EntityWithMetadata(name="B")
    C = EntityWithMetadata(name="C")

    assert str(A.canonicalName) == 'A', str(A.canonicalName)
    assert str(B.canonicalName) == 'B', str(B.canonicalName)

    # set a child through parent member
    B._parent = A
    assert B._parent is A, B._parent
    # check canonical names
    assert str(A.canonicalName) == 'A', str(A.canonicalName)
    assert str(B.canonicalName) == 'A.B', str(B.canonicalName)
    # check children
    assert len(A.children)==1, len(A.children)
    assert A.children[0].ref is B, A.children[0].ref

    # set another child through parent member
    C._parent = A
    assert len(A.children)==2
    assert len(B.children)==0
    assert len(C.children)==0

    # remove reference
    C._parent = None
    assert len(A.children)==1

    # test adding a children
    A.children.append(C)
    assert len(A.children)==2
    assert C._parent.ref is A

    # change name and check propagation
    A.name = 'AA'
    assert str(A.name) == 'AA'
    assert A.iname == 'AA'
    assert str(B._parent) == 'AA', str(B._parent)
    assert str(A.canonicalName) == 'AA'
    assert str(B.canonicalName) == 'AA.B'

    # check override of canonical name and its propagation
    A.canonicalName = 'AAA.AA'
    assert B.canonicalName == 'AAA.AA.B'

    C._parent = None
    assert len(A.children)==1, len(A.children)

    B._parent = None
    assert B._parent.ref is None
    assert B.canonicalName == 'B'

if __name__ == "__main__":
    test_fkey_relationship()

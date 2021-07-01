import pytest

from future.utils import with_metaclass
from ngoschema.exceptions import InvalidValue
from ngoschema.loaders.schemas import load_schema
from ngoschema.protocols import SchemaMetaclass, split_cname

split_cname('asd[1][2]')

load_schema({
    '$id': 'A',
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'a': {'type': 'string'},
    }
})

load_schema({
    '$id': 'B',
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'b': {'type': 'integer'},
    }
})

load_schema({
    '$id': 'BextA',
    'type': 'object',
    'extends': ['A'],
    'additionalProperties': False,
    'properties': {
        'b': {'type': 'integer'},
    }
})


def test_object_protocol():
    class A(with_metaclass(SchemaMetaclass)):
        _id = 'A'

    class B(with_metaclass(SchemaMetaclass)):
        _id = 'B'

    class AB(with_metaclass(SchemaMetaclass, A, B)):
        a = '1'

    a = A(a=1)
    assert a.a == '1'
    with pytest.raises(AttributeError) as e_info:
        a.b = 1
    a.a = 2
    assert a.a == '2', a.a

    b = B(b=1)
    assert b.b == 1, b.b
    with pytest.raises(AttributeError) as e_info:
        b.a = 1

    ab = AB(b=1)
    assert ab.a == '1', ab.a
    assert ab.b == 1, ab.b
    ab.c = 1  # additional properties default is True, not redefined in AB
    assert ab.c == 1

    class BA(with_metaclass(SchemaMetaclass)):
        _id = 'BextA'

    ba = BA(a=1)
    assert ba.a == '1', ba.a


def test_call_order():
    # test smart lazy loading and property evaluation order
    class Foo(with_metaclass(SchemaMetaclass)):
        _lazyLoading = True
        _schema = {
            'type': 'object',
            'additionalProperties': False,
            'required': ['b'],
            'readOnly': ['c'],
            'properties': {
                'a': {'type': 'string', 'default': '{{b}}'},
                'b': {'type': 'integer'},
                'c': {'type': 'integer', 'default': '`int(a)+1', 'maximum': 2}
            }
        }

    foo = Foo(b=1)
    # access attributes through descriptors ensuring conversion and validation
    assert foo.c == 2  # properly evaluate expression with with a not yet evaluated
    assert foo.a == '1'  # properly casted to string
    with pytest.raises(AttributeError) as e_info:
        foo.c = 2  # c is read only
    assert len(foo) == 3  # behaves like normal dict
    assert foo.a == foo['a']
    for k, v in foo.items():
        assert getattr(foo, k) == v
    # set a valid value, which makes another one invalid
    foo.b = 2  # ok so far
    with pytest.raises(InvalidValue) as e_info:
        foo.c  # invalid value as maximum is 2 and evaluation is 3
    foo.b = '1'  # reset to a compatible value for c, setting an integer convert from string
    assert foo['b'] == foo.b == 1
    foo.do_validate()
    # create a json dict with filtering options
    foo2 = foo.do_serialize(no_defaults=False, excludes=Foo._readOnly)
    assert foo2['a'] == foo.a
    assert 'c' not in foo2
    assert 'c' in foo.do_serialize(no_defaults=False)


def test_schema_mro():
    import ngosim
    from ngoschema.types import type_builder
    mro = type_builder.schema_mro('https://numengo.org/ngosim#$defs/variable/$defs/EnumerationVariable')
    assert mro


def test_repr():
    class Obj(with_metaclass(SchemaMetaclass)):
        _schema = {
            'type': 'object',
            'properties': {
                'a': {'type': 'string'},
                'b': {'type': 'integer'},
            }
        }

    print(repr(Obj))
    fa = Obj(a=1)
    fb = Obj(b=1)
    print(repr(fa))
    print(repr(fb))
    print(str(Obj))
    print(str(fa))
    print(str(fb))

    class Arr(with_metaclass(SchemaMetaclass)):
        _schema = {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }

    #print(repr(Arr))
    a1 = Arr(['a', 'b'])
    print(repr(a1))
    print(str(a1))


def test_repr2():
    from ngoschema.models.files import Document
    print(repr(Document._properties))



if __name__ == "__main__":
    #test_repr2()
    test_object_protocol()
    test_call_order()
    test_repr()

    #test_schema_mro()

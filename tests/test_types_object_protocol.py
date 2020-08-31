import pytest

from future.utils import with_metaclass
from ngoschema.exceptions import InvalidValue
from ngoschema.schemas_loader import load_schema
from ngoschema.protocols import ObjectMetaclass, split_cname

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
    class A(with_metaclass(ObjectMetaclass)):
        _id = 'A'

    class B(with_metaclass(ObjectMetaclass)):
        _id = 'B'

    class AB(with_metaclass(ObjectMetaclass, A, B)):
        a = 1  # define a default in class, should be converted to string as required in schema

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

    class BA(with_metaclass(ObjectMetaclass)):
        _id = 'BextA'

    ba = BA(a=1)
    assert ba.a == '1', ba.a


def test_call_order():
    # test smart lazy loading and property evaluation order
    class Foo(with_metaclass(ObjectMetaclass)):
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
    foo2 = foo.do_serialize(no_defaults=False, excludes=Foo._read_only)
    assert foo2['a'] == foo.a
    assert 'c' not in foo2
    assert 'c' in foo.do_serialize(no_defaults=False)


def test_schema_mro():
    import ngosim
    from ngoschema.types import TypeBuilder
    mro = TypeBuilder.schema_mro('https://numengo.org/ngosim#$defs/variable/$defs/EnumerationVariable')
    assert mro


if __name__ == "__main__":
    test_call_order()
    test_object_protocol()
    #test_schema_mro()

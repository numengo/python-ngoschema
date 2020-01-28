# from https://github.com/maroux/serpy.git

import warnings
import pytest  # noqa

from ngoschema.serializers.fields import Field, MethodField, IntField, FloatField, StrField
from ngoschema.serializers.serializer import Serializer, DictSerializer


class Obj(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def assert_true(cond):
    assert cond


def assert_false(cond):
    assert not cond


def test_simple():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field()

    a = Obj(a=5)
    assert ASerializer(a).representation['a'] == 5

    a = ASerializer(data={'a': 5}).internal_value
    assert a.a == 5


def test_data_and_obj_cached():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field()

    a = Obj(a=5)
    serializer = ASerializer(a)
    data1 = serializer.representation
    data2 = serializer.representation
    # Use assertTrue instead of assertIs for python 2.6.
    assert_true(data1 is data2)

    serializer = ASerializer(data={'a': 5})
    obj1 = serializer.internal_value
    obj2 = serializer.internal_value
    # Use assertTrue instead of assertIs for python 2.6.
    assert_true(obj1 is obj2)


def test_inheritance():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field()

    class CSerializer(Serializer):
        _cls = Obj

        c = Field()

    class ABSerializer(ASerializer):
        b = Field()

    class ABCSerializer(ABSerializer, CSerializer):
        pass

    a = Obj(a=5, b='hello', c=100)
    assert ASerializer(a).representation['a'] == 5
    data = ABSerializer(a).representation
    assert data['a'] == 5
    assert data['b'] == 'hello'
    data = ABCSerializer(a).representation
    assert data['a'] == 5
    assert data['b'] == 'hello'
    assert data['c'] == 100

    a = {'a': 5, 'b': 'hello', 'c': 100}
    serializer = ASerializer(data=a)
    assert serializer.internal_value.a == 5
    serializer = ABSerializer(data=a)
    assert serializer.internal_value.a == 5
    assert serializer.internal_value.b == 'hello'
    serializer = ABCSerializer(data=a)
    assert serializer.internal_value.a == 5
    assert serializer.internal_value.b == 'hello'
    assert serializer.internal_value.c == 100


def test_many():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field()

    objs = [Obj(a=i) for i in range(5)]
    data = ASerializer(objs, many=True).representation
    assert len(data) == 5
    assert data[0]['a'] == 0
    assert data[1]['a'] == 1
    assert data[2]['a'] == 2
    assert data[3]['a'] == 3
    assert data[4]['a'] == 4

    data = [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}]
    objs = ASerializer(data=data, many=True).internal_value
    assert len(objs) == 5
    assert objs[0].a == 0
    assert objs[1].a == 1
    assert objs[2].a == 2
    assert objs[3].a == 3
    assert objs[4].a == 4


def test_serializer_as_field():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field()

    class BSerializer(Serializer):
        _cls = Obj

        b = ASerializer()

    b = Obj(b=Obj(a=3))
    assert BSerializer(b).representation['b']['a'] == 3

    data = {'b': {'a': 3}}
    obj = BSerializer(data=data).internal_value
    assert obj.b.a == 3


def test_serializer_as_field_many():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field()

    class BSerializer(Serializer):
        _cls = Obj

        b = ASerializer(many=True)

    b = Obj(b=[Obj(a=i) for i in range(3)])
    b_data = BSerializer(b).representation['b']
    assert len(b_data) == 3
    assert b_data[0]['a'] == 0
    assert b_data[1]['a'] == 1
    assert b_data[2]['a'] == 2

    data = {'b': [{'a': 0}, {'a': 1}, {'a': 2}]}
    obj = BSerializer(data=data).internal_value
    assert len(obj.b) == 3
    assert obj.b[0].a == 0
    assert obj.b[1].a == 1
    assert obj.b[2].a == 2


def test_serializer_as_field_call():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field()

    class BSerializer(Serializer):
        _cls = Obj

        b = ASerializer(call=True)

    b = Obj(b=lambda: Obj(a=3))
    assert BSerializer(b).representation['b']['a'] == 3
    # TBD check that deserialization doesnt work


def test_serializer_method_field():
    class ASerializer(Serializer):
        _cls = Obj

        a = MethodField()
        b = MethodField('add_9', 'sub_9')

        def get_a(self, obj):
            return obj.a + 5

        def set_a(self, obj, value):
            obj.a = value - 5

        def add_9(self, obj):
            return obj.b + 9

        def sub_9(self, obj, value):
            obj.b = value - 9

    a = Obj(a=2, b=2)
    data = ASerializer(a).representation
    assert data['a'] == 7
    assert data['b'] == 11
    data = {'a': 7, 'b': 11}
    obj = ASerializer(data=data).internal_value
    assert obj.a == 2
    assert obj.b == 2


def test_field_called():
    class ASerializer(Serializer):
        _cls = Obj

        a = IntField()
        b = FloatField(call=True)
        c = StrField(attr='foo.bar.baz')

    o = Obj(a='5', b=lambda: '6.2', foo=Obj(bar=Obj(baz=10)))
    data = ASerializer(o).representation
    assert data['a'] == 5
    assert data['b'] == 6.2
    assert data['c'] == '10'
    data = {'a': 5, 'b': 6.2, 'c': '10'}
    obj = ASerializer(data=data).internal_value
    assert obj.a == 5
    assert_false(hasattr(obj, 'b'))
    assert_false(hasattr(obj, 'foo'))


def test_dict_serializer():
    class ASerializer(DictSerializer):
        _cls = Obj

        a = IntField()
        b = Field(attr='foo')

    d = {'a': '2', 'foo': 'hello'}
    data = ASerializer(d).representation
    assert data['a'] == 2
    assert data['b'] == 'hello'
    data = {'a': 2, 'b': 'hello'}
    obj = ASerializer(data=data).internal_value
    assert obj.a == 2
    assert obj.foo == 'hello'


def test_dotted_attr():
    class ASerializer(Serializer):
        _cls = Obj

        a = Field('a.b.c')

    o = Obj(a=Obj(b=Obj(c=2)))
    data = ASerializer(o).representation
    assert data['a'] == 2
    data = {'a': 2}
    obj = ASerializer(data=data).internal_value
    assert_false(hasattr(obj, 'a'))


def test_custom_field():
    class Add5Field(Field):
        def to_representation(self, value):
            return value + 5

        def to_internal_value(self, data):
            return data - 5

    class ASerializer(Serializer):
        _cls = Obj

        a = Add5Field()

    o = Obj(a=10)
    data = ASerializer(o).representation
    assert data['a'] == 15
    data = {'a': 15}
    obj = ASerializer(data=data).internal_value
    assert obj.a == 10


def test_optional_field():
    class ASerializer(Serializer):
        _cls = Obj

        a = IntField(required=False)

    o = Obj(a=None)
    data = ASerializer(o).representation
    assert data['a'] is None

    data = {'a': None}
    obj = ASerializer(data=data).internal_value
    assert obj.a is None

    o = Obj(a='5')
    data = ASerializer(o).representation
    assert data['a'] == 5

    data = {'a': 5}
    obj = ASerializer(data=data).internal_value
    assert obj.a == 5

    class ASerializer(Serializer):
        _cls = Obj

        a = IntField()

    o = Obj(a=None)
    with pytest.raises(TypeError):
        ASerializer(o).representation

    data = {}
    with pytest.raises(KeyError):
        ASerializer(data=data).internal_value


def test_read_only_field():
    class ASerializer(Serializer):
        _cls = Obj

        a = IntField(read_only=True)

    o = Obj(a='5')
    data = ASerializer(o).representation
    assert data['a'] == 5

    data = {'a': 5}
    obj = ASerializer(data=data).internal_value
    assert_false(hasattr(obj, 'a'))


def test_cls_required_for_deserialization():
    class ASerializer(Serializer):
        a = IntField()

    data = {'a': 5}
    with pytest.raises(AttributeError):
        ASerializer(data=data).internal_value


def test_data_backwards_compatibility():
    class ASerializer(Serializer):
        a = IntField()

    o = Obj(a='5')
    serializer = ASerializer(o)
    assert serializer.data is serializer.representation


def test_data_deprecation_warning():
    o = Obj(a='5')
    serializer = Serializer(o)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always', DeprecationWarning)
        serializer.data
        assert len(w) == 1
        assert_true(issubclass(w[-1].category, DeprecationWarning))
        assert 'deprecated' in str(w[-1].message)


if __name__ == '__main__':
    test_simple()
    test_data_and_obj_cached()
    test_inheritance()
    test_many()
    test_serializer_as_field()
    test_serializer_as_field_many()
    test_serializer_as_field_call()
    test_serializer_method_field()
    test_field_called()
    test_dict_serializer()
    test_dotted_attr()
    test_custom_field()
    test_optional_field()
    test_read_only_field()
    test_cls_required_for_deserialization()
    test_data_backwards_compatibility()
    test_data_deprecation_warning()

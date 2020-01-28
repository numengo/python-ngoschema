# from https://github.com/maroux/serpy.git

import warnings

from ngoschema.serializers.fields import (
    Field, MethodField, BoolField, IntField, FloatField, StrField)


class Obj(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def assert_true(cond):
    assert cond


def assert_false(cond):
    assert not cond


def test_to_value_noop():
    assert Field().to_representation(5) == 5
    assert Field().to_representation('a') == 'a'
    assert Field().to_representation(None) is None


def test_to_internal_value_noop():
    assert Field().to_internal_value(5) == 5
    assert Field().to_internal_value('a') == 'a'
    assert Field().to_internal_value(None) is None


def test_as_getter_none():
    assert Field().as_getter(None, None) is None


def test_as_setter_none():
    assert Field().as_setter(None, None) is None


def test_is_to_representation_overridden():
    class TransField(Field):
        def to_representation(self, value):
            return value

    field = Field()
    assert_false(field._is_to_representation_overridden())
    field = TransField()
    assert_true(field._is_to_representation_overridden())
    field = IntField()
    assert_true(field._is_to_representation_overridden())


def test_is_to_internal_value_overridden():
    class TransField(Field):
        def to_internal_value(self, value):
            return value

    field = Field()
    assert_false(field._is_to_internal_value_overridden())
    field = TransField()
    assert_true(field._is_to_internal_value_overridden())


def test_str_field():
    field = StrField()
    assert field.to_representation('a') == 'a'
    assert field.to_representation(5) == '5'
    assert field.to_internal_value('a') == 'a'
    assert field.to_internal_value(5) == '5'


def test_bool_field():
    field = BoolField()
    assert_true(field.to_representation(True))
    assert_false(field.to_representation(False))
    assert_true(field.to_representation(1))
    assert_false(field.to_representation(0))
    assert_true(field.to_internal_value(True))
    assert_false(field.to_internal_value(False))
    assert_true(field.to_internal_value(1))
    assert_false(field.to_internal_value(0))


def test_int_field():
    field = IntField()
    assert field.to_representation(5) == 5
    assert field.to_representation(5.4) == 5
    assert field.to_representation('5') == 5
    assert field.to_internal_value(5) == 5
    assert field.to_internal_value(5.4) == 5
    assert field.to_internal_value('5') == 5


def test_float_field():
    field = FloatField()
    assert field.to_representation(5.2) == 5.2
    assert field.to_representation('5.5') == 5.5
    assert field.to_internal_value(5.2) == 5.2
    assert field.to_internal_value('5.5') == 5.5


def test_method_field():
    class FakeSerializer(object):
        def get_a(self, obj):
            return obj.a

        def set_a(self, obj, value):
            obj.a = value

        def z_sub_1(self, obj):
            return obj.z - 1

        def z_add_1(self, obj, value):
            obj.z = value + 1

    serializer = FakeSerializer()

    field = MethodField()
    fn = field.as_getter('a', serializer)
    assert fn(Obj(a=3)) == 3

    fn = field.as_setter('a', serializer)
    o = Obj(a=-1)
    fn(o, 3)
    assert o.a == 3

    field = MethodField('z_sub_1', 'z_add_1')
    fn = field.as_getter('z', serializer)
    assert fn(Obj(z=3)) == 2

    fn = field.as_setter('z', serializer)
    o = Obj(a=-1)
    fn(o, 2)
    assert o.z == 3

    assert_true(MethodField.getter_takes_serializer)
    assert_true(MethodField.setter_takes_serializer)


def test_to_value_backwards_compatibility():
    class AddOneIntField(IntField):
        def to_value(self, value):
            return super(AddOneIntField, self).to_value(value) + 1

    assert AddOneIntField().to_value('1') == 2

    assert IntField().to_value('1') == 1


def test_to_value_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always', DeprecationWarning)
        IntField().to_value('1')
        assert len(w) == 1
        assert_true(issubclass(w[-1].category, DeprecationWarning))
        assert 'deprecated' in str(w[-1].message)


if __name__ == '__main__':
    test_to_value_noop()
    test_to_internal_value_noop()
    test_as_getter_none()
    test_as_setter_none()
    test_is_to_representation_overridden()
    test_is_to_internal_value_overridden()
    test_str_field()
    test_bool_field()
    test_int_field()
    test_float_field()
    test_method_field()
    test_to_value_backwards_compatibility()
    test_to_value_deprecation_warning()

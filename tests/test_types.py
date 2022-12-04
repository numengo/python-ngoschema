import pytest
from ngoschema.exceptions import *
from ngoschema import datatypes
import ngoschema.datatypes.symbols as symbols

from collections import OrderedDict
import pathlib
import decimal
from urllib.parse import ParseResult
from datetime import datetime, date, time
import arrow


def test_base():
    i = datatypes.Integer(maximum=0)
    assert repr(i) == "ngoschema.datatypes.numerics.Integer(type='integer', maximum=0)"
    assert str(i) == "<ngoschema.datatypes.numerics.Integer type='integer' maximum=0>"
    assert datatypes.Integer()(1) == 1
    assert datatypes.Integer()("1") == 1
    assert datatypes.Integer()("`1+1") == 2
    assert datatypes.Integer()("{{a}}", a=1) == 1
    assert datatypes.Integer(minimum=0, maximum=2)(1) == 1
    with pytest.raises(InvalidValue) as e_info:
        datatypes.Integer(maximum=0)(1) == 1

    assert datatypes.String()(1) == "1"
    assert datatypes.String()("hello world!") == "hello world!"
    assert datatypes.String()("hello {{name}}!", name='world') == 'hello world!'
    assert datatypes.String()("hello {{name}}!", name='world', raw_literals=True) == "hello {{name}}!"
    with pytest.raises(ValidationError) as e_info:
        assert datatypes.String(maxLength=5)("hello {{name}}!", name='world') == 'hello world!'

    assert datatypes.Boolean.check('TRUE', convert=True)
    assert datatypes.Boolean.check('false', convert=True)
    assert not datatypes.Boolean.check('not a boolean', convert=True)
    assert datatypes.Boolean()(True) is True
    assert datatypes.Boolean()(False) is False
    assert datatypes.Boolean()('true', convert=True) is True
    assert datatypes.Boolean()('TRUE', convert=True) is True
    assert datatypes.Boolean()('false', convert=True) is False

    assert datatypes.Number()(2.3) == pytest.approx(decimal.Decimal('2.3')), datatypes.Number()(2.3)
    with pytest.raises(InvalidValue) as e_info:
        assert datatypes.Number(maximum=2)(2.3)

    t = datatypes.Type(type='string')
    assert repr(t) == "ngoschema.datatypes.type.Type(type='string')"
    assert str(t) == "<ngoschema.datatypes.type.Type type='string'>"
    assert datatypes.Type(type='string')(1) == '1', datatypes.Type(type='string')(1)
    assert datatypes.Type(type='integer', minimum=0)(1) == 1
    assert datatypes.Type(type='number')(1) == 1
    assert isinstance(datatypes.Type(type='boolean')(1), bool)


def test_complex():
    Path = datatypes.Path()
    PathFileExists = datatypes.PathFileExists()
    assert Path(__file__) == pathlib.Path(__file__)
    assert PathFileExists(__file__) == pathlib.Path(__file__)
    assert Path('{{user_directory}}', user_directory='.') == pathlib.Path('.')
    assert Path(pathlib.Path('{{user_directory}}'), user_directory='.') == pathlib.Path('.')

    Datetime = datatypes.Datetime()
    dt = datetime(2018, 5, 26, 11, 11, 11)
    a_dt = arrow.get(dt)

    assert Datetime(dt), dt
    assert isinstance(Datetime(dt), arrow.Arrow)
    assert Datetime(a_dt), a_dt
    assert isinstance(Datetime(a_dt), arrow.Arrow)

    Time = datatypes.Time()
    t = time(11, 11, 11)
    dt_t = datetime(1, 1, 1, 11, 11, 11)
    a_t = arrow.get(dt_t)
    assert Time(t) == t, t
    assert Time(dt_t) == t, dt_t
    assert Time(a_t) == t, a_t

    Date = datatypes.Date()
    d = date(2018, 5, 26)
    a_d = arrow.get(d)
    dt_d = a_d.datetime
    assert Date(d) == d, d
    assert Date(a_d) == d, a_d
    assert Date(dt_d) == d, dt_d


def test_array():
    ArrayString = datatypes.Array(items={'type': 'string'})
    ArrayInteger = datatypes.Array(items={'type': 'integer'})
    ArrayInteger5 = datatypes.Array(items={'type': 'integer'}, minItems=5, maxItems=5)
    #print("|%s|" % repr(ArrayString))
    #print("|%s|" % str(ArrayString))
    #print("|%s|" % repr(ArrayInteger5))
    assert repr(ArrayString) == "ngoschema.datatypes.array.Array(type='array', items={'type': 'string'})"
    assert str(ArrayString) == "<ngoschema.datatypes.array.Array type='array' items{1}>"
    assert repr(ArrayInteger5) == "ngoschema.datatypes.array.Array(type='array', items={'type': 'integer'}, minItems=5, maxItems=5)", repr(ArrayInteger5)
    assert ArrayInteger([1, '2', '{{a}}', '`a'], a=1) == [1, 2, 1, 1], ArrayInteger([1, '2', '{{a}}', '`a'], a=1)
    assert ArrayString([1, '2', '{{a}}', '`a'], a=1) == ['1', '2', '1', '1']
    #with pytest.raises(InvalidValue) as e_info:
    #    ArrayInteger5([1, '2', '{{a}}', '`a'], a=1)
    assert ArrayInteger5.default() == [None, None, None, None, None], ArrayInteger5.default()
    # below should be the result if the integer had a default value set to 0
    #assert ArrayInteger5._default() == [0, 0, 0, 0, 0], ArrayInteger5._default()


def test_object():
    from ngoschema.datatypes import Object
    o = {'a': '1', 'b': 1}
    obj = Object()
    #assert obj(o) == o, obj(o)
    #assert obj(**o) == o, obj(o)

    obj2 = Object(properties={'a': datatypes.Integer})
    assert obj2(o)['a'] == 1
    obj3 = Object(required=['c'])
    with pytest.raises(InvalidValue) as e_info:
        obj3(o, convert=False)
    assert obj3(o, convert=True) == {'a': '1', 'b': 1, 'c': None}
    assert obj3.default() == OrderedDict(c=None)


def test_canonical_name():
    from ngoschema.contexts import ObjectProtocolContext as Context
    from ngoschema.datatypes.foreign_key import CanonicalName
    b = {'name': 'b'}
    a = 'a value'
    context = Context({
        'A': {
            'a': a,
            0: b
        }
    })
    cn = CanonicalName()
    assert cn.resolve('A.b', context) == b
    assert cn.resolve('A.a', context) == 'a value'
    with pytest.raises(InvalidValue) as e_info:
        cn.resolve('A.c')


if __name__ == '__main__':
    #test_canonical_name()
    test_object()
    test_base()
    test_array()
    test_complex()

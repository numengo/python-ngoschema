import pytest
from ngoschema.exceptions import *
from ngoschema import types
import ngoschema.types.symbols as symbols

from collections import OrderedDict
import pathlib
import decimal
from urllib.parse import ParseResult
from datetime import datetime, date, time
import arrow


def test_base():
    assert types.Integer()(1) == 1
    assert types.Integer()("1") == 1
    assert types.Integer()("`1+1") == 2
    assert types.Integer()("{{a}}", a=1) == 1
    assert types.Integer(minimum=0, maximum=2)(1) == 1
    with pytest.raises(InvalidValue) as e_info:
        types.Integer(maximum=0)(1) == 1

    assert types.String()(1) == "1"
    assert types.String()("hello world!") == "hello world!"
    assert types.String()("hello {{name}}!", name='world') == 'hello world!'
    assert types.String()("hello {{name}}!", name='world', raw_literals=True) == "hello {{name}}!"
    with pytest.raises(ValidationError) as e_info:
        assert types.String(maxLength=5)("hello {{name}}!", name='world') == 'hello world!'

    assert types.Boolean.check('TRUE', convert=True)
    assert types.Boolean.check('false', convert=True)
    assert not types.Boolean.check('not a boolean', convert=True)
    assert types.Boolean()(True) is True
    assert types.Boolean()(False) is False
    assert types.Boolean()('true', convert=True) is True
    assert types.Boolean()('TRUE', convert=True) is True
    assert types.Boolean()('false', convert=True) is False

    assert types.Number()(2.3) == pytest.approx(decimal.Decimal('2.3')), types.Number()(2.3)
    with pytest.raises(InvalidValue) as e_info:
        assert types.Number(maximum=2)(2.3)

    assert types.Type(type='string')(1) == '1', types.Type(type='string')(1)
    assert types.Type(type='integer', minimum=0)(1) == 1
    assert types.Type(type='number')(1) == 1
    assert isinstance(types.Type(type='boolean')(1), bool)


def test_complex():
    Path = types.Path()
    PathFileExists = types.PathFileExists()
    assert Path(__file__) == pathlib.Path(__file__)
    assert PathFileExists(__file__) == pathlib.Path(__file__)
    assert Path('{{user_directory}}', user_directory='.') == pathlib.Path('.')
    assert Path(pathlib.Path('{{user_directory}}'), user_directory='.') == pathlib.Path('.')

    Datetime = types.Datetime()
    dt = datetime(2018, 5, 26, 11, 11, 11)
    a_dt = arrow.get(dt)

    assert Datetime(dt), dt
    assert isinstance(Datetime(dt), arrow.Arrow)
    assert Datetime(a_dt), a_dt
    assert isinstance(Datetime(a_dt), arrow.Arrow)

    Time = types.Time()
    t = time(11, 11, 11)
    dt_t = datetime(1, 1, 1, 11, 11, 11)
    a_t = arrow.get(dt_t)
    assert Time(t) == t, t
    assert Time(dt_t) == t, dt_t
    assert Time(a_t) == t, a_t

    Date = types.Date()
    d = date(2018, 5, 26)
    a_d = arrow.get(d)
    dt_d = a_d.datetime
    assert Date(d) == d, d
    assert Date(a_d) == d, a_d
    assert Date(dt_d) == d, dt_d


def test_array():
    ArrayString = types.Array(items={'type': 'string'})
    ArrayInteger = types.Array(items={'type': 'integer'})
    ArrayInteger5 = types.Array(items={'type': 'integer'}, minItems=5, maxItems=5)
    assert repr(ArrayInteger5) == "ngoschema.types.array.Array(type='array', items={'type': 'integer'}, minItems=5, maxItems=5)", repr(ArrayInteger5)
    assert ArrayInteger([1, '2', '{{a}}', '`a'], a=1) == [1, 2, 1, 1], ArrayInteger([1, '2', '{{a}}', '`a'], a=1)
    assert ArrayString([1, '2', '{{a}}', '`a'], a=1) == ['1', '2', '1', '1']
    with pytest.raises(InvalidValue) as e_info:
        ArrayInteger5([1, '2', '{{a}}', '`a'], a=1)
    assert ArrayInteger5._default() == [0, 0, 0, 0, 0], ArrayInteger5._default()


def test_object():
    from ngoschema.types import Object
    o = {'a': '1', 'b': 1}
    obj = Object()
    assert obj(o) == o, obj(o)
    assert obj(**o) == o, obj(o)

    obj2 = Object(properties={'a': types.Integer})
    assert obj2(o)['a'] == 1
    with pytest.raises(InvalidValue) as e_info:
        assert 'c' in Object(required=['c'])(o)
    assert Object(required=['c'])._default() == OrderedDict(c=None)


def test_canonical_name():
    from ngoschema.managers.context import Context
    from ngoschema.types.foreign_key import CanonicalName
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
    test_array()
    test_base()
    test_complex()

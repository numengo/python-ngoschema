import os.path
import pathlib
from datetime import date
from datetime import datetime
from datetime import time

import arrow
import pytest  # noqa
import python_jsonschema_objects as pjo

from ngoschema import get_resolver
from ngoschema.classbuilder import ClassBuilder


def test_path():
    schema = {
        "title": "Path Example",
        "type": "object",
        "properties": {
            "listPath": {
                "type": "array",
                "items": {
                    "type": "path"
                }
            },
            "anyPath": {
                "type": "path"
            },
            "existingPath": {
                "type": "path",
                "isPathExisting": True
            },
            "dirPath": {
                "type": "path",
                "isPathDir": True
            },
        },
    }
    builder = ClassBuilder(get_resolver())
    PE = builder.construct("PathExample", schema)

    fp = os.path.abspath(__file__)
    dp = os.path.dirname(fp)

    pe = PE()
    pe.anyPath = "really any path"
    assert isinstance(pe.anyPath._value, pathlib.Path)
    pe.anyPath.exists()
    with pytest.raises(pjo.ValidationError):
        pe.existingPath = "really any path"
    pe.existingPath = fp
    assert isinstance(pe.existingPath._value, pathlib.Path)
    with pytest.raises(pjo.ValidationError):
        pe.dirPath = fp
    pe.dirPath = dp
    assert isinstance(pe.existingPath._value, pathlib.Path)
    pe.listPath = ["really any path", fp, dp]
    for p in pe.listPath:
        assert isinstance(p._value, pathlib.Path)


def test_datetime():
    schema = {
        "title": "Date Time Example",
        "type": "object",
        "properties": {
            "date": {
                "type": "date"
            },
            "time": {
                "type": "time"
            },
            "datetime": {
                "type": "datetime"
            },
        },
    }

    builder = ClassBuilder(get_resolver())
    DTE = builder.construct("DateTimeExample", schema)

    d = date(2018, 5, 26)
    a_d = arrow.get(d)
    dt_d = a_d.datetime

    t = time(11, 11, 11)
    dt_t = datetime(1, 1, 1, 11, 11, 11)
    a_t = arrow.get(dt_t)

    dt = datetime(2018, 5, 26, 11, 11, 11)
    a_dt = arrow.get(dt)

    dte = DTE()

    # takes time
    dte.time = t
    # takes string formatted as time
    dte.time = "11:11"
    assert dte.time.hour == 11
    assert dte.time.minute == 11
    assert isinstance(dte.time._value, time)
    # takes datetime with no date
    dte.time = dt_t
    assert isinstance(dte.time._value, time)
    # takes arrow with no date
    dte.time = a_t
    assert isinstance(dte.time._value, time)
    # doesn t take date
    with pytest.raises(pjo.ValidationError):
        dte.time = d
    # doesn t take datetime with date
    with pytest.raises(pjo.ValidationError):
        dte.time = dt

    # takes date
    dte.date = d
    # takes string formatted as date
    dte.date = "2018/05/26"
    assert dte.date.year == 2018
    assert dte.date.month == 5
    assert dte.date.day == 26
    assert isinstance(dte.date._value, date)
    dte.date = "26/05/2018"
    assert dte.date.year == 2018
    assert dte.date.month == 5
    assert dte.date.day == 26
    # takes datetime with no time
    dte.date = dt_d
    assert not isinstance(dte.date, date)
    assert isinstance(dte.date._value, date)
    # takes arrow with no time
    dte.date = a_d
    assert isinstance(dte.date._value, date)
    # doesn t take time
    with pytest.raises(pjo.ValidationError):
        dte.date = t
    # take only date from datetime with time
    dte.date = dt
    assert isinstance(dte.date._value, date)

    # takes date
    dte.datetime = d
    assert isinstance(dte.datetime._value, arrow.Arrow)
    # takes datetime
    dte.datetime = dt
    assert isinstance(dte.datetime._value, arrow.Arrow)
    # takes arrow
    dte.datetime = a_dt
    assert isinstance(dte.datetime._value, arrow.Arrow)

def test_literal():
    from ngoschema import Path
    p = Path('/Users/cedric/Devel/admin/NUMENGO/NGOSCHEMA/url.mm')
    assert p.to_uri()

if __name__ == "__main__":
    #test_path()
    #test_datetime()
    test_literal()

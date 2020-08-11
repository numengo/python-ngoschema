# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import arrow
import pathlib
import urllib.parse

from ..exceptions import ValidationError, InvalidValue
from .type import Type, TypeChecker
from .literals import String, Literal
from .. import settings


@TypeChecker.register('uri')
class Uri(Literal):
    """
    Add additional 'uri' to json-schema associated in python to urllib.parse.ParseResult
    """
    _schema = {'type': 'uri'}
    _py_type = urllib.parse.ParseResult

    @classmethod
    def check(cls, value, **opts):
        """
        Checks value type against urllib.parse.ParseResult, pathlib.Path and String
        :param value: value to test
        :return: True if compatible
        """
        return super().check(value, **opts) or isinstance(value, pathlib.Path)

    @staticmethod
    def convert(value, **opts):
        """
        Convert from pathlib.Path using as_uri of force to string before parsing using urllib.parse.urlparse

        :param value: value to instanciate
        :param context: evaluation context
        :return: urllib.parse.ParsedResult instance
        """
        if not isinstance(value, urllib.parse.ParseResult):
            s = value.resolve().as_uri() if isinstance(value, pathlib.Path) else String.convert(value, **opts)
            return urllib.parse.urlparse(s)
        return value

    def serialize(self, value, **opts):
        """
        returns for json using urllib.parse.ParsedResult.geturl
        :param value: value (typed or not)
        :param context: evaluation context
        :return: json data
        """
        return self.convert(value, **opts).geturl()


@TypeChecker.register('path')
class Path(Uri):
    """
    Add additional 'path' to json-schema associated in python to pathlib.Path
    """
    _schema = {'type': 'path'}
    _py_type = pathlib.Path

    @staticmethod
    def convert(value, **opts):
        """
        convert from urllib.parse.ParsedResult, unquoting the url.
        """
        typed = value
        if isinstance(typed, urllib.parse.ParseResult):
            typed = pathlib.Path(urllib.parse.unquote(typed.geturl()))
        elif typed:
            typed = pathlib.Path(String.convert(str(typed), **opts))
        return typed

    def __call__(self, value, expand_user=False, resolve=False, validate=True, **opts):
        """
        convert and eventually resolve path from from urllib.parse.ParsedResult, unquoting the url.

        :param value: value to instanciate
        :param expand_user: expand user path
        :param resolve: resolve the path
        :return: pathlib.Path instance
        """
        typed = Type.__call__(self, value, validate=False, **opts)
        if expand_user:
            typed = typed.expanduser()
        if resolve:
            typed = typed.resolve()
        if validate:
            self.validate(typed)
        return typed

    def serialize(self, value, **opts):
        return str(value)

PathExists = Path.extend_type('PathExists', isPathExisting=True)
PathDir = Path.extend_type('PathDir', isPathDir=True)
PathFile = Path.extend_type('PathFile', isPathFile=True)
PathDirExists = PathDir.extend_type('PathDirExists', isPathExisting=True)
PathFileExists = PathDir.extend_type('PathFileExists', isPathExisting=True)


def _serialize(cls, value, **opts):
    format = opts.get('format') or cls._schema.get('format')
    format = settings.DATETIME_FORMATS.get(format, format)
    if format:
        if '%' in format:
            return value.strftime(format)
        else:
            return value.format(format)
    return value.isoformat()


@TypeChecker.register('date')
class Date(Literal):
    """
    Add additional 'date' to json-schema associated in python to datetime.date
    """
    _schema = {'type': 'date'}
    _py_type = datetime.date

    @classmethod
    def check(cls, value, **opts):
        return super().check(value, **opts) or isinstance(value, (arrow.Arrow, datetime.datetime))

    @staticmethod
    def convert(value, **opts):
        if isinstance(value, (arrow.Arrow, datetime.datetime)):
            assert value.time() == datetime.time(0, 0), value.time()
            return value.date()
        if isinstance(value, datetime.date):
            return value
        if String.check(value, **opts):
            value = String.convert(value, **opts)
            if value in settings.DATE_TODAY_STRINGS + settings.DATETIME_NOW_STRINGS:
                return arrow.utcnow().date()
            try:
                a = arrow.get(value, settings.DATE_FORMATS)
                assert a.time() == datetime.time(0, 0), a.time()
                return a.date()
            except Exception:
                try:
                    a = arrow.get(value, settings.ALT_DATE_FORMATS)
                    assert a.time() == datetime.time(0, 0), a.time()
                    return a.date()
                except Exception:
                    pass
        raise InvalidValue("{0} is not detected as a date: {1}".format(value))

    @classmethod
    def serialize(cls, value, **opts):
        return _serialize(cls, value, **opts)


@TypeChecker.register('time')
class Time(Literal):
    """
    Add additional 'time' to json-schema associated in python to datetime.time
    """
    _schema = {'type': 'time'}
    _py_type = datetime.time

    @classmethod
    def check(cls, value, **opts):
        return super().check(value, **opts) or isinstance(value, (arrow.Arrow, datetime.datetime))

    @staticmethod
    def convert(value, **opts):
        if isinstance(value, datetime.time):
            return value
        if isinstance(value, (datetime.datetime, arrow.Arrow)):
            assert value.date() == datetime.date(1, 1, 1)
            return value.time()
        if String.check(value, **opts):
            value = String.convert(value, **opts)
            if value in settings.DATETIME_NOW_STRINGS + settings.DATE_TODAY_STRINGS:
                a = arrow.utcnow()
                return a.time()
            try:
                a = arrow.get(value, settings.ALT_TIME_FORMATS)
                assert a.date() == datetime.date(1, 1, 1)
                return a.time()
            except Exception:
                pass
        raise InvalidValue("{0} is not detected as a time: {1}".format(value))

    @classmethod
    def serialize(cls, value, **opts):
        return _serialize(cls, value, **opts)


@TypeChecker.register('datetime')
class Datetime(Date, Time):
    """
    Add additional 'datetime' to json-schema associated in python to arrow.Arrow
    """
    _schema = {'type': 'datetime'}
    _py_type = arrow.Arrow

    @classmethod
    def check(cls, value, **opts):
        return Time.check(value, **opts)

    @staticmethod
    def convert(value, **opts):
        if isinstance(value, arrow.Arrow):
            return value
        if isinstance(value, datetime.datetime):
            return arrow.get(value)
        try:
            if String.check(value, **opts):
                value = String.convert(value, **opts)
                if value in settings.DATETIME_NOW_STRINGS:
                    return arrow.utcnow()
                if value in settings.DATE_TODAY_STRINGS:
                    return arrow.get(arrow.utcnow().date())
                a_d = arrow.get(value, settings.DATE_FORMATS + settings.ALT_DATE_FORMATS)
                a_t = arrow.get(value, settings.ALT_TIME_FORMATS)
                dt = datetime.datetime.combine(a_d.date(), a_t.time())
                return arrow.get(dt)
        except Exception as er:
            raise InvalidValue("{0} is not detected as a datetime: {1}".format(value, str(er)))

    @classmethod
    def serialize(cls, value, **opts):
        return _serialize(cls, value, **opts)

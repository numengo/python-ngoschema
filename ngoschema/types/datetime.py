# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import arrow

from ..exceptions import ValidationError, InvalidValue
from .type import TypeProtocol, Primitive
from ..managers.type_builder import register_type
from .strings import String
from .. import settings


def _dt_serialize(cls, value, **opts):
    format = opts.get('format') or cls._schema.get('format')
    format = settings.DATETIME_FORMATS.get(format, format)
    if format:
        if '%' in format:
            return value.strftime(format)
        else:
            return value.format(format)
    return value.isoformat() if value else None


@register_type('date')
class Date(Primitive):
    """
    Add additional 'date' to json-schema associated in python to datetime.date
    """
    _pyType = datetime.date

    @staticmethod
    def _check(self, value, **opts):
        if isinstance(value, (arrow.Arrow, datetime.datetime)) or TypeProtocol._check(self, value, **opts):
            return value
        raise TypeError('%s is not of type date.' % value)

    @staticmethod
    def _convert(self, value, **opts):
        if value is None:
            return value
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

    @staticmethod
    def _serialize(self, value, **opts):
        return _dt_serialize(self, value, **opts)


@register_type('time')
class Time(Primitive):
    """
    Add additional 'time' to json-schema associated in python to datetime.time
    """
    _pyType = datetime.time

    @staticmethod
    def _check(self, value, **opts):
        if isinstance(value, (arrow.Arrow, datetime.datetime)) or TypeProtocol._check(self, value, **opts):
            return value
        raise TypeError('%s is not of type date.' % value)

    @staticmethod
    def _convert(self, value, **opts):
        if value is None:
            return value
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

    @staticmethod
    def _serialize(self, value, **opts):
        return _dt_serialize(self, value, **opts)


@register_type('datetime')
class Datetime(Date, Time):
    """
    Add additional 'datetime' to json-schema associated in python to arrow.Arrow
    """
    _pyType = arrow.Arrow

    @staticmethod
    def _check(self, value, **opts):
        if isinstance(value, (arrow.Arrow, datetime.datetime)) or TypeProtocol._check(self, value, **opts):
            return value
        raise TypeError('%s is not of type date.' % value)

    @staticmethod
    def _convert(self, value, **opts):
        if value is None:
            return value
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

    @staticmethod
    def _serialize(self, value, **opts):
        return _dt_serialize(self, value, **opts)

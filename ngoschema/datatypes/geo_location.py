# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections.abc import Mapping, Sequence

from ..exceptions import ValidationError, InvalidValue
from .array import Tuple
from ..managers.type_builder import register_type
from .strings import String
from .numerics import Integer
from .. import settings


@register_type('geo_location')
class GeoLocation(Tuple):
    """
    Add additional 'geo_location' to json-schema associated
    """
    _minItems = 2
    _maxItems = 2
    _asString = False
    _asObject = False
    _strDelimiter = ','

    @staticmethod
    def _check(self, value, **opts):
        try:
            if isinstance(value, str):
                ret = value.split(',')
                if len(ret) == 2:
                    int(ret[0]), int(ret[1])
                    return value
            elif isinstance(value, Sequence):
                if len(value) == 2:
                    int(value[0]), int(value[1])
                    return value
            elif isinstance(value, Mapping):
                if 'longitude' in value and 'latitude' in value:
                    int(value['longitude']), int(value['latitude'])
                    return value
        except Exception as er:
            raise TypeError('%s is not of type location.' % value)

    @staticmethod
    def _convert(self, value, **opts):
        if value is None:
            return value
        try:
            if isinstance(value, str):
                ret = value.split(',')
                if len(ret) == 2:
                    return int(ret[0]), int(ret[1])
            elif isinstance(value, Sequence):
                if len(value) == 2:
                    return int(value[0]), int(value[1])
            elif isinstance(value, Mapping):
                if 'longitude' in value and 'latitude' in value:
                    return int(value['longitude']), int(value['latitude'])
        except Exception as er:
            raise InvalidValue("{0} is not detected as a location: {1}".format(value, str(er)))

    @staticmethod
    def _serialize(self, value, **opts):
        as_object = opts.get('as_object', self._asObject)
        if as_object:
            return {'longitude': value[0], 'latitude': value[1]}
        return Tuple._serialize(self, value, **opts)

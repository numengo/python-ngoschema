# *- coding: utf-8 -*-
from functools import partial
from python_jsonschema_objects import literals as pjo_literals

from . import utils
from .mixins import HasCache
from .validators import validator_registry, converter_registry, formatter_registry
from .decorators import memoized_property


def make_literal(name, subclass, base, **schema):
    validators_ = []

    type_ = 'enum' if 'enum' in schema else schema.get('type', 'string')
    converter_func = converter_registry(type_)

    def converter(value_):
        if converter_func:
            return converter_func(value_, schema)
        return value_

    type_ = schema.get('type', 'string')
    formatter_func = formatter_registry(type_)

    def formatter(value_):
        if formatter_func:
            return formatter_func(value_, schema)
        return value_

    for param, param_val in sorted(schema.items(), key=lambda x: x[0].lower() != "type"):
        validator_func = validator_registry(param)
        if validator_func is not None:
            validators_.append((validator_func, param_val))

    def validator(value_):
        for func, val in validators_:
            func(val, value_, schema)

    # need this to keep compliance with pjo
    propinfo = schema.copy()
    propinfo['__literal__'] = schema
    propinfo['__default__'] = schema.get('default')

    return type(
        str(name),
        tuple(base),
        {
            "__propinfo__": propinfo,
            "__subclass__": subclass,
            "_converter": staticmethod(converter),
            "_formatter": staticmethod(formatter),
            "_validator": staticmethod(validator),
        },
    )


class LiteralValue(pjo_literals.LiteralValue, HasCache):
    __subclass__ = None
    _typed = None

    def __init__(self, value=None):
        if isinstance(value, pjo_literals.LiteralValue):
            value = value._value

        if value is None and self.default() is not None:
            value = self.default()

        if value and utils.is_string(value) and utils.is_pattern(value):
            self.register_expr(value)

        self._value = value
        self.validate()

    def __repr__(self):
        return '<%s<%s> id=%s "%s">' % (
            self.__class__.__name__,
            self._value.__class__.__name__,
            id(self),
            str(self)
        )

    def __format__(self, format_spec):
        return self.for_json().__format__(format_spec)

    def __getattr__(self, name):
        """
        Special __getattr__ method to be able to use subclass methods
        directly on literal
        """
        sub_cls = object.__getattribute__(self, '__subclass__')
        cls = object.__getattribute__(self, '__class__')
        if hasattr(sub_cls, name):
            if isinstance(self._value, sub_cls):
                return getattr(self._value, name)
        elif hasattr(cls, name):
            return object.__getattribute__(self, name)
        else:
            return pjo_literals.LiteralValue.__getattribute__(self, name)

    def for_json(self):
        if self._validated_data is not None:
            return self._validated_data
        if self._formatter:
            return self._formatter(self._typed or self._value)
        return self._typed or self._value

    @memoized_property
    def enum(self):
        return self.__propinfo__['__literal__'].get('enum')

    def validate(self):
        return HasCache.validate(self)

    def _validate(self, data):
        self._typed = self._converter(data)

        # replace the more expensive call to pjo_literals.LiteralValue.validate
        self._validator(self._typed)

        self._validated_data = self._formatter(self._typed)
        return True

    def __eq__(self, other):
        return self._typed == other

    def __hash__(self):
        return hash(self._typed)

    def __lt__(self, other):
        return self._typed < other

    def __int__(self):
        return int(self._typed)

    def __float__(self):
        return float(self._typed)

    def __bool__(self):
        return bool(self._typed)

    __nonzero__ = __bool__


# EXPERIMENTAL: attempt
class TextField(object):
    def __new__(self, *args, **kwargs):
        schema = {'type': 'string'}
        schema.update(**kwargs)
        return make_literal('TextField', str, (LiteralValue, ), **schema)


class ImportableField(object):
    def __new__(self, *args, **kwargs):
        schema = {'type': 'importable'}
        schema.update(**kwargs)
        return make_literal('ImportableField', str, (LiteralValue, ), **schema)


class IntegerField(object):
    def __new__(self, *args, **kwargs):
        schema = {'type': 'string'}
        schema.update(**kwargs)
        return make_literal('IntegerField', str, (LiteralValue, ), **schema)


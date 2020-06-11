# *- coding: utf-8 -*-
from functools import partial
from python_jsonschema_objects import literals as pjo_literals, util as pjo_util
import copy
import urllib.parse
import pathlib
import types

from . import utils
from .mixins import HasCache
from .validators import validator_registry, converter_registry, formatter_registry
from .decorators import memoized_property


def _dispatch_to_typed(fn):
    def wrapper(self, other):
        return fn(self._typed, other)
        pass

    return wrapper


class PathMixin(object):
    def to_uri(self):
        return converter_registry('uri')(self._typed, {})


class UriMixin(object):
    @property
    def defrag(self):
        urlparsed = self._typed
        return urllib.parse.urlunsplit((*urlparsed[:4], '')), urlparsed.fragment

    def resolve_json(self, remote=False):
        from .resolver import resolve_uri
        return resolve_uri(self._typed.geturl(), remote=remote)

    def to_path(self):
        return converter_registry('path')(self._typed, {})


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
    attrs = {
            "__propinfo__": propinfo,
            "__subclass__": subclass,
            "_converter": staticmethod(converter),
            "_formatter": staticmethod(formatter),
            "_validator": staticmethod(validator),
        }


    # add method to path to return as uri
    if type_ == 'path':
        base = base + (PathMixin, subclass)

    # add a method to uri to defrag the uri
    if type_ == 'uri':
        base = base + (UriMixin, subclass)

    cls = type(str(name), tuple(base), attrs,)

    if type_ in ['uri', 'path', 'date', 'datetime', 'time']:
        for op in dir(subclass):
            if op not in pjo_literals.EXCLUDED_OPERATORS:
                fn = getattr(subclass, op)
                setattr(cls, op, _dispatch_to_typed(fn))

    return cls


class LiteralValue(pjo_literals.LiteralValue, HasCache):
    __subclass__ = None
    _typed = None

    def __init__(self, value=None, **opts):
        self._typed = None
        if isinstance(value, pjo_literals.LiteralValue):
            value = value._value

        if value is None and self.default() is not None:
            value = self.default()

        if value and utils.is_string(value) and utils.is_pattern(value):
            self.register_expr(value)

        self._value = value
        self.validate(**opts)

    def __repr__(self):
        return '<%s<%s> id=%s "%s">' % (
            self.__class__.__name__,
            self._value.__class__.__name__,
            id(self),
            str(self)
        )

    def __format__(self, format_spec):
        return self.for_json().__format__(format_spec)

    #def __getattr__(self, name):
    #    """
    #    Special __getattr__ method to be able to use subclass methods
    #    directly on literal
    #    """
    #    sub_cls = object.__getattribute__(self, '__subclass__')
    #    cls = object.__getattribute__(self, '__class__')
    #    if hasattr(sub_cls, name):
    #        if isinstance(self._typed, sub_cls):
    #            _ = copy.copy(self._typed)
    #            return getattr(_, name)
    #    elif hasattr(cls, name):
    #        return object.__getattribute__(self, name)
    #    else:
    #        return pjo_literals.LiteralValue.__getattribute__(self, name)

    def for_json(self):
        if self._validated_data is not None:
            return self._validated_data
        if self._formatter:
            return self._formatter(self._typed or self._value)
        return self._typed or self._value

    @memoized_property
    def enum(self):
        return self.__propinfo__['__literal__'].get('enum')

    def validate(self, **opts):
        raw_literals = opts.get('raw_literals', False)
        if self.is_dirty():
            inputs = self._inputs_data()
            data = self._value
            if not raw_literals:
                if self.has_expr():
                    data = self.eval_expr(**inputs) or data

            self._typed = self._converter(data)
            # replace the more expensive call to pjo_literals.LiteralValue.validate
            self._validator(self._typed)
            self._validated_data = self._formatter(self._typed)

            self._inputs_cached = inputs
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
        return bool(self._value)

    __nonzero__ = __bool__


""" We also have to patch the reverse operators,
which aren't conveniently defined anywhere """
LiteralValue.__radd__ = lambda self, other: other + self._typed
LiteralValue.__rsub__ = lambda self, other: other - self._typed
LiteralValue.__rmul__ = lambda self, other: other * self._typed
LiteralValue.__rtruediv__ = lambda self, other: other / self._typed
LiteralValue.__rfloordiv__ = lambda self, other: other // self._typed
LiteralValue.__rmod__ = lambda self, other: other % self._typed
LiteralValue.__rdivmod__ = lambda self, other: divmod(other, self._typed)
LiteralValue.__rpow__ = lambda self, other, modulo=None: pow(other, self._typed, modulo)
LiteralValue.__rlshift__ = lambda self, other: other << self._typed
LiteralValue.__rrshift__ = lambda self, other: other >> self._typed
LiteralValue.__rand__ = lambda self, other: other & self._typed
LiteralValue.__rxor__ = lambda self, other: other ^ self._typed
LiteralValue.__ror__ = lambda self, other: other | self._typed


# EXPERIMENTAL
def Text(*args, **schema):
    return make_literal('Text', str, (LiteralValue, ), type='text', **schema)(*args)


def Integer(*args, **schema):
    return make_literal('Integer', int, (LiteralValue, ), type='integer', **schema)(*args)


def Number(*args, **schema):
    return make_literal('Number', float, (LiteralValue, ), type='number', **schema)(*args)


def Importable(*args, **schema):
    return make_literal('Importable', str, (LiteralValue, ), type='importable', **schema)(*args)


def Path(*args, **schema):
    return make_literal('Path', pathlib.Path, (LiteralValue, ), type='path', **schema)(*args)


def Uri(*args, **schema):
    return make_literal('Uri', urllib.parse.ParseResult, (LiteralValue, ), type='uri', **schema)(*args)

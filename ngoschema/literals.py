# *- coding: utf-8 -*-
from functools import partial
from python_jsonschema_objects import literals as pjo_literals

from . import utils
from .mixins import HasCache
from .validators import validator_registry, converter_registry, formatter_registry
from .decorators import memoized_property
from .validators import pjo

def make_literal(name, subclass, base, **schema):
    converter = None
    formatter = None
    validators_ = []

    type_ = 'enum' if 'enum' in schema else schema.get('type', 'string')
    converter_func = converter_registry(type_)
    if converter_func:
        def converter(value_):
            return converter_func(value_, schema)

    type_ = schema.get('type', 'string')
    formatter_func = formatter_registry(type_)
    if formatter_func:
        def formatter(value_):
            return formatter_func(value_, schema)

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
    _converter = None
    _formatter = None
    _validator = None

    def __init__(self, value, _parent=None):
        HasCache.__init__(self, context=_parent, inputs=self.propinfo('dependencies'))

        if isinstance(value, LiteralValue):
            val = value._value
        else:
            val = value

        if val is None and self.default() is not None:
            val = self.default()

        if self._converter:
            val = self._converter(val)

        self._value = val
        self.validate()

    def __repr__(self):
        return '<%s<%s> id=%s validated=%s "%s">' % (
            self.__class__.__name__,
            self._value.__class__.__name__,
            id(self),
            self._validated,
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
        if self._formatter:
            return self._formatter(self._value)
        else:
            return self._value

    @memoized_property
    def enum(self):
        return self.__propinfo__['__literal__'].get('enum')

    @memoized_property
    def _is_importable(self):
        return self.__propinfo__['__literal__'].get('type') == 'importable'

    def validate(self):
        from .utils.jinja2 import TemplatedString
        val = self._value
        if '_pattern' in self.__dict__:
            try:
                val = TemplatedString(self._pattern)(
                    this=self._context,
                    **self._input_values)
            except Exception as er:
                # logger.info('evaluating pattern "%s" in literal: %s', self._pattern, er)
                val = self._pattern

        # replace the more expensive call to pjo_literals.LiteralValue.validate
        #pjo_literals.LiteralValue.validate(self)
        if self._validator:
            self._validator(val)

        # type importable: store imported as protected member
        if self._is_importable and not hasattr(self, '_imported'):
            self._imported = utils.import_from_string(self._value)

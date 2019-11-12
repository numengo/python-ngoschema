from python_jsonschema_objects import literals as pjo_literals

from . import utils
from .mixins import HasCache
from .validators import converter_registry

class LiteralValue(pjo_literals.LiteralValue, HasCache):
    __subclass__ = None

    def __init__(self, value, typ=None, _parent=None):
        HasCache.__init__(self, context=_parent, inputs=self.propinfo('dependencies'))

        if isinstance(value, LiteralValue):
            self._value = value._value
        else:
            self._value = value

        if self._value is None and self.default() is not None:
            self._value = self.default()

        if converter_registry.registry:
            info = self.propinfo('__literal__')
            type_ = 'enum' if 'enum' in info else info.get('type', 'string')
            converter = converter_registry(type_)
            if converter:
                self._value = converter(self, self._value, info)

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
        return self._value.__format__(format_spec)

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
        from . import validators
        if validators.formatter_registry.registry:
            info = self.propinfo('__literal__')
            formatter = validators.formatter_registry(info.get('type', 'string'))
            return formatter(self, self._value, info) if formatter else self._value
        else:
            return self._value

    @property
    def enum(self):
        info = self.propinfo('__literal__')
        return info.get('enum')

    def validate(self):
        from .utils.jinja2 import TemplatedString
        if '_pattern' in self.__dict__:
            try:
                self._value = TemplatedString(self._pattern)(
                    this=self._context,
                    **self._input_values)
            except Exception as er:
                # logger.info('evaluating pattern "%s" in literal: %s', self._pattern, er)
                self._value = self._pattern
        pjo_literals.LiteralValue.validate(self)
        # type importable: store imported as protected member
        if self.propinfo('__literal__').get('type') == 'importable' and not hasattr(self, '_imported'):
            self._imported = utils.import_from_string(self._value)

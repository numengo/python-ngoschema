
from .converter import Converter


class Transformer(Converter):
    _converter = Converter
    _fromClass = None
    _toClass = None

    def __init__(self, converter=Converter, fromClass=None, toClass=None, **opts):
        self._converter = converter
        self._converter.__init__(self, **opts)
        self._fromClass = fromClass or self._pyType
        self._toClass = toClass

    @staticmethod
    def _check(self, value, **opts):
        fromClass = opts.get('fromClass', self._fromClass)
        if not isinstance(value, fromClass):
            raise TypeError('%s if not of type %s' % (value, fromClass))
        return value

    @staticmethod
    def _transform(self, value, convert=True, **opts):
        value = self._convert(self, value, **opts) if convert else value
        toClass = opts.get('toClass', self._toClass)
        try:
            return toClass(value, **opts)
        except Exception as er:
            self._logger.error(er, exc_info=True)
            raise

    def __call__(self, value, **opts):
        return self._transform(self, value, **opts)

    @classmethod
    def transform(cls, value, convert=False, **opts):
        value = cls._convert(cls, value, **opts) if convert else value
        return cls._transform(cls, value, convert=convert, **opts)

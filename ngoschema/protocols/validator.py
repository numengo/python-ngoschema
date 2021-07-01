# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict
from copy import copy
import logging

from ..exceptions import InvalidValue, ValidationError, ConversionError
from ..utils import ReadOnlyChainMap, shorten
from ..managers.type_builder import DefaultValidator

from .converter import Converter
from .context import Context

logger = logging.getLogger(__name__)


class Validator(Converter, Context):
    _converter = Converter
    _default = None
    _schema = {}
    _jsValidator = DefaultValidator({})

    def __init__(self, converter=None, schema=None, context=None, **opts):
        from ..managers.type_builder import untype_schema, type_builder
        self._converter = converter or self._converter
        self._converter.__init__(self, **opts)
        Context.__init__(self, context, **opts)
        schema = untype_schema(schema or opts)
        self._schema = ReadOnlyChainMap(schema, self._schema)
        sch = dict(self._schema)
        type_builder.check_schema(sch)
        self._default = sch.get('default', self._default)
        self._jsValidator = DefaultValidator(sch)

    @staticmethod
    def _repr_schema(self, **opts):
        rs = OrderedDict(opts.get('schema', self._schema))
        if 'type' in rs:
            rs.move_to_end('type', False)
        return dict(rs)

    @classmethod
    def repr_schema(cls, **opts):
        return cls._repr_schema(cls, **opts)

    @staticmethod
    def _errors(self, value, excludes=[], with_type=True, **opts):
        """
        Validate the value according to schema
        Return dictionnary of errors or raise ngoschema.InvalidValue
        """
        if not with_type:
            excludes = list(excludes) + ['type']
        schema = {k: v for k, v in opts.get('schema', self._schema).items() if k not in excludes}
        return {'/'.join(e.schema_path): e.message
                for e in self._jsValidator.iter_errors(value, schema)}

    def _format_errors(self, value, **opts):
        errors = Validator._errors(self, value, **opts)
        if errors:
            return '\n'.join([f"Problem validating {self} with {shorten(value, 128, str_fun=repr)}:"]
                           + [f'\t{k}: {e}' for k, e in errors.items()])

    @staticmethod
    def _validate(self, value, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        msg = Validator._format_errors(self, value, **opts)
        if msg:
            raise InvalidValue(msg)
        return value

    @staticmethod
    def _evaluate(self, value, convert=True, validate=True, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        if value is None:
            if self._default is None:
                return None
            value = copy(self._default)
        value = self._convert(self, value, validate=False, **opts) if convert else value
        if validate:
            # value is not modified
            self._validate(self, value, with_type=False, **opts)
        return value

    def __call__(self, value, **opts):
        return self._evaluate(self, value, **opts)

    @classmethod
    def check(cls, value, convert=False, validate=False, **opts):
        try:
            value = cls._convert(cls, value, validate=False, **opts) if convert else value
            value = cls._check(cls, value, **opts)
            value = cls._validate(cls, value, with_type=False, **opts) if validate else value
            return True
        except Exception as er:
            p = False
            if p:
                logger.error(er, exc_info=True)
            return False

    @classmethod
    def evaluate(cls, value, **opts):
        return cls._evaluate(cls, value, **opts)

    @classmethod
    def validate(cls, value, with_type=True, **opts):
        return cls._validate(cls, value, with_type=with_type, **opts)

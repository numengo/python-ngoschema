# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from ..types import ObjectMetaclass, with_metaclass
from ..types.symbols import *


class Symbol(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/Symbol'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_importable
        return Importable(inspect_importable(value))


class Module(with_metaclass(ObjectMetaclass, Importable)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/modules/$defs/Module'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_module
        return Module(inspect_module(value))


class VariableType(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/VariableType'


class Variable(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/Variable'


class VariableValue(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/variables/$defs/VariableValue'


class Argument(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/functions/$defs/Argument'

    @classmethod
    def convert(cls, value, **opts):
        from ..inspect.doc_rest_parser import parse_docstring
        data = Variable.convert(value, **opts)
        doctype = data.pop('doctype', None)
        if doctype:
            data.update({k: v for k, v in parse_docstring(doctype).items() if v})
        return Object.convert(cls, data, **opts)


class Function(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/functions/$defs/Function'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_function
        return Function(inspect_function(value))


class FunctionCall(with_metaclass(ObjectMetaclass)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/functions/$defs/FunctionCall'


    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_function_call
        return FunctionCall(inspect_function_call(value))


class Class(with_metaclass(ObjectMetaclass, Importable)):
    _schema_id = 'https://numengo.org/ngoschema/inspect#/$defs/classes/$defs/Class'

    @staticmethod
    def inspect(value):
        from ..inspect.inspect_symbols import inspect_class
        return Class(inspect_class(value))

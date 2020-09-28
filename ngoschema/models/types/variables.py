# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from ...protocols import SchemaMetaclass, with_metaclass, ObjectProtocol


class Value(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/variables/$defs/Value'


class Variable(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/variables/$defs/Variable'


class VariableValue(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/variables/$defs/VariableValue'

    def json_schema(self):
        return self.valueLiteral


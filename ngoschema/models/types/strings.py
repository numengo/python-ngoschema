# *- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from ...protocols import SchemaMetaclass, with_metaclass


class String(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/strings/$defs/String'


class RawString(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/strings/$defs/RawString'


class Expr(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/strings/$defs/Expr'


class Pattern(with_metaclass(SchemaMetaclass)):
    _id = 'https://numengo.org/ngoschema#/$defs/types/$defs/strings/$defs/Pattern'

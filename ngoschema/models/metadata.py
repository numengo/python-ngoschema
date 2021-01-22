# *- coding: utf-8 -*-
"""
Foreign key component

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 28/01/2019
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from future.utils import with_metaclass
import sys
import weakref

from .. import settings
from ..decorators import classproperty, depend_on_prop
from ..protocols import SchemaMetaclass, ObjectProtocol

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


class Annotation(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/Annotation"


class Name(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/Name"


class Id(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/Id"


class Plural(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/metadata/$defs/Plural"

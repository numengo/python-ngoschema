# *- coding: utf-8 -*-
import os.path

from future.utils import with_metaclass

from .classbuilder import ProtocolBase
from .schema_metaclass import SchemaMetaclass

dirpath = os.path.dirname(os.path.realpath(__file__))


class Project(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaPath = os.path.join(dirpath, "../../tests/schemas/project.json")

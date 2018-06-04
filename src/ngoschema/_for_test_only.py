# *- coding: utf-8 -*-
import os.path
from future.utils import with_metaclass
from .schema_metaclass import SchemaMetaclass
from .classbuilder import ProtocolBase

dirpath = os.path.dirname(os.path.realpath(__file__))

class Project(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaPath = os.path.join(dirpath,'../../tests/schemas/project.json')


# -*- coding: utf-8 -*-
from future.utils import with_metaclass
import pytest
import logging
logging.basicConfig(level=logging.INFO)

from ngoschema import ValidationError, ProtocolBase
from ngoschema import SchemaMetaclass

def hybrid_class():
    """Build a hybrid class from a json-schema with overloaded setters/getters
    Test type validation
    """
    class A(with_metaclass(SchemaMetaclass, ProtocolBase)):
        schema = {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer'
                },
                'name': {
                    'type': 'string'
                }
            },
            'readOnly': ['count']
        }

        # private and protected members start with _ or __ and can be set with no checks
        _count = 0
        def get_count(self):
            self._count += 1
            return self._count

        def set_name(self, value):
            # value is already set and converted to Literal and accessible with
            # _get_prop_value
            # here can be done any specific treatment
            modified = value.upper()
            # value can be set using _set_prop_value
            print('HELLO %s!' % modified)
            self._set_prop_value('name', modified)

    a = A()

    # the getter increments the protected variable each time
    assert a.count == 1
    assert a.count == 2

    a.name = 'World'
    # the setter is called and the value uppercased
    assert a.name == 'WORLD'

def external_schema_class():
    """create a class from a schema stored in a file or available online"""

    class B(with_metaclass(SchemaMetaclass, ProtocolBase)):
        """An external schema can be referred using the __schema_uri__ class argument
        The resolver will look for the schema in schemas loaded using
        load_module_schemas.
        In this case, load_module_schemas is called when importing ngoschema, and all
        schemas available in ngoschema/schemas were loaded. Schemas are then referred
        using their $id or id argument, which is the URI where it is supposed to be
        available online.
        In this case, the file in ngoschema/schemas/Document.json was loaded and found
        through its id which was registered among all other schemas and metaschemas.
        Other schema loaders are available to load a json-schema, a file or a directory.
        """
        __schema_uri__ = r'http://numengo.org/ngoschema/draft-05/document#/definitions/Document'

    # schema has an attribute author
    b1 = B(author="Sam")
    b2 = B(author="Max")
    # we can use get and list class method to query for a specific instance
    assert B.get(author="Sam") is b1

if __name__ == "__main__":
    hybrid_class()
    external_schema_class()

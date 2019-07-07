=====
Usage
=====

To add a schema to a class, user needs to have the class use the ``SchemaMetaClass``

.. code-block:: python

    from future.utils import with_metaclass
    from ngoschema import SchemaMetaclass, ProtocolBase

    class MyCardClass(with_metaclass(SchemaMetaclass, ProtocolBase)):
        __schema__ = "http://json-schema.org/card"

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, **kwargs)


The schema can be indicated using different fields:
* ``__schema__`` indicates a URI that the resolver will look for in the
schema store. The library comes with a derived resolver which automatically looks
for some schemas to load. see ``ngoschema.resolver``
* ``__schema_path__`` indicates a path to a file containing the schema

The class should always inherit from ``with_metaclass(SchemaMetaclass, Parent1, Parent2)``

If user redefines the ``__init__`` method, it should always call the ProtocolBase
initialization method.

User can't define additional public properties, but is free to do anything with protected or private properties.



SchemaMetaClass will build the class doing a lot of magic:
* it adds a logger that can be accessed with self.logger
* it adds proper logging and exception handling to all methods 
* it add type conversion/checking and data validation to methods according to their
documentation



Generated Classes
-----------------

Classes generated using ``ngoschema`` expose all defined
properties as both attributes and through dictionary access.

In addition, classes contain a number of utility methods for serialization,
deserialization, and validation.

.. autoclass:: ngoschema.schema_metaclass.SchemaMetaclass
    :members:

.. autoclass:: ngoschema.classbuilder.ClassBuilder
    :members:

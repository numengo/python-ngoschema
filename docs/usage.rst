=====
Usage
=====
To build a class from a schema, user can call the ``ClassBuilder`` using ``get_builder`` as:

.. code-block:: python
    >>> from ngoschema import get_builder

    >>> Counter = get_builder().construct('Counter', {
    ...        'type': 'object',
    ...        'additionalProperties': False,
    ...        'properties': {
    ...            'count': {'type': 'integer', 'minimum': 0}
    ...        }
    ...    })

    >>> c = Counter()
    >>> c.count = 1
    >>> c.count = -1
    Traceback (most recent call last):
        ...
    python_jsonschema_objects.validators.ValidationError: -1 is less than 0

User can register json files as schemas in his module using ``load_module_schemas("{module_folder}")`` in the module ``__init__.py``.

A proper JSON-schema document should have a property ``$id`` set to `an absolute URI (it s domain/namespace) <https://json-schema.org/understanding-json-schema/structuring.html#the-id-property>`_.

To add a schema to a class, user needs to have the class use the ``SchemaMetaclass`` and can build a class refering to a
domain/namespace which will be looked first in the available modules schemas, and eventually on-line.
Some schemas from `json-schema.org <https://json-schema.org/>`_ are included in the schemas directory of the module.


The library adds some meta-programing to create instrumented classes following a ``ProtocolBase``
One could create a class extending the Card class from `json-schema.org <https://json-schema.org/>`_ as follows:

.. code-block:: python

    from future.utils import with_metaclass
    from ngoschema import SchemaMetaclass, ProtocolBase

    class MyCardClass(with_metaclass(SchemaMetaclass, ProtocolBase)):
        __schema__ = "http://json-schema.org/card"




The schema can be indicated using different fields:
* ``__schema__`` indicates a URI that the resolver will look for in the
schema store. The library comes with a derived resolver which automatically looks
for some schemas to load. see ``ngoschema.resolver``
* ``__schema_path__`` indicates a path to a file containing the schema

The class should always inherit from ``with_metaclass(SchemaMetaclass, Parent1, Parent2)``

If user redefines the ``__init__`` method, it should always call the ProtocolBase
initialization method.

User can't define additional public properties, but is free to do anything with protected or private properties.


``SchemaMetaclass`` will build the class doing a lot of magic:
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

.. autoclass:: ngoschema.protocol_base.ProtocolBase
    :members:

.. autoclass:: ngoschema.wrapper_types.ArrayWrapper
    :members:

.. autoclass:: ngoschema.literals.LiteralValue
    :members:

Schemas
=========

The library intends to deal with complex schemas, possibly using inheritance which is
not yet supported in JSON Schema, as well as data types which can be useful in generated class.

For this purpose, a meta-schema is built on top of the standard ones, adding specific
features, but which won't be recognized by standard validators. Though, the schema
valid against this meta-schema should usually be processed without problem by standard
validation libraries (with warnings for the unknown field) with the exception.

The additional grammar adds:
    * extra object attributes:
        - ``isAbtract`` boolean to indicate an abstract class.
        - ``extends`` allowing to specify the ``id`` of parent classes.
        - ``readOnly`` and ``notSerialized`` to specify properties which cannot beset or are not serialized.
    * extra literal types (``date``, ``time``, ``datetime``, ``path``, ``importable``).
    * extra property attributes for specific types:
        - ``isPathDir`` boolean to indicate the path of a directory
        - ``isPathFile`` boolean to indicate the path of a file
        - ``isPathExisting`` boolean to indicate an existing path
        - ``foreignKey`` dictionary of options to define a foreign key to another object

It also comes with a few definitions that can be useful in a `Domain-Driven Design implementation <https://en.wikipedia.org/wiki/Domain-driven_design>`_.

This meta-schema is available as ``https://numengo.org/ngoschema <https://numengo.org/ngoschema#``
and can be optionally referred as `$schema <https://json-schema.org/understanding-json-schema/basics.html#declaring-a-json-schema>`_.
in the definitions (instead of the standard `draft <https://json-schema.org/understanding-json-schema/index.html>`_)

Additional types are available for literals, and can then be used already properly casted in further code. Those types are mapped as follows:
    * ``date``: ``datetime.date``
    * ``datetime``: ``datetime.datetime``
    * ``time``: ``datetime.time``
    * ``time``: ``datetime.time``
    * ``path``: ``pathlib.Path``


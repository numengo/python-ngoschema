Schemas
=======

The library intends to deal with complex schemas, possibly using inheritance which is 
not yet supported in JSON Schema, as well as data types which can be useful in generated class.

For this purpose, a meta-schema is built on top of the standard ones, adding specific 
features, but which won't be recognized by standard validators. Though, the schema 
valid against this meta-schema should usually be processed without problem by standard 
validation libraries (with warnings for the unknow field) with the exception



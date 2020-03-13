
schema = {
    'type': 'object',
    'readOnly': ['canonicalName'],
    'properties': {
        'name': {
            'type': 'string',
            'default': '<anonymous>'
        },
        'canonicalName': {
            'type': 'string',
            'default': '{% if this.parent %}{{ this.parent.canonicalName }}.{% endif %}{{this.name}}',
        },
        'parent': {'$ref': '#'}
    }
}

from future.utils import with_metaclass
from ngoschema import get_builder, SchemaMetaclass, ProtocolBase


NamedClass = get_builder().construct('#', schema, (ProtocolBase, ))

a = NamedClass()
assert a.name == '<anonymous>'
a.name = 'a'
assert a.name == 'a', a.name
b = NamedClass(name='b')
assert b.canonicalName == 'b', b.canonicalName
b.parent = a
assert b.canonicalName == 'a.b', b.canonicalName

a.name = 'A'
assert a.name == 'A'
assert b.canonicalName == 'A.b', b.canonicalName

b.parent.name = 'a'
assert a.name == 'a'

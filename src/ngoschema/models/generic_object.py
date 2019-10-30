from __future__ import print_function
from __future__ import unicode_literals

from ..classbuilder import get_builder

from ..protocol_base import ProtocolBase


GenericObject = get_builder().construct(
    'http://numengo.org/draft-05/generic-object#/definitions/GenericObject',
    {
        'type': 'object',
        'description': 'generic extensible object',
        'additionalProperties': True
    },
    parent=(ProtocolBase, ))

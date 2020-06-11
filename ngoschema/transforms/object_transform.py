from abc import abstractmethod

from future.utils import with_metaclass
#from ngoschema import utils, get_builder, SchemaMetaclass, ProtocolBase
from ngoschema.utils import GenericClassRegistry
from ..types import ObjectMetaclass


class ObjectTransform(with_metaclass(ObjectMetaclass)):
    """
    Class to do simple model to model transformation
    """
    _schema_id = "https://numengo.org/ngoschema/object-transform#/$defs/ObjectTransform"

    #def __init__(self, **kwargs):
    #    ProtocolBase.__init__(self, **kwargs)

    @abstractmethod
    def __call__(self, src, *args):
        raise Exception("must be overloaded")

    @classmethod
    def transform(cls, src, *args, **kwargs):
        return cls(**kwargs)(src, *args)


transform_registry = GenericClassRegistry()

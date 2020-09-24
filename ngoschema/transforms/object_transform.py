from abc import abstractmethod

from future.utils import with_metaclass
#from ngoschema import utils, get_builder, SchemaMetaclass, ProtocolBase
from ngoschema.utils import GenericClassRegistry
from ..protocols import SchemaMetaclass


class ObjectTransform(with_metaclass(SchemaMetaclass)):
    """
    Class to do simple model to model transformation
    """
    _id = "https://numengo.org/ngoschema#/$defs/transforms/$defs/ObjectTransform"

    #def __init__(self, **kwargs):
    #    ProtocolBase.__init__(self, **kwargs)

    @abstractmethod
    def __call__(self, src, *args, **kwargs):
        raise Exception("must be overloaded")

    @classmethod
    def transform(cls, src, *args, **kwargs):
        try:
            return cls(**kwargs)(src, *args)
        except Exception as er:
            cls._logger.error(er, exc_info=True)
            raise


transform_registry = GenericClassRegistry()

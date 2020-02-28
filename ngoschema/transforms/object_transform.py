from abc import abstractmethod

from future.utils import with_metaclass
from ngoschema import utils, get_builder, SchemaMetaclass, ProtocolBase
from ngoschema.utils import GenericClassRegistry


class ObjectTransform(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to do simple model to model transformation
    """
    __schema_uri__ = "http://numengo.org/ngoschema/object-transform#/definitions/ObjectTransform"

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)
        self._from_cls = self.from_._imported if self.from_ else None
        self._to_cls = self.to_._imported if self.to_ else None

    @abstractmethod
    def __call__(self, src, *args):
        raise Exception("must be overloaded")

    @classmethod
    def transform(cls, src, *args, **kwargs):
        return cls(**kwargs)(src, *args)


transform_registry = GenericClassRegistry()

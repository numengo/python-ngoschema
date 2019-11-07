from abc import abstractmethod

from future.utils import with_metaclass
from ngoschema import utils, get_builder, SchemaMetaclass, ProtocolBase
from ngoschema.utils import GenericClassRegistry


def _process_cls(value):
    if not value:
        return None
    value = str(value)
    if utils.is_importable(value):
        return utils.import_from_string(value)
    else:
        return get_builder().resolve_or_construct(value)


class ObjectTransform(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to do simple model to model transformation
    """
    __schema__ = "http://numengo.org/draft-05/ngoschema/object-transform#/definitions/ObjectTransform"

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)
        self._from_cls = _process_cls(self.from_)
        self._to_cls = _process_cls(self.to_)

    @abstractmethod
    def __call__(self, from_, *args):
        raise Exception("must be overloaded")

    @classmethod
    def transform(cls, from_, *args, **kwargs):
        return cls(**kwargs)(from_, *args)


transform_registry = GenericClassRegistry()

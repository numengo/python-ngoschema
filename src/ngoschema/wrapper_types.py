import collections
import logging

import six
import weakref

from python_jsonschema_objects import util
from python_jsonschema_objects.validators import registry, ValidationError
import python_jsonschema_objects.wrapper_types as pjo_wrapper_types

logger = logging.getLogger(__name__)


class ArrayWrapper(pjo_wrapper_types.ArrayWrapper):
    """ A wrapper for array-like structures.

    This implements all of the array like behavior that one would want,
    with a dirty-tracking mechanism to avoid constant validation costs.
    """

    #def __delitem__(self, index):
    #    pjo_wrapper_types.ArrayWrapper.__delitem__(self, index)
#
    #def insert(self, index, value):
    #    pjo_wrapper_types.ArrayWrapper.insert(self, index, value)
 #
    #def __setitem__(self, index, value):
    #    pjo_wrapper_types.ArrayWrapper.__delitem__(self, index, value)
#
    #def __getitem__(self, idx):
    #    pjo_wrapper_types.ArrayWrapper.__getitem__(self, idx)

    def __init__(self, ary):
        pjo_wrapper_types.ArrayWrapper.__init__(self, ary)

    def validate(self):
        return pjo_wrapper_types.ArrayWrapper.validate(self)

    def validate_items(self):
        ret = pjo_wrapper_types.ArrayWrapper.validate_items(self)
        if ret and self._parent:
            self.set_items_parent()
        return ret
    
    def set_items_parent(self):
        from .metadata import Metadata
        from .classbuilder import ProtocolBase
        if not self._parent:
            return
        for item in self._typed:
            if isinstance(item, ArrayWrapper) and item._parent is not self._parent:
                item.parent = self._parent()
            elif isinstance(item, Metadata) and \
                (not item._parent or item._parent._ref is not self._parent):
                if item._lazy_loading:
                    item._set_prop_value('parent', self)
                else:
                    item.parent = self

    _parent = None

    def get_parent(self):
        return self._parent() if self._parent else None
    
    def set_parent(self, value):
        self._parent = weakref.ref(value)
        #from . import classbuilder
        #for elem in self._typed:
        #    if util.safe_issubclass(typ, ProtocolBase):
        #        pass

    parent = property(get_parent, set_parent)        

    @staticmethod
    def create(name, item_constraint=None, **addl_constraints):
        """ Create an array validator based on the passed in constraints.

        If item_constraint is a tuple, it is assumed that tuple validation
        is being performed. If it is a class or dictionary, list validation
        will be performed. Classes are assumed to be subclasses of ProtocolBase,
        while dictionaries are expected to be basic types ('string', 'number', ...).

        addl_constraints is expected to be key-value pairs of any of the other
        constraints permitted by JSON Schema v4.
        """
        from python_jsonschema_objects.classbuilder import LiteralValue
        from python_jsonschema_objects.classbuilder import ProtocolBase as pjo_ProtocolBase
        from python_jsonschema_objects.classbuilder import TypeProxy, TypeRef
        from .classbuilder import ProtocolBase
        klassbuilder = addl_constraints.pop("classbuilder", None)
        props = {}

        if item_constraint is not None:
            if isinstance(item_constraint, (tuple, list)):
                for i, elem in enumerate(item_constraint):
                    isdict = isinstance(elem, (dict,))
                    isklass = isinstance( elem, type) and util.safe_issubclass(
                        elem, (ProtocolBase, LiteralValue))

                    if not any([isdict, isklass]):
                        raise TypeError(
                            "Item constraint (position {0}) is not a schema".format(i))
            elif isinstance(item_constraint, (TypeProxy, TypeRef)):
                pass
            elif util.safe_issubclass(item_constraint, ArrayWrapper):
                pass
            else:
                isdict = isinstance(item_constraint, (dict,))
                isklass = isinstance( item_constraint, type) and util.safe_issubclass(
                    item_constraint, (ProtocolBase, LiteralValue))

                if not any([isdict, isklass]):
                    raise TypeError("Item constraint is not a schema")

                if isdict and '$ref' in item_constraint:
                    if klassbuilder is None:
                        raise TypeError("Cannot resolve {0} without classbuilder"
                                        .format(item_constraint['$ref']))

                    uri = item_constraint['$ref']
                    if uri in klassbuilder.resolved:
                        logger.debug(util.lazy_format(
                            "Using previously resolved object for {0}", uri))
                    else:
                        logger.debug(util.lazy_format("Resolving object for {0}", uri))

                        with klassbuilder.resolver.resolving(uri) as resolved:
                            # Set incase there is a circular reference in schema definition
                            klassbuilder.resolved[uri] = None
                            klassbuilder.resolved[uri] = klassbuilder.construct(
                                uri,
                                resolved,
                                (ProtocolBase,))

                    item_constraint = klassbuilder.resolved[uri]

                elif isdict and item_constraint.get('type') == 'array':
                    # We need to create a sub-array validator.
                    item_constraint = ArrayWrapper.create(name + "#sub",
                                                          item_constraint=item_constraint[
                                                                'items'],
                                                          addl_constraints=item_constraint)
                elif isdict and 'oneOf' in item_constraint:
                    # We need to create a TypeProxy validator
                    uri = "{0}_{1}".format(name, "<anonymous_list_type>")
                    type_array = []
                    for i, item_detail in enumerate(item_constraint['oneOf']):
                        if '$ref' in item_detail:
                            subtype = klassbuilder.construct(
                                util.resolve_ref_uri(
                                    klassbuilder.resolver.resolution_scope,
                                    item_detail['$ref']),
                                item_detail)
                        else:
                            subtype = klassbuilder.construct(
                                uri + "_%s" % i, item_detail)

                        type_array.append(subtype)

                    item_constraint = TypeProxy(type_array)

                elif isdict and item_constraint.get('type') == 'object':
                    """ We need to create a ProtocolBase object for this anonymous definition"""
                    uri = "{0}_{1}".format(name, "<anonymous_list_type>")
                    item_constraint = klassbuilder.construct(
                        uri, item_constraint)

        props['__itemtype__'] = item_constraint

        props.update(addl_constraints)


        validator = type(str(name), (ArrayWrapper,), props)

        return validator

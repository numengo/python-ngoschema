from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import sys

import six
import json

from ngoschema.utils import rreplace
from python_jsonschema_objects import util
from python_jsonschema_objects.validators import registry, ValidationError
import python_jsonschema_objects.wrapper_types as pjo_wrapper_types

from .resolver import resolve_uri, qualify_ref
from .mixins import HasCache, HasParent, HandleRelativeCname
from .utils.json import ProtocolJSONEncoder
from .validators.pjo import convert_array as converter
from . import utils

logger = logging.getLogger(__name__)


class ArrayWrapper(pjo_wrapper_types.ArrayWrapper, HandleRelativeCname, HasParent, HasCache):
    """ A wrapper for array-like structures.

    Inherits from python_jsonschema_objects.ArrayWrapper and adds parent relationships,
    cache invalidation and better representation.
    """
    __propinfo__ = {}

    def __init__(self, ary, _parent=None, _strict=None):
        self.data = converter(ary, self.__propinfo__)
        self._dirty = True
        self._typed = None
        self._parent = _parent
        if _strict:
            self.validate()

    @classmethod
    def propinfo(cls, prop_name):
        return cls.__propinfo__.get(prop_name) or {}

    def __str__(self):
        from . import settings
        items = self.data if self._dirty else self._typed
        if len(items) >= settings.PPRINT_MAX_EL:
            return rreplace(str([str(e) for e in items[:settings.PPRINT_MAX_EL]]), ']', ' +%i...]')
        return str([str(e) for e in items])

    def __repr__(self):
        items = self.data if self._dirty else self._typed
        cls = self.__class__
        return "<%s id=%s validated=%s %s>" % (
            getattr(cls, 'cls_fullname', cls.__name__),
            id(self),
            not self._dirty,
            [str(e) for e in items]
        )

    def __format__(self, format_spec):
        return str([str(e) for e in self.typed_elems]).__format__(format_spec)

    def append(self, value):
        self.data.append(value)
        self.mark_or_revalidate()

    def pop(self, index=-1):
        ret = self.typed_elems[index]
        self.data.pop(index)
        self.mark_or_revalidate()
        return ret

    def __eq__(self, other):
        if not utils.is_sequence(other):
            return False
        if len(self) != len(other):
            return False
        for i, e in enumerate(self):
            if e != other[i]:
                return False
        return True

    def _touch_children(self):
        if self._typed is None:
            return
        for item in self.typed_elems:
            try:
                item._touch_children()
                pass
            except Exception as er:
                pass

    def serialize(self, **opts):
        self.validate()
        enc = ProtocolJSONEncoder(**opts)
        return enc.encode(self)

    def is_dirty(self):
        return HasCache.is_dirty(self) or self.strict or self._dirty

    def _validate(self, data):
        self.data = data
        self.validate_items(data)
        self.validate_length()
        self.validate_uniqueness()

        if all([item.validate() for item in self._typed if item]):
            self._validated_data = [item._validated_data for item in self._typed]
        else:
            errors = [i for i, item in enumerate(self._typed) if item and item.is_dirty()]
            logger.info('errors validating items %s', errors)

    def validate(self):
        return HasCache.validate(self)

    def validate_items(self, data):
        from python_jsonschema_objects import classbuilder
        data = self.data

        if self.__itemtype__ is None:
            return

        type_checks = self.__itemtype__
        if not isinstance(type_checks, (tuple, list)):
            # we were given items = {'type': 'blah'} ; thus ensure the type for all data.
            type_checks = [type_checks] * len(data)
        elif len(type_checks) > len(data):
            raise ValidationError(
                "{1} does not have sufficient elements to validate against {0}"
                .format(self.__itemtype__, data))

        typed_elems = []
        for i, (elem, typ) in enumerate(zip(data, type_checks)):
            if isinstance(typ, (classbuilder.TypeProxy, classbuilder.TypeRef)):
                typ = typ.ref_class
            # check if already properly typed:
            if isinstance(elem, typ):
                elem.validate()
                if isinstance(elem, HasParent):
                    elem._parent = self._parent
                typed_elems.append(elem)
                continue
            # replace references
            if utils.is_mapping(elem) and '$ref' in elem:
                elem.update(resolve_uri(elem.pop('$ref')))
            # check types
            if isinstance(typ, dict):
                for param, paramval in six.iteritems(typ):
                    validator = registry(param)
                    if validator is not None:
                        validator(paramval, elem, typ)
                typed_elems.append(elem)

            elif util.safe_issubclass(typ, classbuilder.LiteralValue):
                val = typ(elem)
                typed_elems.append(val)
            elif util.safe_issubclass(typ, classbuilder.ProtocolBase):
                try:
                    val = typ(_parent=self._parent,
                              **self._parent._childConf,
                              **util.coerce_for_expansion(elem))
                except (TypeError, ValidationError) as er:
                    raise six.reraise(ValidationError,
                                      ValidationError("Problem setting array item [%i]: %s " % (i, er)),
                                      sys.exc_info()[2])
                typed_elems.append(val)
            elif util.safe_issubclass(typ, ArrayWrapper):
                val = typ(elem, _parent=self._parent)
                typed_elems.append(val)

        for i, t in enumerate(typed_elems):
            t._set_context_info(self._context, f'{self._prop_name}[{i}]')

        self._dirty = False
        # CRN: overwrite data with typed elem to avoid recreation next validation
        self.data = typed_elems
        self._typed = typed_elems
        return self._typed

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
        from python_jsonschema_objects.classbuilder import TypeProxy, TypeRef
        from ngoschema import ProtocolBase
        klassbuilder = addl_constraints.pop("classbuilder", None)

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
                                qualify_ref(item_detail['$ref'],
                                            klassbuilder.resolver.resolution_scope),
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

        props = {
            '__itemtype__': item_constraint,
            '__propinfo__': addl_constraints
        }
        strict = addl_constraints.pop("strict", None) or False
        props["_strict_"] = strict
        props.update(addl_constraints)

        validator = type(str(name), (ArrayWrapper,), props)

        return validator

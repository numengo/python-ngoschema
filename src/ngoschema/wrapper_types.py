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

from ngoschema.resolver import resolve_uri
from .mixins import HasCache, HasParent, HandleRelativeCname
from ngoschema.utils.json import ProtocolJSONEncoder
from . import utils

logger = logging.getLogger(__name__)

PPRINT_MAX_EL = utils.PPRINT_MAX_EL

class ArrayWrapper(pjo_wrapper_types.ArrayWrapper, HandleRelativeCname, HasParent, HasCache):
    """ A wrapper for array-like structures.

    This implements all of the array like behavior that one would want,
    with a dirty-tracking mechanism to avoid constant validation costs.
    """
    __propinfo__ = {}

    def __init__(self, ary, _parent=None):
        # convert to array is necessary
        if not utils.is_sequence(ary) or isinstance(ary, ArrayWrapper):
            ary = [ary]
        pjo_wrapper_types.ArrayWrapper.__init__(self, ary)
        HasCache.__init__(self,
                          context=_parent,
                          inputs=self.propinfo('dependencies'))
        self._parent = _parent

    @classmethod
    def propinfo(cls, propname):
        return cls.__propinfo__.get(propname) or {}

    def __str__(self):
        items = self.data if self._dirty else self._typed
        if len(items) >= PPRINT_MAX_EL:
            return rreplace(str([str(e) for e in items[:PPRINT_MAX_EL]]), ']', ' +%i...]')
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
        self._dirty = True

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

    def validate_items(self):
        if not self._dirty and self._typed is not None:
            return self._typed
        from python_jsonschema_objects import classbuilder

        if self.__itemtype__ is None:
            return

        type_checks = self.__itemtype__
        if not isinstance(type_checks, (tuple, list)):
            # we were given items = {'type': 'blah'} ; thus ensure the type for all data.
            type_checks = [type_checks] * len(self.data)
        elif len(type_checks) > len(self.data):
            raise ValidationError(
                "{1} does not have sufficient elements to validate against {0}"
                .format(self.__itemtype__, self.data))

        typed_elems = []
        for i, (elem, typ) in enumerate(zip(self.data, type_checks)):
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
                val = typ(elem, _parent=self._parent)
                val.do_validate()
                typed_elems.append(val)
            elif util.safe_issubclass(typ, classbuilder.ProtocolBase):
                if not isinstance(elem, typ):
                    try:
                        if isinstance(elem, (six.string_types, six.integer_types, float)) or getattr(self, 'isLiteralClass', False):
                            val = typ(elem, _parent=self._parent)
                        else:
                            val = typ(_parent=self._parent,
                                      **self._parent._childConf,
                                      **util.coerce_for_expansion(elem))
                    except Exception as e:
                        self._parent.logger.error('problem instanciating array item [%i]', i, exc_info=True)
                        raise ValidationError("'{0}' is not a valid value for '{1}': {2}"
                                              .format(elem, typ, e))
                else:
                    val = elem
                    val._parent = self._parent
                val.do_validate()
                typed_elems.append(val)

            elif util.safe_issubclass(typ, ArrayWrapper):
                val = typ(elem, _parent=self._parent)
                val.do_validate()
                typed_elems.append(val)

            elif isinstance(typ, classbuilder.TypeRef) and isinstance(elem, typ.ref_class):
                val = elem
                val._parent = self._parent
                val.do_validate()
                typed_elems.append(val)

            elif isinstance(typ, (classbuilder.TypeProxy, classbuilder.TypeRef)):
                try:
                    if isinstance(elem, (six.string_types, six.integer_types, float)) or getattr(self, 'isLiteralClass', False):
                        val = typ.ref_class(elem, _parent=self._parent)
                    else:
                        val = typ.ref_class(**self._parent._childConf,
                                  **util.coerce_for_expansion(elem),
                                  _parent=self._parent)
                except TypeError as e:
                    six.reraise(ValidationError,
                                ValidationError("'%s' is not a valid value for '%s'" % (elem, typ)))
                val.do_validate()
                typed_elems.append(val)

        self._typed = typed_elems
        self.set_clean()
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

        props = {
            '__itemtype__': item_constraint,
            '__propinfo__': addl_constraints
        }
        validator = type(str(name), (ArrayWrapper,), props)

        return validator

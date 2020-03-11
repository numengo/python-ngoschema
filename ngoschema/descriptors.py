from python_jsonschema_objects import \
    classbuilder as pjo_classbuilder, \
    util as pjo_util, \
    wrapper_types as pjo_wrapper_types, \
    literals as pjo_literals, \
    validators as pjo_validators

from . import utils
from .protocol_base import ProtocolBase
from .mixins import HasParent
from .literals import LiteralValue
from .wrapper_types import ArrayWrapper


class AttributeDescriptor(object):
    """ Provides property access for constructed class properties """

    def __init__(self, prop, info, fget=None, fset=None, fdel=None, desc=""):
        self.prop = prop
        self.info = info
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.desc = desc
        # flag to know if variable is readOnly check is active
        self._RO_active = True

    def __get__(self, obj, owner=None):
        from .models import ForeignKey
        if obj is None and owner is not None:
            return self

        trans = self.prop
        obj.logger.debug(utils.lazy_format("GET {0}.{1}", obj.short_repr, trans))

        prop = obj._properties[trans]

        # load lazy data
        if trans in obj._lazy_data:
            obj.logger.debug("lazy loading of '%s'", trans)
            prop._RO_active = False
            setattr(obj, trans, obj._lazy_data[trans])
            prop._RO_active = True

        if prop and prop.is_dirty():
            if self.fget:
                try:
                    self._RO_active = False
                    self.__set__(obj, self.fget(obj))
                    prop = obj._properties[trans]
                except Exception as er:
                    self._RO_active = True
                    obj.logger.error("GET %s.%s %s", obj, trans, er, exc_info=True)
                    raise
            prop.validate()

        if isinstance(prop, LiteralValue) and not isinstance(prop, ForeignKey):
            return prop._typed or prop._validated_data or prop._value
        else:
            return prop

    def __set__(self, obj, val):
        trans = self.prop
        raw = obj.__prop_translated_flatten__.get(trans) or trans
        info = self.info

        obj.logger.debug(
            utils.lazy_format("SET {0}.{1}={2}", obj.short_repr, trans, val, to_format=[2]))

        if self._RO_active and raw in obj.__read_only__:
            raise AttributeError("'%s' is read only" % raw)

        ptype = info["type"]
        types = [ptype] if not utils.is_sequence(ptype) else ptype

        prop = obj._properties[trans]

        if val is None and prop is None:
            return

        # load lazy data
        if trans in obj._lazy_data:
            obj._lazy_data.pop(trans)

        if obj._attrByName:
            if utils.is_mapping(val) and 'name' in val:
                obj._key2attr[val['name']] = (trans, None)
            if utils.is_sequence(val):
                for i, v2 in enumerate(val):
                    if utils.is_mapping(v2) and 'name' in v2:
                        obj._key2attr[v2['name']] = (trans, i)

        def build_typed_item(typ, prop, value):
            if isinstance(typ, pjo_classbuilder.TypeRef):
                typ = typ.ref_class
            if pjo_util.safe_issubclass(typ, ProtocolBase):
                if isinstance(value, typ):
                    if typ.validate(value):
                        return value
                return typ(**pjo_util.coerce_for_expansion(value), **obj._childConf, _parent=obj)
            if pjo_util.safe_issubclass(typ, LiteralValue):
                if prop is None:
                    prop = typ(value)
                else:
                    prop.__init__(value)
                return prop
            else:
                return typ(value, _parent=obj)

        old_value = prop._validated_data if prop else None
        typed = None
        if not utils.is_sequence(ptype):
            typed = build_typed_item(ptype, prop, val)
        else:
            errors = []
            for typ in ptype:
                try:
                    typed = build_typed_item(ptype, prop, val)
                    break
                except Exception as er:
                    errors.append(er)
            else:
                msgs = ["Impossible to build any of the types:"] + [
                    '%s: %s' % (p, e) for p, e in zip(ptype, errors)
                ]
                raise pjo_validators.ValidationError('\n'.join(msgs))

        typed._set_context_info(obj, raw)

        obj._properties[trans] = typed

        if typed._validated_data != old_value:
            obj.touch()

        if self.fset:
            self.fset(obj, typed)

    def __delete__(self, obj):
        prop = self.prop
        obj.logger.debug(utils.lazy_format("DEL {0}.{1}", obj.short_repr, prop))
        if prop in obj.__required__:
            raise AttributeError("'%s' is required" % prop)
        else:
            if self.fdel:
                self.fdel(obj)
            del obj._properties[prop]


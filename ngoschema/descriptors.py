from python_jsonschema_objects import \
    classbuilder as pjo_classbuilder, \
    util as pjo_util, \
    wrapper_types as pjo_wrapper_types, \
    literals as pjo_literals, \
    validators as pjo_validators

from . import utils
from .protocol_base import ProtocolBase
from .mixins import HasParent
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
        self.info['RO_active'] = True

    def __get__(self, obj, owner=None):
        if obj is None and owner is not None:
            return self

        propname = self.prop
        info = self.info
        obj.logger.debug(utils.lazy_format("GET {0}.{1}", obj.short_repr, propname))

        # load lazy data
        if propname in obj._lazy_data:
            try:
                obj.logger.debug("lazy loading of '%s'", propname)
                v = obj._lazy_data.pop(propname)
                setattr(obj, propname, v)
            except Exception as er:
                obj._lazy_data[propname] = v
                obj.logger.error(utils.lazy_format("GET {0}.{1} lazy loading failed with data {2})",
                                              obj.short_repr,
                                              propname, v, to_format=[2]),
                                  exc_info=True)
                raise

        prop = obj._properties.get(propname)

        if self.fget and (prop is None or prop.is_dirty()):
            try:
                info['RO_active'] = False
                self.__set__(obj, self.fget(obj))
                prop = obj._properties[propname]
            except Exception as er:
                info['RO_active'] = True
                obj.logger.error("GET %s.%s %s", obj, propname, er, exc_info=True)
                raise
        try:
            if prop is not None:
                # only forces validation for literals
                # only forces validation if pattern
                #force = not getattr(info["type"], "isLiteralClass", False) and not obj._lazyLoading
                force = False
                prop.do_validate(force=obj._strict)
                return prop
        except Exception as er:
            obj.logger.error("problem validating attribute %s: %s", propname, er, exc_info=True)
            raise

    def __set__(self, obj, val):
        prop = self.prop
        info = self.info
        obj.logger.debug(
            utils.lazy_format("SET {0}.{1}={2}", obj.short_repr, prop, val, to_format=[2]))
        if val is None and prop not in obj.__required__:
            obj._properties[prop] = None
            return
        if info['RO_active'] and prop in obj.__read_only__:
            # in case default has not been set yet
            if not (prop in obj.__has_default__ and obj._properties.get(prop) is None):
                raise AttributeError("'%s' is read only" % prop)

        infotype = info["type"]

        # pop any previous lazy data
        obj._lazy_data.pop(prop, None)
        old_prop = obj._properties.get(prop)
        old_val = old_prop._value if isinstance(old_prop, pjo_literals.LiteralValue) else None

        if obj._attrByName:
            if utils.is_mapping(val) and 'name' in val:
                obj._key2attr[val['name']] = (prop, None)
            if utils.is_sequence(val):
                for i, v2 in enumerate(val):
                    if utils.is_mapping(v2) and 'name' in v2:
                        obj._key2attr[v2['name']] = (prop, i)

        if isinstance(infotype, (list, tuple)):
            ok = False
            errors = []
            type_checks = []

            for typ in infotype:
                if not isinstance(typ, dict):
                    type_checks.append(typ)
                    continue
                typ = next(t for n, t in pjo_validators.SCHEMA_TYPE_MAPPING +
                           pjo_validators.USER_TYPE_MAPPING
                           if typ["type"] == n)
                if typ is None:
                    typ = type(None)
                if isinstance(typ, (list, tuple)):
                    type_checks.extend(typ)
                else:
                    type_checks.append(typ)

            for typ in type_checks:
                if isinstance(val, typ):
                    ok = True
                    break
                elif hasattr(typ, "isLiteralClass"):
                    try:
                        validator = typ(val, _parent=obj)
                    except Exception as e:
                        errors.append("Failed to coerce to '{0}': {1}".format(
                            typ, e))
                    else:
                        validator.do_validate(force=obj._strict)
                        ok = True
                        break
                elif pjo_util.safe_issubclass(typ, ProtocolBase):
                    # force conversion- thus the val rather than validator assignment
                    try:
                        if not utils.is_string(val):
                            val = typ(**obj._childConf,
                                      **pjo_util.coerce_for_expansion(val),
                                      _parent=obj)
                        else:
                            val = typ(val, _parent=obj)
                    except Exception as e:
                        errors.append(
                            "Failed to coerce to '%s': %s" % (typ, e))
                    else:
                        if isinstance(val, HasParent):
                            val._parent = obj
                        val.do_validate(force=obj._strict)
                        ok = True
                        break
                elif pjo_util.safe_issubclass(typ,
                                              pjo_wrapper_types.ArrayWrapper):
                    try:
                        val = typ(val, _parent=obj)
                    except Exception as e:
                        errors.append(
                            "Failed to coerce to '%s': %s" % (typ, e))
                    else:
                        val.do_validate(force=obj._strict)
                        ok = True
                        break

            if not ok:
                errstr = "\n".join(errors)
                raise pjo_validators.ValidationError(
                    "Object must be one of %s: \n%s" % (infotype, errstr))

        elif infotype == "array":
            val = info["validator"](val, _parent=obj)
            # only validate if no lazy loading
            if not obj._lazyLoading:
                val.do_validate(force=obj._strict)

        elif issubclass(infotype, ArrayWrapper):
        #elif getattr(infotype, 'type', None) == 'array':
            val = infotype(val, _parent=obj, _strict=obj._strict)

        elif getattr(infotype, "isLiteralClass", False):
            if not isinstance(val, infotype):
                validator = infotype(val, _parent=obj)
                # handle case of patterns
                if utils.is_pattern(val):
                    from ngoschema.utils.jinja2 import get_variables
                    vars = get_variables(val)
                    validator._add_inputs(*vars)
                    validator._pattern = val
                    # if there are variables, touch it in order to have it evaluated last minute
                    if vars:
                        validator.touch()
                else:
                    validator.do_validate(force=obj._strict)
                val = validator

        elif pjo_util.safe_issubclass(infotype, ProtocolBase):
            if not isinstance(val, infotype):
                if not utils.is_string(val):
                    val = infotype(_parent=obj,
                                   **obj._childConf,
                                   **pjo_util.coerce_for_expansion(val or {}))
                else:
                    val = infotype(val)
            val.do_validate(force=obj._strict)

        elif isinstance(infotype, pjo_classbuilder.TypeProxy):
            val = infotype(val, _parent=obj)

        elif isinstance(infotype, pjo_classbuilder.TypeRef):
            if not isinstance(val, infotype.ref_class):
                if not utils.is_string(val):
                    val = infotype(_parent=obj,
                                   **obj._childConf,
                                   **pjo_util.coerce_for_expansion(val))
                else:
                    val = infotype(val)
            val.do_validate(force=obj._strict)

        elif infotype is None:
            # This is the null value
            if val is not None:
                raise pjo_validators.ValidationError(
                    "None is only valid value for null")

        else:
            raise TypeError("Unknown object type: '%s'" % infotype)

        if old_val != val:
            if self.fset:
                # call the setter, and get the value stored in _properties
                self.fset(obj, val)
            if old_val is not None:
                # notifies dependencies content has changed but set state to clean
                val.touch(recursive=True)
                val.set_clean()
            #val.touch(recursive=True)
            #val.set_clean()

        obj._properties[prop] = val

    def __delete__(self, obj):
        prop = self.prop
        obj.logger.debug(utils.lazy_format("DEL {0}.{1}", obj.short_repr, prop))
        if prop in obj.__required__:
            raise AttributeError("'%s' is required" % prop)
        else:
            if self.fdel:
                self.fdel(obj)
            del obj._properties[prop]


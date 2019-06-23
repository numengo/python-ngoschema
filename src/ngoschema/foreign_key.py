# *- coding: utf-8 -*-
"""
Foreign key component

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 28/01/2019
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import weakref

import python_jsonschema_objects.literals as pjo_literals
from python_jsonschema_objects.wrapper_types import ArrayWrapper
from . import utils
from .decorators import classproperty
from .mixins import HasCache
from ngoschema.logger import HasLogger


class ForeignKey(pjo_literals.LiteralValue, HasCache, HasLogger):
    _keys = None
    _foreignClass = None
    _ref = None
    _value = None
    #_validated = False
        
    @classproperty
    def foreignSchemaUri(cls):
        return cls.propinfo('foreignKey').get('foreignSchemaUri', None)

    @classproperty
    def relationship(cls):
        return cls.propinfo('foreignKey').get('relationship', {})

    @classproperty
    def foreignClass(cls):
        from .classbuilder import get_builder
        from .metadata import Metadata
        if not cls._foreignClass and cls.foreignSchemaUri:
            try:
                cls._foreignClass = get_builder().resolve_or_build(cls.foreignSchemaUri)
            except Exception as er:
                cls.logger.error(er)
            if not issubclass(cls._foreignClass, Metadata):
                raise ValueError('target class (%r) must implement (%r) interface.' \
                                % (cls._foreignClass, Metadata))
        return cls._foreignClass

    @classproperty
    def isOne2Many(self):
        return self.relationship.get('cardinality') == 'one2many'

    @classproperty
    def backPopulates(self):
        return self.relationship.get('backPopulates', False)

    @classproperty
    def onDelete(cls):
        return cls.propinfo('foreignKey').get('onDelete')

    @classproperty
    def key(cls):
        return cls.propinfo('foreignKey').get('key','canonicalName')

    @classproperty
    def name(cls):
         return cls.propinfo('foreignKey').get('name') \
            or cls.propinfo('items').get('foreignKey', {}).get('name')

    @classproperty
    def ordering(cls):
        return cls.propinfo('foreignKey').get('ordering')

    @classproperty
    def reverse(cls):
        return cls.propinfo('foreignKey').get('reverse', False)

    def __init__(self, value):
        from .metadata import Metadata
        from .wrapper_types import ArrayWrapper
        HasCache.__init__(self)
        self._set_inputs(self.key)
        self._value = None
        self._ref = None
        self._dirty = False
        if value is None:
            return
        if isinstance(value, self.foreignClass):
            self.ref = value
            self._value = str(value._get_prop_value(self.key))
        elif isinstance(value, ForeignKey):
            self.ref = value._ref() if value._ref else None
            self._value = value._value
            self._dirty = value._dirty
        elif isinstance(value, ArrayWrapper):
            self.ref = value._parent
            #self._value = str(value._parent()._get_prop_value(self.key))
        else:
            self._value = str(value)
        # to force resolution of reference and backpopulates
        self._set_backref()
    
    def for_json(self):
        return None if not self._value else pjo_literals.LiteralValue.for_json(self)
 
    def validate(self):
        if self._value:
            pjo_literals.LiteralValue.validate(self)
        # literal value is validated, now let s see if it corresponds to reference
        if self._ref and self._ref():
            ref, key = self.ref, self.key
            ref_key_prop = ref._get_prop_value(key)
            # if key_prop is different, update the value
            if ref_key_prop != self._value:
                self._value = str(ref_key_prop)

    def _set_backref(self):
        if not self._ref or not self._ref():
            return

        def validate_backref(instance):
            if self.is_dirty():
                return
            
            foreignClass = instance.__itemtype__.foreignClass if self.isOne2Many else instance.foreignClass
            ref, key = (self._ref, self.name)
            def _access_key_ref(x):
                x_key = x._get_prop_value(key)
                return x_key._ref if x_key else None

            if not self.isOne2Many:
                assert isinstance(instance, ForeignKey)
                # check first if reference already defined and that literal corresponds
                if instance.ref and instance.ref._get_prop_value(instance.key) == self._value:
                    #instance._validated = True
                    instance._dirty = False
                    return
                # if not, make a query and initialize
                for i in foreignClass._instances:
                    if _access_key_ref(i) is ref:
                        backref = i
                        if not instance.ref is backref:
                            instance.__init__(backref)
                            return
            else: #ArrayWrapper
                if not hasattr(instance, '_init'):
                    # not initialized yet (while setting default for ex) 
                    return []

                data, typed = instance.data, instance._typed
                # data might have been inserted, we might need to add the backref
                if data and typed and len(data) != len(typed):
                    old_typed = [e.ref for e in typed]
                    # we use validate items to create new proper typed items
                    instance.validate_items()
                    for fk in instance.typed_elems:
                        if fk.is_dirty():
                            fk.validate()
                        if fk.ref not in old_typed:
                            # data has been inserted, set the backref
                            if fk.ref._lazy_loading:
                                # if lazy loading just set value
                                fk.ref._set_prop_value(self.name, self._value)
                            elif fk.ref._get_prop_value(self.name) != self._value:
                                # no lazy loading, use setter
                                fk.ref[self.name] = self.ref
                        else:
                            old_typed.remove(fk.ref)
                    # what is left in old_typed_elems are the deleted elements
                    # remove their backreference
                    for ref in old_typed:
                        ref[self.name] = None

                # we resolve all backreferences
                backrefs = [i() for i in foreignClass._instances
                            if _access_key_ref(i()) is ref]
                if self.ordering:
                    backrefs = sorted(backrefs, self.ordering, self.reverse)

                # setting refs avoids to resolve them from key values
                instance.__init__(backrefs)
                # validate would cause problem with data types, validate_items does the job
                instance.validate_items()
                # by doing that, we set backrefs as data in the arraywrapper, which creates
                # a reference, set it back to a foreignKey
                instance.data = [e for e in instance._typed]
                instance._dirty = False

        if self.backPopulates:
            backref_validator = self.ref._properties.get(self.backPopulates)
            if backref_validator is not None:
                backref_validator.__class__.validate = validate_backref
                backref_validator._init = True
                getattr(self.ref, self.backPopulates).touch()

    def _get_ref(self):
        if self._ref:
            return self._ref()
        if self._value is None:
            return
        key, val = self.key, self._value
        for i in self.foreignClass._instances:
            ival = str(i.get(key))
            if not ival:
                continue
            if ival == val:
                self.ref = i
                return i
        else:
            # not instanciated yet (lazy loading?)
            # look for a common ancestor
            ancs = self._value.split('.')
            from .protocol_base import ProtocolBase
            for i in ProtocolBase._instances:
                ival = str(i.get(key))
                iancs = ival.split('.')
                comm = []
                for a, ia in zip(ancs, iancs):
                    if a!=ia: break
                    comm.append(a)
                if comm:
                    ancestor = '.'.join(comm)
                    cur = i
                    while cur:
                        if cur.get(key) == ancestor:
                            break
                        cur = cur._parent
                    assert cur, ancestor
                    path2 = cur.resolve_cname(self._value)
                    for p in path2:
                        cur = cur[p]
                    self.ref = cur
                    return cur
        raise ValueError("Impossible to resolve reference '%s'" % self._value)

    def _set_ref(self, instance):
        if instance is not None:
            self._set_context(instance)
            self._ref = weakref.ref(instance)
            self._set_backref()

    ref = property(_get_ref, _set_ref)

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
import logging
import collections

import python_jsonschema_objects.literals as pjo_literals
from python_jsonschema_objects.wrapper_types import ArrayWrapper
from . import utils
from .decorators import classproperty
from .mixins import HasCache, HasLogger


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

    _isOne2Many = None
    @classproperty
    def isOne2Many(self):
        if not self._isOne2Many:
            self._isOne2Many = (self.relationship.get('cardinality') == 'one2many')
        return self._isOne2Many

    _backPopulates = None
    @classproperty
    def backPopulates(self):
        if self._backPopulates is None:
            self._backPopulates = self.relationship.get('backPopulates', False)
        return self._backPopulates

    _onDelete = None
    @classproperty
    def onDelete(cls):
        if not cls._onDelete:
            _onDelete = cls.propinfo('foreignKey').get('onDelete')
        return cls._onDelete

    _key = None
    @classproperty
    def key(cls):
        if not cls._key:
            cls._key = cls.propinfo('foreignKey').get('key','canonicalName')
        return cls._key

    _name = None
    @classproperty
    def name(cls):
        if not cls._name:
            cls._name = cls.propinfo('foreignKey').get('name') \
                or cls.propinfo('items').get('foreignKey', {}).get('name')
        return cls._name

    _ordering = None
    @classproperty
    def ordering(cls):
        if not cls._ordering:
            cls._ordering = cls.propinfo('foreignKey').get('ordering')
        return cls._ordering
 
    _reverse = None
    @classproperty
    def reverse(cls):
        if not cls._reverse:
            cls._reverse = cls.propinfo('foreignKey').get('reverse', False)
        return cls._reverse

    def __init__(self, value):
        from .metadata import Metadata
        from .wrapper_types import ArrayWrapper
        HasCache.__init__(self)
        self._value = None
        self._ref = None
        self._dirty = False
        if value is None:
            return
        if isinstance(value, self.foreignClass):
            self.ref = value
            self._value = str(value._get_prop_value(self.key))
        elif isinstance(value, ForeignKey):
            self.ref = value.ref
            self._value = value._value
            self._dirty = value._dirty
        elif isinstance(value, ArrayWrapper):
            self.ref = value._parent()
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
                for i in foreignClass.instances:
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
                backrefs = [i for i in foreignClass.instances 
                            if _access_key_ref(i) is ref]
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
        for i in self.foreignClass.instances:
            ival, val = i[self.key], self._value
            if not ival:
                continue
            if ival == val:
                self.ref = i
                return i
            if ival.startswith('%s.' % i.cname):
                try:
                    ref, path = i, i.resolve_cname(val)
                    for p in path:
                        ref = ref[p]
                    self.ref = ref
                    # now it s resolved, we can set backref
                    self._set_backref()
                    return ref
                except Exception as er:
                    self.logger.error(er)
        # due to lazy loading, certain instances are not loaded
        # last chance - find a parent in Metadata instances and explore children
        try:
            from .metadata import Metadata
            first_ancestor = next(filter(lambda i: self._value.startswith('%s.' % i.cname), Metadata.instances))
            #ancestors = [i for i in Metadata.instances if self._value.startswith('%s.' % i.cname)]
            #ancestors = sorted(ancestors, key=lambda a: len(a.cname), reverse=True)
            #best_parent = ancestors[0]
            best_parent = first_ancestor
            path = self._value
            path2 = best_parent.resolve_cname(path)
            ref = best_parent
            for p in path2:
                ref = ref[p] if isinstance(p, int) else getattr(ref, str(p))
            self.ref = ref
            return ref
        except Exception as er:
            self.logger.error(er)

        self.logger.warning('impossible to resolve %s %s=%s', 
                       self.foreignClass, self.key, self._value)

    def _set_ref(self, instance):
        self._set_inputs(ref=instance)
        self._ref = weakref.ref(instance)
        #_register_foreign_key(self)

    ref = property(_get_ref, _set_ref)

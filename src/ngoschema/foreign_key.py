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

# Registry of alive foreign keys
_foreign_keys_ref = weakref.WeakValueDictionary()

logger = logging.getLogger(__name__)

def _register_foreign_key(fkey):
    _foreign_keys_ref[id(fkey)] = fkey

def touch_all_refs(instance):
    for ref in [fk() for fk in _foreign_keys_ref.valuerefs() if fk().ref is instance]:
        ref._validated = False
        ref.validate()

class ForeignKey(pjo_literals.LiteralValue):
    _keys = None
    _foreignClass = None
    _ref = None
    _value = None
    _validated = False
        
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
                print('######## %s ##########\n%s' % (cls.foreignSchemaUri, er))
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
        if not self._onDelete:
            _onDelete = cls.propinfo('foreignKey').get('onDelete')
        return self._onDelete

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
        _register_foreign_key(self)
        self._value = None
        if value is None:
            self._ref = None
            self._validated = True
            return
        if isinstance(value, self.foreignClass):
            self._ref = weakref.ref(value)
            fkey_value = value._get_prop_value(self.key)
            pjo_literals.LiteralValue.__init__(self, fkey_value)
        else:
            self._ref = None
            pjo_literals.LiteralValue.__init__(self, value)
        # to force resolution of reference and backpopulates
        self._validated = False
        self.validate()
    
    def for_json(self):
        return None if not self._value else pjo_literals.LiteralValue.for_json(self)
 
    _backrefs = None
    def validate(self):
        from .query import Query
        from .classbuilder import iter_instances
        from .classbuilder import touch_property
        from .classbuilder import is_property_dirty
        if not self._value or not is_property_dirty(self):
            return
        pjo_literals.LiteralValue.validate(self)
        kwargs = { self.key: self._value }
        # literal value is validated, now let s see if it corresponds to reference
        if not self.ref:
            if self._value is None:
                return
            try:
                ref = self.foreignClass.get(**kwargs)
                self._ref = weakref.ref(ref)
            except Exception as er:
                # ref does not exist (any more??)
                try:
                    from .metadata import Metadata
                    ancestors = [i for i in Metadata.instances if self._value.startswith(str(i.cname))]
                    ancestors = sorted(ancestors, key=lambda a: len(a.cname), reverse=True)
                    best_parent = ancestors[0]
                    path = self._value[len(best_parent.cname)+1:]
                    ref = best_parent.get(path.split('.'))
                    self._ref = weakref.ref(ref)
                except Exception as er:
                    logger.warning('impossible to resolve %s %s=%s', 
                                    self.foreignClass, self.key, self._value)
                    self._ref = None
                    return
        else:
            ref_key_prop = self.ref._get_prop_value(self.key)
            # if key_prop is different, update the value
            if ref_key_prop != self._value:
                self._value = str(ref_key_prop)
        
        def touch_on_delete(prop):
            touch_property(prop)
        weakref.finalize(self.ref, touch_on_delete, self)


        def validate_backref(instance):
            if not is_property_dirty(instance):
                return
            
            foreignClass = instance.__itemtype__.foreignClass if self.isOne2Many else instance.foreignClass

            if not self.isOne2Many:
                assert isinstance(instance, ForeignKey)
                # check first if reference already defined and that literal corresponds
                if instance.ref and instance.ref._get_prop_value(instance.key) == self._value:
                    instance._validated = True
                    return
                # if not, make a query and initialize
                backref = foreignClass.get(**instance.propinfo('fkey'))
                if not instance.ref is backref:
                    instance.__init__(backref) 
            else:
                assert isinstance(instance, ArrayWrapper)

                # not initialized yet (while setting default for ex) 
                if not hasattr(instance, '_fkey'):
                    return []

                instance_key = instance.__itemtype__.key

                # data might have been inserted, we might need to add the backref
                if instance.data and instance._typed and len(instance.data) != len(instance._typed):
                    old_typed_elems = instance._typed
                    old_typed_elems_ref = [e.ref for e in old_typed_elems]
                    instance.validate_items()
                    for fk in instance.typed_elems:
                        if is_property_dirty(fk):
                            fk.validate()
                        if fk.ref not in old_typed_elems_ref:
                            # data has been inserted, set the backrefs
                            if fk.ref._lazy_loading:
                                fk.ref._set_prop_value(self.name, self._value)
                            elif fk.ref._get_prop_value(self.name) != self._value:
                                fk.ref[self.name] = self._value
                        else:
                            old_typed_elems_ref.remove(fk.ref)
                    # what is left in old_typed_elems are the deleted elements
                    # remove their backreference
                    for ref in old_typed_elems_ref:
                        ref[self.name] = None
                    del old_typed_elems_ref

                # we resolve all backreferences
                backrefs = foreignClass.list(**backref_validator._fkey)
                if self.ordering:
                    backrefs = sorted(backrefs, self.ordering, self.reverse)

                # setting refs avoids to resolve them from key values
                instance.__init__(backrefs)
                # validate would cause problem with data types, validate_items does the job
                instance.validate_items()
                # by doing that, we set backrefs as data in the arraywrapper, which creates
                # a reference, set it back to a foreignKey
                instance.data = [e for e in instance._typed]

        if self.backPopulates:
            backref_validator = self.ref._properties.get(self.backPopulates)
            if backref_validator is not None:
                backref_validator.__class__.validate = validate_backref
                if self.isOne2Many:
                    backref_validator._fkey = {self.name: self._value}
                else:
                    backref_validator.__propinfo__['fkey'] = {self.name: self._value}
                #backref_validator._kwargs =  {self.name: self._value}
                touch_property(backref_validator)

    @property
    def ref(self):
        if self._ref:
            return self._ref()


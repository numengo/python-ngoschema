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

def _register_foreign_key(fkey):
    _foreign_keys_ref[id(fkey)] = fkey

def touch_all_refs(instance):
    all_refs = [fk() for fk in _foreign_keys_ref.valuerefs() if fk().ref is instance]
    for ref in all_refs:
        ref._validated = False

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
        if isinstance(value, self.foreignClass):
            self._ref = weakref.ref(value)
            fkey_value = value.get(self.key)
            pjo_literals.LiteralValue.__init__(self, fkey_value)
        else:
            self._ref = None
            pjo_literals.LiteralValue.__init__(self, value)
        # to force resolution of reference and backpopulates
        self._validated = False
        self.validate()
 
    def validate(self):
        from .query import Query
        from .classbuilder import iter_instances
        from .classbuilder import touch_property
        from .classbuilder import is_property_dirty
        if not self._value or not is_property_dirty(self):
            return
        pjo_literals.LiteralValue.validate(self)
        # literal value is validated, now let s see if it corresponds to reference
        ref = self.ref
        if not ref:
            kwargs = { self.key: self._value }
            try:
                ref = Query(iter_instances(self.foreignClass)).get(**kwargs)
            except Exception as er:
                # ref does not exist (any more??)
                self._value = None
                return
            self._ref = weakref.ref(ref)
        else:
            ref_key_prop = ref._get_prop_value(self.key)
            # if key_prop is different, update the value
            if ref_key_prop != self._value:
                self._value = ref_key_prop._value
        
        def touch_on_delete(prop):
            touch_property(prop)
        weakref.finalize(ref, touch_on_delete, self)

        def validate_backref(instance):
            if not is_property_dirty(instance):
                return
            
            kwargs = { self.name: self._value }
            foreignClass = instance.__itemtype__.foreignClass if self.isOne2Many else instance.foreignClass

            if not self.isOne2Many:
                assert isinstance(instance, ForeignKey)
                backref = Query(iter_instances(foreignClass)).get(**kwargs)
                if not instance.ref is backref:
                    instance.__init__(backref._get_prop_value(instance.key)) 
            else:
                assert isinstance(instance, ArrayWrapper)

                backrefs = Query(iter_instances(foreignClass)).list(**kwargs)
                if self.ordering:
                    backrefs = sorted(backrefs, self.ordering, self.reverse)
                    # setting refs avoids to resolve them from key values
                instance_key = instance.__itemtype__.key
                instance.__init__([b._get_prop_value(instance_key) for b in backrefs])
                instance.validate_items()

        if self.backPopulates:
            backref_validator = ref._properties.get(self.backPopulates)
            if backref_validator is not None:
                backref_validator.__class__.validate = validate_backref
                touch_property(backref_validator)

    @property
    def ref(self):
        if self._ref:
            return self._ref()


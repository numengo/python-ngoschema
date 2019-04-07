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
    for ref in (fk() for fk in _foreign_keys_ref.valuerefs() if fk()._ref and fk()._ref() is instance):
        ref._validated = False
        #ref.validate()

def _on_fk_ref_delete(fkey):
    print('on delete (%r)' % (fkey))
    from .classbuilder import touch_property
    #backref_validator = deleted._properties.get(fkey.backPopulates)
    #touch_property(backref_validator)
    fkey._ref = None
    fkey._value = None
    touch_property(fkey)

def _on_fk_ref_delete2(ref, fkey):
    print('on delete2 (%r) (%r)' % (ref(), fkey))
    from .classbuilder import touch_property
    if ref():
        backref_validator = ref()._properties.get(fkey.backPopulates)
        touch_property(backref_validator)

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
            self._value = str(value._get_prop_value(self.key))
            self._validated = True
        elif isinstance(value, ForeignKey):
            self._ref = value._ref
            self._value = value._value
            self._validated = value._validated
        else:
            self._ref = None
            self._value = str(value)
            self._validated = True
        if self._ref and self._ref():
            weakref.finalize(self._ref(), _on_fk_ref_delete, self)
            weakref.finalize(self._ref(), _on_fk_ref_delete2, self._ref, self)
        # to force resolution of reference and backpopulates
        #self._validated = False
        self._set_backref()
    
    def for_json(self):
        return None if not self._value else pjo_literals.LiteralValue.for_json(self)
 
    def validate(self):
        from .classbuilder import is_property_dirty
        if not self._value or not is_property_dirty(self):
            return
        pjo_literals.LiteralValue.validate(self)
        #kwargs = { self.key: self._value }
        # literal value is validated, now let s see if it corresponds to reference
        if self._ref and self._ref():
            ref_key_prop = self.ref._get_prop_value(self.key)
            # if key_prop is different, update the value
            if ref_key_prop != self._value:
                self._value = str(ref_key_prop)

    def _set_backref(self):
        from .classbuilder import touch_property
        from .classbuilder import is_property_dirty, iter_instances
        if not self.ref:
            return

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
                backref = foreignClass.first(**instance.propinfo('fkey'))
                if not instance.ref is backref:
                    instance.__init__(backref) 
            else:
                assert isinstance(instance, ArrayWrapper)

                # not initialized yet (while setting default for ex) 
                if not hasattr(instance, '_init'):
                    return []

                instance_key = instance.__itemtype__.key

                # data might have been inserted, we might need to add the backref
                if instance.data and instance._typed and len(instance.data) != len(instance._typed):
                    old_typed_elems = instance._typed
                    old_typed_elems_ref = [e.ref for e in old_typed_elems]
                    # we use validate items to create new proper typed items
                    instance.validate_items()
                    for fk in instance.typed_elems:
                        if is_property_dirty(fk):
                            fk.validate()
                        if fk.ref not in old_typed_elems_ref:
                            # data has been inserted, set the backrefs
                            if fk.ref._lazy_loading:
                                fk.ref._set_prop_value(self.name, self._value)
                            elif fk.ref._get_prop_value(self.name) != self._value:
                                fk.ref[self.name] = self.ref
                        else:
                            old_typed_elems_ref.remove(fk.ref)
                    # what is left in old_typed_elems are the deleted elements
                    # remove their backreference
                    for ref in old_typed_elems_ref:
                        ref[self.name] = None
                    del old_typed_elems_ref

                # we resolve all backreferences
                ref = self._ref
                key = self.name
                def _access_key_ref(x):
                    x_key = x.get(key)
                    return x_key._ref if x_key else None
                backrefs = [i for i in iter_instances(foreignClass) 
                            if _access_key_ref(i) is ref]
                #backref_validator = self.ref._properties.get(self.backPopulates)
                #backrefs = foreignClass.filter(**backref_validator._fkey)
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
                backref_validator._init = True
                #if self.isOne2Many:
                #    backref_validator._fkey = {'%s._ref' % self.name: self._ref}
                #else:
                #    backref_validator.__propinfo__['fkey'] = {'%s._ref' % self.name: self._ref}
                
                #backref_validator._kwargs =  {self.name: self._value}
                touch_property(backref_validator)

    @property
    def ref(self):
        if not self._ref:
            if self._value is None:
                return
            try:
                ref = self.foreignClass.first(**{ self.key: self._value })
                weakref.finalize(ref, _on_fk_ref_delete, self)
                self._ref = weakref.ref(ref)
                weakref.finalize(ref, _on_fk_ref_delete2, self._ref, self)
            except Exception as er:
                # ref does not exist (any more??)
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
                    self._ref = weakref.ref(ref)
                    weakref.finalize(ref, _on_fk_ref_delete, self)
                    weakref.finalize(ref, _on_fk_ref_delete2, self._ref, self)
                    #logger.info('HERE %s / %s', self._value, path2)
                except Exception as er:
                    logger.error(er)
                    logger.warning('impossible to resolve %s %s=%s', 
                                    self.foreignClass, self.key, self._value)
                    self._ref = None
        if self._ref:
            return self._ref()


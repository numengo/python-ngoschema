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

from future.utils import with_metaclass
import python_jsonschema_objects.literals as pjo_literals
from python_jsonschema_objects.wrapper_types import ArrayWrapper
from . import utils
from .decorators import classproperty
from ngoschema import ProtocolBase
from .classbuilder import get_builder
from .schema_metaclass import SchemaMetaclass
from .foreign_key import ForeignKey
from .metadata import Metadata

class Relationship(with_metaclass(SchemaMetaclass, ProtocolBase)):
    """
    Class to deal with relationships
    """
    schemaUri = "http://numengo.org/draft-05/schema#/definitions/Relationship"

    _backrefs = None
    _validator = None

    def __init__(self, **kwargs):
        ProtocolBase.__init__(self, **kwargs)
        owner = self.foreignKey.targetClass
        # build relationship : create a property of the relationship name on the owner
        owner_propinfo = owner.propinfo(str(self.name))
        if owner_propinfo:
            # owner prop already exists, make it a ForeignKey if not already
            owner_prop_type = owner_propinfo['type']
            if issubclass(owner_prop_type, pjo_literals.LiteralValue):
                if not issubclass(owner_prop_type, ForeignKey):
                    owner_propinfo['foreignKey'] = {
                        'foreignSchemaUri': owner.__schema__['$id']
                    }                    
                    validator = type(
                        str(self.name),
                        (ForeignKey, ),
                        {
                            '__propinfo__': owner_propinfo
                        },
                    )
                else:
                    validator = owner_prop_type
            else:
                raise ValueError("property '%s' is not an array or a literal and cannot be used as a relationship" % self.name)
        else:
            validator = type(
                str(self.name),
                (ForeignKey, ),
                {
                    '__propinfo__': {
                        'foreignKey': {
                            'foreignSchemaUri': owner.__schema__['$id']
                        }
                    }
                },
            )
        self._validator = validator
        owner.__propinfo__[str(self.name)] = validator

        if self.backPopulates:
            def validate_and_backpopulate(instance):
                super(instance.__class__, instance).validate()
                if self._backrefs:
                    if self.isOne2Many:
                        if instance._value not in self._backrefs:
                            instance._backrefs.append(instance._value)
                            instance._backrefs._value = sorted(self._backrefs._values, str(self.ordering), self.reverse)
                            instance._backrefs.validate()

                    elif self._backrefs != instance._value:
                            self._backrefs = instance._value
                    return
                # foreignKey should be resolved
                target = instance.targetClass
                # check if backPopulates property exists
                target_propinfo = target.propinfo(str(self.backPopulates))
                if target_propinfo:
                    # owner prop already exists, make it a ForeignKey if not already
                    target_prop_type = target_propinfo['type']
                    if issubclass(target_prop_type, pjo_literals.LiteralValue):
                        if self.isOne2Many:
                            raise ValueError("property '%s' already exists as a literal but \
                            the relationship '%s' is set to one-to-many" % (self.backPopulates, self.name))
                        if not issubclass(target_prop_type, ForeignKey):
                            target_propinfo['foreignKey'] = {
                                'foreignSchemaUri': target.__schema__['$id']
                            }
                            validator = type(
                                str(self.backPopulates),
                                (ForeignKey, ),
                                {
                                    '__propinfo__': target_propinfo
                                },
                            )
                        else:
                            validator = target_prop_type
                    elif issubclass(target_prop_type, ArrayWrapper):
                        if not self.isOne2Many:
                            raise ValueError("property '%s' is array but relationship '%s' is one-to-one" % (self.backPopulates, self.name))
                        target_prop_item_type = target_prop_type.__itemtype__
                        if issubclass(target_prop_item_type, pjo_literals.LiteralValue):
                            if not issubclass(target_prop_item_type, ForeignKey):
                                target_prop_item_propinfo = target_prop_item_type.__propinfo__
                                target_prop_item_propinfo['foreignKey'] = {
                                    'foreignSchemaUri': target.__schema__['$id']
                                }
                                item_validator = type(
                                    str(self.backPopulates),
                                    (ForeignKey, ),
                                    {
                                        '__propinfo__': target_prop_item_propinfo
                                    },
                                )
                                target_propinfo['__itemtype__'] = item_validator
                                validator = type(str(name), (ArrayWrapper,), props)
                            else:
                                validator = target_prop_item_type
                        else:
                            raise ValueError("property '%s' is not an array of literals and cannot be used as a relationship" % self.name)
                    else:
                        raise ValueError("property '%s' is not an array or a literal and cannot be used as a relationship" % self.name)
                else:
                    validator = type(
                        str(self.backPopulates),
                        (ForeignKey, ),
                        {
                            '__propinfo__': {
                                'foreignKey': {
                                    'foreignSchemaUri': target.__schema__['$id']
                                }
                            }
                        },
                    )
                    if self.isOne2Many:
                        item_validator = validator
                        target_propinfo = {
                            '__propinfo__': {
                                'type': 'array',
                                'foreignKey': {
                                    'foreignSchemaUri': target.__schema__['$id']
                                }
                            },
                            '__itemtype__': item_validator
                        }
                        validator = type(str(self.backPopulates), (ArrayWrapper,), target_propinfo)
                self._backrefs = validator
                target.__propinfo__[str(self.backPopulates)] = validator
            self._validator.validate = validate_and_backpopulate

    def targetClass(self):
        return self.foreignKeys.targetClass

    def set_foreignKeys(self, value):
        self._set_prop_value('foreignKeys', value)

    _isOne2Many = None
    @property
    def isOne2Many(self):
        if not self._isOne2many:
            self._isOne2Many = (self.cardinality == 'one2many')
        return self._isOne2Many





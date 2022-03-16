# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from jsonschema import _validators
from jsonschema.validators import create

from ..utils.utils import GenericClassRegistry
from ..exceptions import ValidationError
from ngoschema.resolvers.uri_resolver import resolve_doc, UriResolver
from .. import settings

# create a registry for validators
jsch_validators_registry = GenericClassRegistry()

# add jsonschema validators to registry
#jsch_validators_registry.register('$ref')(_validators.ref)
jsch_validators_registry.register('additionalItems')(_validators.additionalItems)
jsch_validators_registry.register('additionalProperties')(_validators.additionalProperties)
jsch_validators_registry.register('allOf')(_validators.allOf)
jsch_validators_registry.register('anyOf')(_validators.anyOf)
jsch_validators_registry.register('const')(_validators.const)
jsch_validators_registry.register('contains')(_validators.contains)
#jsch_validators_registry.register('dependencies')(_validators.dependencies)
## 3.7
jsch_validators_registry.register('dependencies')(getattr(_validators, 'dependentSchemas', getattr(_validators, 'dependencies', None)))
jsch_validators_registry.register('dependentSchemas')(_validators.dependentSchemas)
jsch_validators_registry.register('dependentRequired')(_validators.dependentRequired)
jsch_validators_registry.register('enum')(_validators.enum)
jsch_validators_registry.register('exclusiveMaximum')(_validators.exclusiveMaximum)
jsch_validators_registry.register('exclusiveMinimum')(_validators.exclusiveMinimum)
jsch_validators_registry.register('format')(_validators.format)
jsch_validators_registry.register('if')(_validators.if_)
jsch_validators_registry.register('items')(_validators.items)
jsch_validators_registry.register('maxItems')(_validators.maxItems)
jsch_validators_registry.register('maxLength')(_validators.maxLength)
jsch_validators_registry.register('maxProperties')(_validators.maxProperties)
jsch_validators_registry.register('maximum')(_validators.maximum)
jsch_validators_registry.register('minItems')(_validators.minItems)
jsch_validators_registry.register('minLength')(_validators.minLength)
jsch_validators_registry.register('minProperties')(_validators.minProperties)
jsch_validators_registry.register('minimum')(_validators.minimum)
jsch_validators_registry.register('multipleOf')(_validators.multipleOf)
jsch_validators_registry.register('oneOf')(_validators.oneOf)
jsch_validators_registry.register('not')(_validators.not_)
jsch_validators_registry.register('pattern')(_validators.pattern)
jsch_validators_registry.register('patternProperties')(_validators.patternProperties)
jsch_validators_registry.register('properties')(_validators.properties)
jsch_validators_registry.register('propertyNames')(_validators.propertyNames)
jsch_validators_registry.register('required')(_validators.required)
jsch_validators_registry.register('uniqueItems')(_validators.uniqueItems)

# draft 2019-09
jsch_validators_registry.register('definitions')(_validators.properties)
jsch_validators_registry.register('$defs')(_validators.properties)


@jsch_validators_registry.register('$recursiveRef')
def recursive_ref(validator, ref, instance, schema):
    resolve = getattr(validator.resolver, "resolve", None)
    if resolve is None:
        with validator.resolver.resolving(ref) as resolved:
            for error in validator.descend(instance, resolved):
                yield error
    else:
        scope, resolved = validator.resolver.resolve(ref)
        recursive = resolved.get('$recursiveAnchor', True)
        if recursive:
            validator.resolver.push_scope(scope)

        try:
            for error in validator.descend(instance, resolved):
                yield error
        finally:
            if recursive:
                validator.resolver.pop_scope()


@jsch_validators_registry.register('extends__')
def extends(validator, ref, instance, schema):
    resolve = getattr(validator.resolver, "resolve", None)
    if resolve is None:
        with validator.resolver.resolving(ref) as resolved:
            for error in validator.descend(instance, resolved):
                yield error
    else:
        scope, resolved = validator.resolver.resolve(ref)

        try:
            for error in validator.descend(instance, resolved):
                yield error
        finally:
            pass

# custom validators
@jsch_validators_registry.register()
def isPathDir(validator, param, value, type_data):
    if value.is_dir() != param:
        raise ValidationError(
            "{0} is not the path of a directory".format(value))


@jsch_validators_registry.register()
def isPathFile(validator, param, value, type_data):
    if value.is_file() != param:
        raise ValidationError("{0} is not the path of a file".format(value))


@jsch_validators_registry.register()
def isPathExisting(validator, param, value, type_data):
    if value.exists() != param:
        raise ValidationError("{0} is not an existing path".format(value))


Draft201909Validator = create(
        meta_schema=resolve_doc(settings.MS_URI),
        validators=jsch_validators_registry._registry,
        version='2019-09',
    )

default_meta_validator = Draft201909Validator(
    Draft201909Validator.META_SCHEMA,
    resolver=UriResolver.create(uri=settings.MS_URI))

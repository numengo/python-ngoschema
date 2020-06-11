# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict, defaultdict, Mapping
import re

from .. import settings
from ..exceptions import InvalidValue
from ..utils import ContextManager
from ..decorators import assert_arg
from ..resolver import resolve_uri
from ..session import Session, scoped_session, session_maker
from .type import Type, TypeChecker
from .literals import String, Integer
from .array import Array, Tuple
from .object import Object

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


@TypeChecker.register('$ref')
class Ref(String):

    def validate(self, value, resolve=True, **opts):
        String.validate(self, value, **opts)
        if resolve:
            try:
                resolve_uri(value)
                return True
            except Exception as er:
                return False

    @staticmethod
    def resolve(value):
        return resolve_uri(value)

    def __call__(self, value, validate=True, resolve=False, **opts):
        value = String.__call__(self, value, validate=False, **opts)
        if validate:
            self.validate(value, resolve=False)
        return Ref.resolve(value) if resolve else value


@TypeChecker.register('foreignKey')
class ForeignKey(Ref):
    _foreign_class = None
    _foreign_keys = ['id']
    _foreign_keys_type = [Integer]
    _back_populates = None

    def convert(self, value, **opts):
        if self._foreign_class and isinstance(value, self._foreign_class):
            value = [getattr(value, k) for k in self._foreign_keys]
        return tuple(t.convert(v, **opts) for t, v in zip(self._foreign_keys_type, value))

    @classmethod
    @assert_arg(1, Array, str_delimiter=',')
    def check(cls, value, **opts):
        return all(t.check(v, **opts) for t, v in zip(cls._foreign_keys_type, Array.convert(Array, value, **opts)))

    def __init__(self, **schema):
        from .type_builder import TypeBuilder
        from .object_protocol import ObjectProtocol
        Type.__init__(self, **schema)
        fc = TypeBuilder.load(self._schema['$schema']) if '$schema' in self._schema else None
        self._foreign_keys = self._schema.get('foreignKey', {}).get('fkeys') or self._foreign_keys
        if fc:
            self._foreign_class = fc
            self._foreign_keys = fk = fc._schema.get('primaryKeys')
            self._foreign_keys_type = [fc._property_type(k) for k in fk]
        else:
            self._foreign_class = ObjectProtocol

    def __call__(self, value, validate=True, resolve=False, context=None, **opts):
        context = Type._make_context(self, context, opts)
        value = self.convert(value, context=context, **opts)
        if validate:
            self.validate(value, resolve=False, context=context)  # resolve False to avoid double resolution
        if resolve:
            return self.resolve(value, context=context)
        return value

    def validate(self, value, resolve=False, **opts):
        Type.validate(self, value, **opts)
        if resolve:
            raise InvalidValue()
        pass

    @assert_arg(1, Tuple, str_delimiter=',')
    def resolve(self, key, session=None, **opts):
        session = session or scoped_session(session_maker())()
        fc_repos = [r for r in session._repos if issubclass(r.objectClass, self._foreign_class)]
        for r in fc_repos:
            v = r.get(key)
            if v is not None:
                return v
        raise InvalidValue('impossible to resolve foreign key %s' % repr(key))


        def _check_object(c):
            if not set(self._foreign_keys).difference(c.keys()):
                cur_key = tuple([c[k] for k in self._foreign_keys])
                if cur_key == key:
                    return True
            return False

        ctx = Type._make_context(self, context, opts)
        for c in ctx.maps_flattened:
            if isinstance(c, self._foreign_class):
                if not set(self._foreign_keys).difference(c.keys()):
                    cur_key = tuple([c[k] for k in self._foreign_keys])
                    if cur_key == key:
                        return c
        else:
            raise InvalidValue('impossible to resolve foreign key %s' % repr(key))


@TypeChecker.register('canonicalName')
class CanonicalName(ForeignKey):
    _foreign_keys = ['canonicalName']
    _foreign_keys_type = [String]

    def convert(self, value, **opts):
        if self._foreign_class and isinstance(value, self._foreign_class):
            value = [getattr(value, k) for k in self._foreign_keys]
        return tuple(t.convert(v, **opts) for t, v in zip(self._foreign_keys_type, value))[0]

    @assert_arg(1, Array, str_delimiter='.')
    def resolve(self, cname, session=None, **opts):
        from ..models.metadata import NamedObject
        session = session or scoped_session(session_maker())()
        fc_repos = [r for r in session._repos if issubclass(r.objectClass, NamedObject)]
        root = cname[0]
        ns = cname[1:]
        for r in fc_repos:
            v = r.get(root)
            if v is not None:
                return v if not ns else v.resolve_cname(ns)
        raise InvalidValue('impossible to resolve %s in context' % repr('.'.join(cname[1:])))

        cur = Type._make_context(self, context, opts)
        for i, n in enumerate(cname):
            if n in cur:
                v = cur[n]
            else:
                try:
                    v = ForeignKey.resolve(self, n, context=cur)
                except Exception as er:
                    raise InvalidValue('impossible to resolve %s in context' % repr('.'.join(cname[:i + 1])))
            cur = ContextManager(v)
        return v


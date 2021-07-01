# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict, defaultdict, Mapping, Sequence
import re

from .. import settings
from ..exceptions import InvalidValue
from ..decorators import assert_arg
from ngoschema.resolvers.uri_resolver import resolve_uri
from ..session import Session, scoped_session, session_maker
from ..protocols import TypeProtocol, Resolver
from ..managers.type_builder import register_type
from .strings import String
from .numerics import Integer
from .uri import Id
from .array import Array, Tuple

ATTRIBUTE_NAME_FIELD = settings.ATTRIBUTE_NAME_FIELD


@register_type('$ref')
class Ref(String, Resolver):

    @staticmethod
    def _validate(self, value, resolve=True, **opts):
        String.validate(value, **opts)
        if resolve:
            try:
                resolve_uri(value)
                return True
            except Exception as er:
                return False

    @staticmethod
    def _convert(self, value, **opts):
        return Id.convert(value, **opts)

    @staticmethod
    def _resolve(self, value):
        return resolve_uri(value)

    @staticmethod
    def _evaluate(self, value, validate=True, resolve=False, **opts):
        value = String._evaluate(self, value, validate=False, **opts)
        if validate:
            self._validate(self, value, resolve=False)
        return self._resolve(self, value) if resolve else value


@register_type('foreignKey')
class ForeignKey(Ref):
    _foreignSchema = None
    _foreignClass = None
    _foreignKeys = ['id']
    _foreignKeysType = [Integer]
    _backPopulates = None

    def __init__(self, value=None, foreign_schema=None, **opts):
        TypeProtocol.__init__(self, **opts)
        fs = foreign_schema or self._schema.get('foreignKey', {}).get('foreignSchema')
        if fs:
            self.set_foreignSchema(fs)

    def set_foreignSchema(self, foreign_schema):
        from ..protocols.object_protocol import ObjectProtocol
        from ..managers.type_builder import type_builder, scope
        self._foreignSchema = fs = foreign_schema
        self._foreignClass = ObjectProtocol
        if fs:
            try:
                fs = scope(fs, self._id)
                fc = type_builder.load(fs)
                self.set_foreignClass(fc)
            except Exception as er:
                self._logger.error(er, exc_info=True)
                pass

    def set_foreignClass(self, foreign_class):
        from ..protocols import TypeProxy
        from ..models.instances import Entity
        fc = foreign_class
        if fc and not issubclass(fc, TypeProxy):
            if not issubclass(fc, Entity):
                raise ValueError('target class (%r) must implement (%r) interface.' \
                                 % (fc, Entity))
            else:
                self._foreignClass = fc
                self._foreignKeys = fk = self._schema.get('foreignKey', {}).get('foreignKeys', fc._primaryKeys)
                self._foreignKeysType = tuple(fc._items_type(fc, k) for k in fk)
        return fc

    def get_foreignClass(self):
        from ..protocols.type_proxy import TypeProxy
        fc, fs = self._foreignClass, self._foreignSchema
        if fc and issubclass(fc, TypeProxy):
            self._foreignClass = fc.proxy_type()
        if not fc and fs:
            ForeignKey.set_foreignSchema(self, self._foreignSchema)
        return self._foreignClass

    @staticmethod
    def _convert(self, value, foreign_class=None, **opts):
        if value is None:
            return None
        fc = foreign_class or ForeignKey.get_foreignClass(self)
        if fc and isinstance(value, fc):
            value = [getattr(value, k) for k in self._foreignKeys]
        elif Integer.check(value):
            if value < 0:
                return None
            value = [value]
        else:
            value = Array.deserialize(value, split_string=True, **opts)
        opts['raw_literals'] = False
        fkt = self._foreignKeysType
        return fkt[0]._convert(fkt[0], value[0], **opts) if len(fkt)==1 else tuple(t._convert(t, v, **opts) for t, v in zip(fkt, value))
        #return tuple(t._convert(t, v, **opts) for t, v in zip(self._foreignKeysType, value))

    @staticmethod
    @assert_arg(1, Array, strDelimiter=',')
    def _check(self, value, **opts):
        if all(t._check(t, v, **opts) for t, v in zip(self._foreignKeysType, Array.deserialize(value, **opts))):
            return value
        raise TypeError('%s is not of type foreignKey.' % value)

    @staticmethod
    def _serialize(self, value, **opts):
        fkt = self._foreignKeysType
        return fkt[0]._convert(fkt[0], value, **opts) if len(fkt)==1 else tuple(t._convert(t, v, **opts)\
                                                                                  for t, v in zip(fkt, value))
        #return tuple(t._convert(t, v, **opts) for t, v in zip(self._foreignKeysType, value)) if value is not None else None

    @staticmethod
    def _evaluate(self, value, validate=True, resolve=False, context=None, **opts):
        ctx = TypeProtocol._create_context(self, context)
        value = self._convert(self, value, context=ctx, **opts)
        if validate:
            self._validate(self, value, resolve=False, context=ctx)  # resolve False to avoid double resolution
        if resolve:
            return self._resolve(self, value, context=ctx)
        return value

    @staticmethod
    def _validate(self, value, resolve=False, **opts):
        TypeProtocol._validate(self, value, **opts)
        if resolve:
            raise InvalidValue()
        return value

    @staticmethod
    @assert_arg(1, Tuple, strDelimiter=',')
    def _resolve(self, key, session=None, **opts):
        session = session or scoped_session(session_maker())()
        ric = [r.instanceClass for r in session.repositories]
        fc_repos = [r for r in session.repositories if issubclass(r.instanceClass, self._foreignClass)]
        for r in fc_repos:
            # change resolve_fkey to use resolve??
            v = r.resolve_fkey(key)
            if v is not None:
                return v
        raise InvalidValue('impossible to resolve foreign key %s' % repr(key))


        def _check_object(c):
            if not set(self._foreignKeys).difference(c.keys()):
                cur_key = tuple([c[k] for k in self._foreignKeys])
                if cur_key == key:
                    return True
            return False

        ctx = Type.make_context(self, context)
        for c in ctx.maps_flattened:
            if isinstance(c, self._foreignClass):
                if not set(self._foreignKeys).difference(c.keys()):
                    cur_key = tuple([c[k] for k in self._foreignKeys])
                    if cur_key == key:
                        return c
        else:
            raise InvalidValue('impossible to resolve foreign key %s' % repr(key))


@register_type('canonicalName')
class CanonicalName(ForeignKey):
    _foreignKeys = ['canonicalName']
    _foreignKeysType = [String]

    @staticmethod
    def _convert(self, value, **opts):
        fc = self.foreignClass
        if fc and isinstance(value, fc):
            value = [getattr(value, k) for k in self._foreignKeys]
        return tuple(t._convert(t, v, **opts) for t, v in zip(self._foreignKeysType, value))[0]

    @staticmethod
    @assert_arg(1, Array, strDelimiter='.')
    def _resolve(self, cname, session=None, **opts):
        from ..models.instances import Instance
        session = session or scoped_session(session_maker())()
        fc_repos = [r for r in session._repos if issubclass(r.instanceClass, Instance)]
        root = cname[0]
        ns = cname[1:]
        for r in fc_repos:
            v = r.get(root)
            if v is not None:
                return v if not ns else v.resolve_cname(ns)
        raise InvalidValue('impossible to resolve %s in context' % repr('.'.join(cname[1:])))

        from ..utils import Context
        cur = Type.make_context(self, context)
        for i, n in enumerate(cname):
            if n in cur:
                v = cur[n]
            else:
                try:
                    v = ForeignKey.resolve(self, n, context=cur)
                except Exception as er:
                    raise InvalidValue('impossible to resolve %s in context' % repr('.'.join(cname[:i + 1])))
            cur = Context(v)
        return v



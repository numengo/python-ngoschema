# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import datetime
import arrow
import pathlib
import urllib.parse

from ..managers.type_builder import register_type
from ..contexts.ns_manager_context import find_ns_mgr, NsManagerContext
from ..resolvers.uri_resolver import resolve_uri, scope
from ..protocols import Resolver, Context
from .type import Primitive
from .strings import String


@register_type('uri')
class Uri(Primitive, Resolver):
    """
    Add additional 'uri' to json-schema associated in python to urllib.parse.ParseResult
    """
    _pyType = urllib.parse.ParseResult

    @staticmethod
    def _check(self, value, **opts):
        """
        Checks value type against urllib.parse.ParseResult, pathlib.Path and String
        :param value: value to test
        :return: True if compatible
        """
        if Primitive._check(self, value) or isinstance(value, pathlib.Path) or String.check(value, **opts):
            return value
        raise TypeError('%s is not type Uri.' % value)

    @staticmethod
    def _convert(self, value, **opts):
        """
        Convert from pathlib.Path using as_uri of force to string before parsing using urllib.parse.urlparse

        :param value: value to instanciate
        :param context: evaluation context
        :return: urllib.parse.ParsedResult instance
        """
        if not isinstance(value, urllib.parse.ParseResult):
            s = value.resolve().as_uri() if isinstance(value, pathlib.Path) else String.convert(value, **opts)
            return urllib.parse.urlparse(s)
        return value

    @staticmethod
    def _serialize(self, value, **opts):
        """
        returns for json using urllib.parse.ParsedResult.geturl
        :param value: value (typed or not)
        :param context: evaluation context
        :return: json data
        """
        return Uri._convert(self, value, **opts).geturl()

    @staticmethod
    def _resolve(self, value, **opts):
        return resolve_uri(Uri._serialize(self, value, **opts), **opts)


# https://regex101.com/r/njslOV/2
cn_re = re.compile(r"^[\.\da-zA-Z_]+$")


@register_type('id')
class Id(NsManagerContext, String):
    _canonical = False

    def __init__(self, **opts):
        String.__init__(self, **opts)
        self._canonical = self._schema.get('canonical', self._canonical)

    @staticmethod
    def _check(self, value, canonical=True, context=None, **opts):
        if Uri._check(self, value, **opts) and '#' in Uri.serialize(value, context=context):
            return value
        m = cn_re.search(String.convert(value, **opts))
        if m and canonical:
            uri = find_ns_mgr(context).get_cname_id(m.group())
            return value
        raise TypeError('%s is not type Id.' % value)

    @staticmethod
    def _convert(self, value, context=None, **opts):
        uri = value
        if value:
            ns_mgr = find_ns_mgr(context or self._context)
            if cn_re.search(uri):
                uri = ns_mgr.get_cname_id(uri)
            if '#' not in uri:
                uri = uri + '#'
            uri = scope(uri, ns_mgr.currentNsUri)
        return uri

    @staticmethod
    def _serialize(self, value, context=None, **opts):
        ns_mgr = find_ns_mgr(context or self._context)
        canonical = opts.get('canonical', self._canonical)
        if canonical:
            return ns_mgr.get_id_cname(value)
        else:
            doc_id = ns_mgr.currentNsUri.split('#')[0]
            if value.startswith(doc_id + '#'):
                value = value[len(doc_id):]
            return value


@register_type('canonical')
class Canonical(Id):
    _canonical = True


@register_type('path')
class Path(Uri):
    """
    Add additional 'path' to json-schema associated in python to pathlib.Path
    """
    _pyType = pathlib.Path
    _expandUser = False
    _relative = None
    _isPathExisting = False
    _isPathDir = False
    _isPathFile = False

    def __init__(self, **opts):
        Primitive.__init__(self, **opts)
        self._expandUser = self._schema.get('expandUser', self._expandUser)
        self._isPathExisting = self._schema.get('isPathExisting', self._isPathExisting)
        self._isPathDir = self._schema.get('isPathDir', self._isPathDir)
        self._isPathFile = self._schema.get('isPathFile', self._isPathFile)

    @staticmethod
    def _convert(self, value, resolve=False, **opts):
        """
        convert from urllib.parse.ParsedResult, unquoting the url.
        """
        typed = value
        if isinstance(typed, urllib.parse.ParseResult):
            typed = pathlib.Path(urllib.parse.unquote(typed.geturl()))
        elif typed:
            # cast to str to make sure the path is converted
            typed = pathlib.Path(String.convert(str(typed), **opts))
        expand_user = opts.get('expand_user', self._expandUser)
        if expand_user:
            typed = typed.expanduser()
        if resolve:
            typed = typed.resolve()
        return typed

    @staticmethod
    def _serialize(self, value, context=None, **opts):
        relative = opts.get('relative', self._relative)
        if relative:
            from ..repositories import FileRepository
            ctx = self._create_context(self, context)
            fr = ctx.find_file_repository()
            if fr and fr.document:
                fp = fr.document.filepath
                from pathlib import Path
                p = value.relative_to(fp)
        return str(value)

    @staticmethod
    def _resolve(self, typed, **opts):
        return typed.resolve()


PathExists = Path.extend_type('PathExists', isPathExisting=True)
PathDir = Path.extend_type('PathDir', isPathDir=True)
PathFile = Path.extend_type('PathFile', isPathFile=True)
PathDirExists = PathDir.extend_type('PathDirExists', isPathExisting=True)
PathFileExists = PathFile.extend_type('PathFileExists', isPathExisting=True)

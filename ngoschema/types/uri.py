# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import arrow
import pathlib
import urllib.parse

from ..exceptions import ValidationError, InvalidValue
from ..managers.type_builder import register_type
from ..resolver import scope
from .. import settings
from .type import Primitive
from .strings import String


def find_ns_mgr(context):
    from ..managers.namespace_manager import NamespaceManager, default_ns_manager
    return next((m for m in context.maps if isinstance(m, NamespaceManager)), default_ns_manager)


@register_type('uri')
class Uri(Primitive):
    """
    Add additional 'uri' to json-schema associated in python to urllib.parse.ParseResult
    """
    _py_type = urllib.parse.ParseResult

    def _check(self, value, **opts):
        """
        Checks value type against urllib.parse.ParseResult, pathlib.Path and String
        :param value: value to test
        :return: True if compatible
        """
        return Primitive._check(self, value) or isinstance(value, pathlib.Path) or String.check(value, **opts)

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

    def _serialize(self, value, **opts):
        """
        returns for json using urllib.parse.ParsedResult.geturl
        :param value: value (typed or not)
        :param context: evaluation context
        :return: json data
        """
        return Uri.convert(value, **opts).geturl()


@register_type('id')
class Id(String):
    _doc_id = ''
    _ns_mgr = None

    def __init__(self, **schema):
        String.__init__(self, **schema)

    def __repr__(self):
        uri = self._data_validated.get('uri') or self._data.get('uri')
        return f'<id {uri}>'

    def _check(self, value, **opts):
        return Uri._check(self, value, **opts) and '#' in str(value)

    def set_context(self, context=None, *extra_contexts):
        String.set_context(self, context, *extra_contexts)
        self._ns_mgr = find_ns_mgr(self._context)

    def _convert(self, value, context=None, **opts):
        uri = value
        if value:
            ns_mgr = find_ns_mgr(context)
            if '/' not in uri:
                uri = ns_mgr.get_cname_id(uri)
            if '#' not in uri:
                uri = uri + '#'
            uri = scope(uri, ns_mgr.currentNsUri)
        return uri

    def _serialize(self, value, canonical=False, context=None, **opts):
        ns_mgr = find_ns_mgr(context)
        if canonical:
            return ns_mgr.get_id_cname(value)
        else:
            doc_id = ns_mgr.currentNsUri.split('#')[0]
            if value.startswith(doc_id + '#'):
                value = value[len(doc_id):]
            return value


@register_type('path')
class Path(Uri):
    """
    Add additional 'path' to json-schema associated in python to pathlib.Path
    """
    _py_type = pathlib.Path
    _expand_user = False
    _resolve = False

    def __init__(self, **schema):
        Primitive.__init__(self, **schema)
        self._expand_user = self._schema.get('expandUser', False)
        self._resolve = self._schema.get('resolve', False)

    def _convert(self, value, **opts):
        """
        convert from urllib.parse.ParsedResult, unquoting the url.
        """
        typed = value
        if isinstance(typed, urllib.parse.ParseResult):
            typed = pathlib.Path(urllib.parse.unquote(typed.geturl()))
        elif typed:
            # cast to str to make sure the path is converted
            typed = pathlib.Path(String.convert(str(typed), **opts))
        if self._expand_user:
            typed = typed.expanduser()
        if self._resolve:
            typed = typed.resolve()
        return typed

    def _evaluate___(self, value, expand_user=None, resolve=None, **opts):
        """
        convert and eventually resolve path from from urllib.parse.ParsedResult, unquoting the url.

        :param value: value to instanciate
        :param expand_user: boolean to expand user path
        :param resolve: boolean to resolve the path
        :return: pathlib.Path instance
        """
        validate = opts.pop('validate', self._validate)
        if expand_user is None:
            expand_user = self._expand_user
        if resolve is None:
            resolve = self._resolve
        typed = Uri._evaluate(self, value, validate=False, **opts)
        if expand_user:
            typed = typed.expanduser()
        if resolve:
            typed = typed.resolve()
        if validate:
            self.validate(typed)
        return typed

    def _serialize(self, value, context=None, relative=False, **opts):
        if relative:
            from ..repositories import FileRepository
            ctx = self.create_context(context)
            fr = ctx.find_file_repository()
            if fr and fr.document:
                fp = fr.document.filepath
                from pathlib import Path
                p = value.relative_to(fp)
        return str(value)


PathExists = Path.extend_type('PathExists', isPathExisting=True)
PathDir = Path.extend_type('PathDir', isPathDir=True)
PathFile = Path.extend_type('PathFile', isPathFile=True)
PathDirExists = PathDir.extend_type('PathDirExists', isPathExisting=True)
PathFileExists = PathFile.extend_type('PathFileExists', isPathExisting=True)

# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import arrow
import pathlib
import urllib.parse

from ..exceptions import ValidationError, InvalidValue
from .type import Primitive
from ..managers.type_builder import register_type
from .strings import String
from .. import settings


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

    def __init__(self, **schema):
        String.__init__(self, **schema)

    def _check(self, value, **opts):
        return Uri._check(self, value, **opts) and '#' in str(value)

    def _make_context(self, context=None, *extra_contexts):
        from ..managers.namespace_manager import NamespaceManager, default_ns_manager
        String._make_context(self, context, *extra_contexts)
        self._ns_mgr = next((m for m in self._context.maps if isinstance(m, NamespaceManager)), default_ns_manager)

    def _convert(self, value, context=None, **opts):
        uri = value
        if value:
            String._make_context(context, opts)
            if '/' not in uri:
                uri = self._ns_mgr.get_cname_id(uri)
            if '#' not in uri:
                uri = uri + '#'
        return uri

    def _serialize(self, value, canonical=False, context=None, **opts):
        Id._make_context(self, context)
        if canonical:
            return self._ns_mgr.get_id_cname(value)
        else:
            doc_id = self._ns_mgr._current_ns_uri
            if value.startswith(doc_id):
                value = value[len(doc_id):]
            return value


@register_type('path')
class Path(Uri):
    """
    Add additional 'path' to json-schema associated in python to pathlib.Path
    """
    _py_type = pathlib.Path

    def __init__(self, **schema):
        Primitive.__init__(self, **schema)
        self._expand_user = schema.get('expandUser', False)
        self._resolve = schema.get('resolve', False)

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
        return typed

    def __call__(self, value, expand_user=None, resolve=None, validate=True, **opts):
        """
        convert and eventually resolve path from from urllib.parse.ParsedResult, unquoting the url.

        :param value: value to instanciate
        :param expand_user: boolean to expand user path
        :param resolve: boolean to resolve the path
        :return: pathlib.Path instance
        """
        if expand_user is None:
            expand_user = self._expand_user
        if resolve is None:
            resolve = self._resolve
        typed = Uri.__call__(self, value, validate=False, **opts)
        if expand_user:
            typed = typed.expanduser()
        if resolve:
            typed = typed.resolve()
        if validate:
            self.validate(typed)
        return typed

    def _serialize(self, value, **opts):
        return str(value)


PathExists = Path.extend_type('PathExists', isPathExisting=True)
PathDir = Path.extend_type('PathDir', isPathDir=True)
PathFile = Path.extend_type('PathFile', isPathFile=True)
PathDirExists = PathDir.extend_type('PathDirExists', isPathExisting=True)
PathFileExists = PathFile.extend_type('PathFileExists', isPathExisting=True)

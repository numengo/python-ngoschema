# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import re
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


# https://regex101.com/r/njslOV/2
cn_re = re.compile(r"^[\.a-zA-Z_]+$")


@register_type('id')
class Id(String):
    _doc_id = ''
    _canonical = False

    def __init__(self, **schema):
        String.__init__(self, **schema)

    def __repr__(self):
        uri = self._data_validated.get('uri') or self._data.get('uri')
        return f'<id {uri}>'

    def _check(self, value, canonical=True, context=None, **opts):
        if Uri._check(self, value, **opts) and '#' in Uri.serialize(value, context=context):
            return True
        m = cn_re.search(String.convert(value, **opts))
        if m and canonical:
            try:
                uri = find_ns_mgr(context).get_cname_id(m.group())
                return True
            except Exception as er:
                pass
        return False

    def _convert(self, value, context=None, **opts):
        uri = value
        if value:
            ns_mgr = find_ns_mgr(context)
            if cn_re.search(uri):
                uri = ns_mgr.get_cname_id(uri)
            if '#' not in uri:
                uri = uri + '#'
            uri = scope(uri, ns_mgr.currentNsUri)
        return uri

    def _serialize(self, value, canonical=None, context=None, **opts):
        ns_mgr = find_ns_mgr(context)
        canonical = self._canonical if canonical is None else canonical
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

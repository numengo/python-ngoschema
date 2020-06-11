# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from urllib.parse import urlparse, urlsplit
import inflection
import re
from .. import settings
from functools import lru_cache

from ..exceptions import InvalidValue
from ..utils import ReadOnlyChainMap as ChainMap, ContextManager
from ..resolver import resolve_uri
from ..decorators import memoized_method

CLEAN_JS_NAME_REGEX = re.compile(r"[^a-zA-z0-9\.\-_]+")


def clean_js_name(name):
    return CLEAN_JS_NAME_REGEX.sub("", name.split(':')[-1]).replace('-', '_')


def clean_def_name(name):
    return inflection.camelize(clean_js_name(name))


def clean_for_uri(name):
    return name.split(':')[-1].replace('_', '-')


class NamespaceManager(ContextManager):

    def __init__(self, *parents, **local):
        local.setdefault('', settings.MS_DOMAIN)
        self._local = local
        ContextManager.__init__(self, local, *parents)

    def add(self, uri, name=None):
        if not uri.split('#')[0]:
            uri = self[''].split('#')[0] + uri
        #self._local[name or NamespaceManager._uri_to_cname(uri)] = uri.split('#')[0]
        self._local[NamespaceManager._uri_to_cname(uri) if name is None else name] = uri

    @memoized_method(maxsize=2048)
    def get_id_cname(self, ref):
        ns = ChainMap(self, NamespaceManager.builder_namespaces(), NamespaceManager.available_namespaces())
        ns_names = [k for k, uri in sorted(ns.items(), key=lambda x: len(x[1]), reverse=True)
                    if ref.startswith(uri)]
        ns_name = ns_names[0] if ns_names else NamespaceManager._uri_to_cname(ref.split('#')[0])
        return ns_name + NamespaceManager._fragment_to_cname(ref.split('#')[-1])

    @memoized_method(maxsize=2048)
    def get_cname_id(self, cname):
        ns = ChainMap(self, NamespaceManager.builder_namespaces(), NamespaceManager.available_namespaces())
        # iterate on namespace sorted from the longest to get the most qualified
        ns_names = [k for k, uri in sorted(ns.items(), key=lambda x: len(x[1]), reverse=True)
                    if cname.startswith(k+'.') or k == cname]
        ns_name = ns_names[0] if ns_names else ''
        uri = ns[ns_name]
        fragment_cname = cname[len(ns_name):]
        fragment_parts = []
        if fragment_cname:
            cur = resolve_uri(uri)
            for c in fragment_cname.split('.'):
                if not c:
                    #fragment_parts += ['']
                    continue
                for k in ['$defs', 'definitions', 'properties']:
                    if c in cur.get(k, {}):
                        fragment_parts += [k, c]
                        cur = cur[k][c]
                        break
                else:
                    for reg, sch in cur.get('patternProperties', {}).items():
                        if re.compile(reg).search(c):
                            fragment_parts += ['patternProperties', reg]
                            cur = cur['patternProperties'][reg]
                    else:
                        if cur.get('additionalProperties', True):
                            fragment_parts += ['additionalProperties']
                            cur = cur.get('additionalProperties')
                        else:
                            raise InvalidValue('%s is not permitted in %s' % (cname))
        return '/'.join([uri + ('#' if '#' not in uri else '')] + fragment_parts)

    @staticmethod
    def _fragment_to_cname(uri_fragment):
        fragments = uri_fragment.split('/')
        return '.'.join([clean_js_name(s) for i, s in enumerate(fragments) if not i % 2 or i == len(fragments)-1])

    @staticmethod
    @lru_cache(maxsize=2048)
    def _uri_to_cname(uri):
        u = urlparse(uri)
        ns_name = u.path[1:].replace('-', '_').replace('/', '.')
        return ns_name + NamespaceManager._fragment_to_cname(u.fragment) if u.fragment else ns_name

    @staticmethod
    def builder_namespaces():
        from .type_builder import TypeBuilder
        return {NamespaceManager._uri_to_cname(uri): uri
                for uri in {k.split('#')[0] for k in TypeBuilder._registry.keys()}}

    @staticmethod
    def available_namespaces():
        from ..resolver import UriResolver
        return {NamespaceManager._uri_to_cname(k): k for k in UriResolver._doc_store.keys()}

    def load(self, cname):
        from .type_builder import TypeBuilder
        return TypeBuilder.load(self.get_cname_id(cname))


default_ns_manager = NamespaceManager()

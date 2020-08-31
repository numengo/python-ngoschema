# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from urllib.parse import urlparse, urlsplit, urldefrag
import inflection
import re
from collections import OrderedDict
from functools import lru_cache

from .. import settings
from ..exceptions import InvalidValue
from ..utils import ReadOnlyChainMap as ChainMap, Registry
from ..resolver import resolve_uri, UriResolver

CLEAN_JS_NAME_REGEX = re.compile(r"[^a-zA-z0-9\.\-_]+")


def clean_js_name(name):
    return CLEAN_JS_NAME_REGEX.sub("", name.split(':')[-1]).replace('-', '_')


def clean_def_name(name):
    return inflection.camelize(clean_js_name(name))


def clean_for_uri(name):
    return name.split(':')[-1].replace('_', '-')


class NamespaceManager(Registry):
    _current_ns = ''
    _current_ns_uri = '#'

    def __init__(self, *parents, **local):
        self._get_id_cname = lru_cache(1024)(self._get_id_cname_cached)
        self._get_cname_id = lru_cache(1024)(self._get_cname_id_cached)
        self._local = dict(local)
        self._local.setdefault('', self._current_ns_uri)
        self._registry = ChainMap(self._local, *parents)

    def add(self, uri, name=None):
        if not uri.split('#')[0]:
            uri = self._registry[''].split('#')[0] + uri
        self._local[NamespaceManager._uri_to_cname(uri) if name is None else name] = uri

    def set_current(self, name):
        ns_names = sorted([k for k in self._registry.keys() if name.startswith(k)])
        assert ns_names, name
        cname = ns_names[-1]
        self._current_ns = cname
        self._current_ns_uri = self._local[''] = self._registry[cname]

    def get_id_cname(self, ref):
        cname = self._get_id_cname(ref)
        rcn = self._current_ns
        if rcn and cname.startswith(rcn):
            local_cn = cname[len(rcn):].split('.')
            if local_cn and not local_cn[0]:
                return '.'.join(local_cn[1:])
            return rcn
        return cname

    def _get_id_cname_cached(self, ref):
        from ..types.uri import Uri
        ns = ChainMap(self._registry, NamespaceManager.builder_namespaces(), NamespaceManager.available_namespaces())
        ns_uri, frag = urldefrag(ref)
        ns_names = [k for k, uri in sorted(ns.items(), key=lambda x: len(x[1]), reverse=True)
                    if ref.startswith(uri)]
        ns_cn = ns_names[0] if ns_names else Uri.convert(ref).path.replace('/', '.')
        cn = ns_cn
        if frag:
            f_cn = NamespaceManager._fragment_to_cname(frag)
            return '%s.%s' % (ns_cn, f_cn)
        return ns_cn

    def get_cname_id(self, cname):
        if cname.startswith('.'):
            rcn = self._current_ns.split('.')
            cname = cname[1:]
            while cname[0] == '.':
                rcn.pop()
                cname = cname[1:]
            cname = '.'.join(rcn + [cname])
        return self._get_cname_id(cname)

    def _get_cname_id_cached(self, cname):
        ns = ChainMap(self._registry, NamespaceManager.builder_namespaces(), NamespaceManager.available_namespaces())
        # iterate on namespace sorted from the longest to get the most qualified
        ns_names = [k for k, uri in sorted(ns.items(), key=lambda x: len(x[1]), reverse=True)
                    if cname.startswith(k+'.') or k == cname]
        ns_name = ns_names[0] if ns_names else ''
        ns_uri = ns[ns_name]
        fragment_cname = cname[len(ns_name):]
        cns = fragment_cname.split('.')
        if cns and not cns[0]:
            cns = cns[1:]
        fragment_parts = []
        if fragment_cname:
            if ns_uri in UriResolver._doc_store:
                import dpath.util
                doc = resolve_uri(ns_uri)
                glob = ''.join(['/*/'+c for c in cns])
                glob = glob.strip('/')
                for x in dpath.util.search(doc, glob, yielded=True):
                    return ns_uri + ('#/' if '#' not in ns_uri else '/') + x[0]
                # not found: if namespace uri corresponds to local namespace, compute a path
                #if ns_uri != ns.get(''):
                #    raise InvalidValue(f"impossible to find '{cname}' in {ns_uri}.")
            for c in cns[:-1]:
                fragment_parts += ['$defs', c]
            fragment_parts += (['properties', cns[-1]] if len(cns) > 2 and cns[-2][0].isupper() and cns[-1][0].islower() else ['$defs', cns[-1]])
        return '/'.join([ns_uri + ('#' if '#' not in ns_uri else '')] + fragment_parts)

    @staticmethod
    def _fragment_to_cname(uri_fragment):
        fragments = uri_fragment.lstrip('/').split('/')
        return '.'.join([clean_js_name(s) for i, s in enumerate(fragments) if not (i+1) % 2 or i == len(fragments)-1])

    @staticmethod
    @lru_cache(maxsize=2048)
    def _uri_to_cname(uri):
        u = urlparse(uri)
        cn = []
        for p in u.path.split('/'):
            if p:
                if p[0].isdigit() and cn:
                    cn[-1] += '_' + p.replace('-', '_')
                elif not p[0].isdigit():
                    cn.append(p.replace('-', '_'))
        ns_name = '.'.join(cn)
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

    def namespaces(self, contains=None):
        ns = ChainMap(self._registry, NamespaceManager.builder_namespaces(), NamespaceManager.available_namespaces())
        nsk = list(ns.keys())
        if contains:
            nsk = [n for n in nsk if contains in n]
        return OrderedDict([(k, ns[k]) for k in sorted(nsk)])

    def get_cname_definitions(self, cname):
        ns_uri = self.get_cname_id(cname)
        doc = resolve_uri(ns_uri)
        defs = {}
        for tag in ['$defs', 'definitions']:
            for k, v in doc.get(tag, {}).items():
                defs[f'{cname}.{k}'] = f'{ns_uri}/{tag}/{k}'
        return defs


default_ns_manager = NamespaceManager()

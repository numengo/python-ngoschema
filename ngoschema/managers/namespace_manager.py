# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from urllib.parse import urlparse
import inflection
import re
from collections import OrderedDict
from functools import lru_cache

from .. import settings
from ..utils import ReadOnlyChainMap as ChainMap, Registry
from ngoschema.resolvers.uri_resolver import resolve_uri, UriResolver

CLEAN_JS_NAME_REGEX = re.compile(r"[^a-zA-z0-9\.\-_]+")
MS_NETLOC = urlparse(settings.MS_DOMAIN).netloc


def clean_js_name(name):
    return CLEAN_JS_NAME_REGEX.sub("", name.split(':')[-1]).replace('-', '_')


def clean_def_name(name):
    return inflection.camelize(clean_js_name(name))


def clean_for_uri(name):
    return name.split(':')[-1].replace('_', '-')


class NamespaceManager(Registry):
    _current_ns = ''
    _current_ns_uri = '#'
    _builder_ns = {}

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

    @property
    def currentNs(self):
        return self._current_ns

    @property
    def currentNsUri(self):
        return self._current_ns_uri

    def _find_ns_by_cname(self, cname):
        reg = ChainMap(self._registry, self._builder_ns)
        ns_names = sorted([c for c, u in reg.items() if cname.startswith(c+'.') or c == cname], reverse=True)
        if ns_names:
            cn = ns_names[0]
            return cn, reg[cn]
        for u in UriResolver._doc_store.keys():
            c = NamespaceManager._uri_to_cname(u)
            if cname.startswith(c+'.') or c == cname:
                return c, u
        return None, None

    def _find_ns_by_uri(self, uri):
        reg = ChainMap(self._registry, self._builder_ns)
        ns_names = sorted([c for c, u in reg.items() if uri.startswith(u)], reverse=True)
        if ns_names:
            cn = ns_names[0]
            return cn, reg[cn]
        uri_ns = uri.split('#')[0] if '#' in uri else uri
        if uri_ns in UriResolver._doc_store.keys():
            return NamespaceManager._uri_to_cname(uri_ns), uri_ns
        return None, None

    def __contains__(self, item):
        from ..types.symbols import Module
        if Module.check(item):
            item = item.__module__
        n, u = self._find_ns_by_cname(item)
        return bool(n and u)

    def get_id_cname(self, ref, relative=False):
        rcn = self._current_ns
        cname = self._get_id_cname(ref, rcn)
        if relative and rcn and cname.startswith(rcn):
            local_cn = cname[len(rcn):].split('.')
            if local_cn and not local_cn[0]:
                return '.'.join(local_cn[1:])
            return rcn
        return cname

    def _get_id_cname_cached(self, ref, current_ns):
        ns_cn, ns_uri = self._find_ns_by_uri(ref)
        #ns = ChainMap(self._registry, NamespaceManager.builder_namespaces(), NamespaceManager.available_namespaces())
        #ns_names = sorted([k for k, uri in ns.items() if ref.startswith(uri)], reverse=True)
        #ns_uri = ns.get(ns_names[0]) if ns_names else urldefrag(ref)[0]
        #ns_cn = ns_names[0] if ns_names else Uri.convert(ref).path.replace('/', '.')
        cn = ns_cn or current_ns
        frag = ref[len(ns_uri):] if ns_uri and ref.startswith(ns_uri) else ref
        #ns_uri, frag = urldefrag(ref)
        if frag:
            f_cn = NamespaceManager._fragment_to_cname(frag.strip('#'))
            return f'{ns_cn}.{f_cn}' if ns_cn else f_cn
        return ns_cn

    def get_cname_id(self, cname):
        if cname.startswith('.'):
            rcn = self._current_ns.split('.')
            cname = cname[1:]
            while cname[0] == '.':
                rcn.pop()
                cname = cname[1:]
            cname = '.'.join(rcn + [cname])
        id = self._get_cname_id(cname, self._current_ns)
        u = self._current_ns_uri.split('#')[0] + '#'
        if u and id.startswith(u):
            id = id[len(u.strip('#')):]
        return id

    def _get_cname_id_cached(self, cname, current_ns):
        #ns = ChainMap(self._registry, NamespaceManager.builder_namespaces(), NamespaceManager.available_namespaces())
        # iterate on namespace sorted from the longest to get the most qualified
        #ns_names = sorted([k for k, uri in ns.items() if cname.startswith(k+'.') or k == cname], reverse=True)
        #ns_name = ns_names[0] if ns_names else ''
        #ns_uri = ns[ns_name]
        ns_name, ns_uri = self._find_ns_by_cname(cname)
        fragment_cname = cname[len(ns_name):] if ns_name else cname
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
        ns_uri = ns_uri or self._find_ns_by_cname(current_ns)[1]
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
        if u.netloc != MS_NETLOC:
            cn = [u.netloc.split('.')[0].replace('-', '_')]
        for p in u.path.split('/'):
            if p:
                if p[0].isdigit() and cn:
                    cn[-1] += '_' + p.replace('-', '_')
                elif not p[0].isdigit():
                    cn.append(p.replace('-', '_'))
        ns_name = '.'.join(cn)
        return ns_name + NamespaceManager._fragment_to_cname(u.fragment) if u.fragment else ns_name

    @staticmethod
    def register_ns(uri, cname=None):
        ns_uri = uri.split('#')[0] if '#' in uri else uri
        cname = cname or NamespaceManager._uri_to_cname(ns_uri)
        if cname not in NamespaceManager._builder_ns:
            NamespaceManager._builder_ns[cname] = ns_uri

    #@staticmethod
    #def builder_namespaces():
    #    from .type_builder import TypeBuilder
    #    return {NamespaceManager._uri_to_cname(uri): uri
    #            for uri in {k.split('#')[0] for k in TypeBuilder._registry.keys()}}
    #
    @staticmethod
    def available_namespaces():
        from ngoschema.resolvers.uri_resolver import UriResolver
        return {NamespaceManager._uri_to_cname(k): k for k in UriResolver._doc_store.keys()}

    def load(self, cname):
        from .type_builder import type_builder
        return type_builder.load(self.get_cname_id(cname))

    def namespaces(self, contains=None):
        ns = ChainMap(self._registry, self._builder_ns, NamespaceManager.available_namespaces())
        nsk = list(ns.keys())
        if contains:
            nsk = [n for n in nsk if contains in n]
        return OrderedDict([(k, ns[k]) for k in sorted(nsk)])

    def get_cname_definitions(self, cname):
        ns_uri = self.get_id_cname(cname)
        doc = resolve_uri(ns_uri)
        defs = {}
        for tag in ['$defs', 'definitions']:
            for k, v in doc.get(tag, {}).items():
                defs[f'{cname}.{k}'] = f'{ns_uri}/{tag}/{k}'
        return defs


default_ns_manager = NamespaceManager()

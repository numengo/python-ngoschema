# *- coding: utf-8 -*-
"""
Jinja2 serializer and custom filters

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import re
import functools
from builtins import object
from builtins import str

import inflection
import jinja2
import jinja2.parser

from .utils import GenericClassRegistry

# default jinja2 environment instance
_default_jinja_env = None

_jinja2_globals = {}
_jinja2_globals['enumerate'] = enumerate
_jinja2_globals['len'] = len
_jinja2_globals['str'] = str
_jinja2_globals['list'] = list


def extend_jinja2_globals(**globals):
    _jinja2_globals.update(**globals)


def default_jinja2_env():
    """
    Return the default Jinja2 Environment with prefixed modules
    """
    global _default_jinja_env
    if _default_jinja_env is None:
        from ..query import Query
        extensions = ['jinja2.ext.loopcontrols', 'jinja2.ext.i18n']
        _default_jinja_env = ModulePrefixedJinja2Environment(extensions=extensions)
        _default_jinja_env.globals.update(**_jinja2_globals,
                                          Query=Query)
    return _default_jinja_env


regex_has_dot = re.compile(r"(\{\{\s*\w+\.)")


class TemplatedString(object):
    """
    Returns a templated string for a given context
    """

    def __init__(self, templated_str):
        self._templated_str = str(templated_str)
        self._template = default_jinja2_env().from_string(self._templated_str)
        self._has_dot = regex_has_dot.search(self._templated_str) is not None

    def __call__(self, *args, **kwargs):
        return self._template.render(*args, **kwargs)


@functools.lru_cache(512)
def get_jinja2_variables(source, remove_this=True):
    """return the list of variables in jinja2 source (no filters)"""
    env = default_jinja2_env()
    parser = jinja2.parser.Parser(env, source)
    vars = []
    var = []
    processing = False
    for t in parser.stream:
        if t.type == 'variable_begin':
            processing = True
            continue
        if processing:
            if t.type == 'variable_end' or t.value == '|':
                processing=False
                vars.append(''.join(var))
                var = []
                continue
            if t.type == 'integer' and var[-1] == '.':
                var.pop(-1)
                var.append(f'[{t.value}]')
            else:
                var.append(t.value)
    return vars if not remove_this \
        else [v.replace('this.', '').replace('self.', '') for v in vars]

# ADDITIONAL FILTERS FROM INFLECTION


filters_registry = GenericClassRegistry()


@filters_registry.register()
def camelize(string, uppercase_first_letter=True):
    __doc__ = inflection.camelize.__doc__
    return inflection.camelize(str(string), uppercase_first_letter)


@filters_registry.register()
def dasherize(word):
    __doc__ = inflection.dasherize.__doc__
    return inflection.dasherize(str(word))


@filters_registry.register()
def ordinal(number):
    __doc__ = inflection.ordinal.__doc__
    return inflection.ordinal(int(number))


@filters_registry.register()
def ordinalize(number):
    __doc__ = inflection.ordinalize.__doc__
    return inflection.ordinalize(int(number))


@filters_registry.register()
def parameterize(string, separator="-"):
    __doc__ = inflection.parameterize.__doc__
    return inflection.parameterize(str(string), separator)


@filters_registry.register()
def pluralize(word):
    __doc__ = inflection.pluralize.__doc__
    return inflection.pluralize(str(word))


@filters_registry.register()
def singularize(word):
    __doc__ = inflection.singularize.__doc__
    return inflection.singularize(str(word))


@filters_registry.register()
def tableize(word):
    __doc__ = inflection.tableize.__doc__
    return inflection.tableize(str(word))


@filters_registry.register()
def titleize(word):
    __doc__ = inflection.titleize.__doc__
    return inflection.titleize(str(word))


@filters_registry.register()
def transliterate(string):
    __doc__ = inflection.transliterate.__doc__
    return inflection.transliterate(str(string))


@filters_registry.register()
def underscore(word):
    __doc__ = inflection.underscore.__doc__
    return inflection.underscore(str(word))


@filters_registry.register()
def slugify(string):
    from slugify import slugify as _slugify
    return _slugify(string)


@filters_registry.register()
def split(string, sep=',', maxsplit=-1):
    return (string or '').split(sep, maxsplit)


@filters_registry.register()
def rsplit(string, sep=',', maxsplit=-1):
    return (string or '').rsplit(sep, maxsplit)


@filters_registry.register()
def last(any):
    return any[-1]


class ModulePrefixedJinja2Environment(jinja2.Environment):
    logger = logging.getLogger(__name__ + ".DefaultJinja2Environment")
    _extra_opts = {
        "trim_blocks": True,
        "lstrip_blocks": True,
        "keep_trailing_newline": True,
    }

    def __init__(self, **opts):
        self.loader = jinja2.PrefixLoader({})
        from ngoschema.query import Query
        jinja2.Environment.__init__(self, loader=self.loader, **opts, **self._extra_opts)
        self.globals.update(**_jinja2_globals, Query=Query)

        # add filters
        for k, v in filters_registry.items():
            self.filters[k] = v

    def update_loader(self):
        from ..loaders import templates_module_loader
        self.loader.mapping = {
            mname: jinja2.PackageLoader(mname, path.name)
            for mname, paths in templates_module_loader.items()
            for path in paths
        }

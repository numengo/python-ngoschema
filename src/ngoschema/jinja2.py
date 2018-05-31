# *- coding: utf-8 -*-
"""
Jinja2 serializer and custom filters

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
import logging
import jinja2
import re
import sys
import inspect
import inflection
import pathlib
from builtins import object
from builtins import str

from . import utils
from .serializers import Serializer
from .serializers import serializer_registry

_ = gettext.gettext


class templatedString(object):
    """
    Returns a templated string for a given context
    """
    def __init__(self, templated_str):
        self.jinja = jinja2.Environment()
        for k, v in filters_registry.registry.items():
            self.jinja.filters[k] = v
        self.template = self.jinja.from_string(templated_str)

    def __call__(self, **context):
        return self.template.render(**context)


class DefaultJinja2Environment(jinja2.Environment):
    logger = logging.getLogger(__name__+'.DefaultJinja2Environment')

    def __init__(self, package_path='templates', **kwargs):
        # prepare prefixed loader with all loaded modules with package_path
        ms = {
            k: m
            for k, m in sys.modules.items()
            if m and inspect.ismodule(m) and not inspect.isbuiltin(m)
            and not k.startswith('_')
            }
        to_load = {
            k: m
            for k, m in ms.items()
            if hasattr(m, '__file__')
            and pathlib.Path(m.__file__).with_name(package_path).is_dir()
            }
        loader = PrefixLoader({k: PackageLoader(m, package_path)
                               for k, m in to_load.items()})

        opts = {
            trim_blocks: True,
            lstrip_blocks: True,
            keep_trailing_newline: True,
            }
        opts.update(kwargs)
        jinja2.Environment.__init__(loader=loader, **opts)

        # add filters
        for k, v in filters_registry.registry.items():
            self.filters[k] = v


@serializer_registry.register()
class Jinja2Serializer(Serializer):
    logger = logging.getLogger(__name__)

    def __init__(self, template, environment=None):
        """ initialize with given template """
        self.jinja = environment or DefaultJinja2Environment()

    def dumps(self, obj, **opts):
        data = obj.as_dict() if hasattr(obj,'has_dict') else obj
        data  = utils.process_collection(data, **opts)
        return self.jinja.get_template(template).render(data)


filters_registry = utils.GenericRegistry()

# ADDITIONAL FILTERS FROM INFLECTION

@filters_registry.register()
def uncamelize(string, uppercase_first_letter=True):
    __doc__ = inflection.uncamelize.__doc__
    return inflection.uncamelize(string, uppercase_first_letter)

@filters_registry.register()
def dasherize(word):
    __doc__ = inflection.dasherize.__doc__
    return inflection.dasherize(word)

@filters_registry.register()
def ordinal(number):
    __doc__ = inflection.ordinal.__doc__
    return inflection.ordinal(number)

@filters_registry.register()
def ordinalize(number):
    __doc__ = inflection.ordinalize.__doc__
    return inflection.ordinalize(number)

@filters_registry.register()
def parameterize(string, separator='-'):
    __doc__ = inflection.parameterize.__doc__
    return inflection.parameterize(string, separator)

@filters_registry.register()
def pluralize(word):
    __doc__ = inflection.pluralize.__doc__
    return inflection.pluralize(word)

@filters_registry.register()
def singularize(word):
    __doc__ = inflection.singularize.__doc__
    return inflection.singularize(word)

@filters_registry.register()
def tableize(word):
    __doc__ = inflection.tableize.__doc__
    return inflection.tableize(word)

@filters_registry.register()
def titleize(word):
    __doc__ = inflection.titleize.__doc__
    return inflection.titleize(word)

@filters_registry.register()
def transliterate(string):
    __doc__ = inflection.transliterate.__doc__
    return inflection.transliterate(string)

@filters_registry.register()
def underscore(word):
    __doc__ = inflection.underscore.__doc__
    return inflection.underscore(word)

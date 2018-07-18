# *- coding: utf-8 -*-
"""
Jinja2 serializer and custom filters

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import six
import inspect
import logging
import pathlib
import re
import sys
from builtins import object
from builtins import str

import inflection
import jinja2

from . import utils
from .serializers import Serializer
from .serializers import serializer_registry

templates_module_loader = utils.GenericModuleFileLoader('templates')

# default jinja2 environment instance
_default_jinja_env = None


def default_jinja2_env():
    """
    Return the default Jinja2 Environment with prefixed modules
    """
    global _default_jinja_env
    if _default_jinja_env is None:
        _default_jinja_env = ModulePrefixedJinja2Environment()
    return _default_jinja_env


regex_has_dot = re.compile(r"(\{\{\s*\w+\.)")


class TemplatedString(object):
    """
    Returns a templated string for a given context
    """

    def __init__(self, templated_str):
        self.templated_str = templated_str
        self.template = default_jinja2_env().from_string(templated_str)
        self.has_dot = regex_has_dot.search(templated_str) is not None

    def __call__(self, obj):
        # ctx = context.as_dict() if hasattr(context,'as_dict') else context
        if not hasattr(obj, "as_dict") or not self.has_dot:
            return self.template.render(obj)
        return self.template.render({"this": obj})


@serializer_registry.register()
class Jinja2Serializer(Serializer):
    logger = logging.getLogger(__name__)

    def __init__(self, template, environment=None):
        """ initialize with given template """
        self.jinja = environment or default_jinja2_env()
        self.template = template

    def dump(self,
             obj,
             path,
             overwrite=False,
             protocol='w',
             encoding="utf-8",
             logger=None,
             **opts):
        __doc__ = Serializer.dump.__doc__
        logger = logger or self.logger
        logger.info("DUMP file %s", path)
        logger.debug("data:\n%r ", obj)

        if path.exists() and not overwrite:
            raise IOError("file %s already exists" % str(path))
        with io.open(str(path), protocol, encoding=encoding) as outfile:
            stream = self.dumps(obj, encoding=encoding, **opts)
            stream = six.text_type(stream)
            outfile.write(stream)

    def dumps(self, obj, **opts):
        data = obj.as_dict() if hasattr(obj, "as_dict") else obj
        data = utils.process_collection(data, **opts)
        return self.jinja.get_template(self.template).render(data)


# ADDITIONAL FILTERS FROM INFLECTION

filters_registry = utils.GenericRegistry()


@filters_registry.register()
def camelize(string, uppercase_first_letter=True):
    __doc__ = inflection.camelize.__doc__
    return inflection.camelize(string, uppercase_first_letter)


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


class ModulePrefixedJinja2Environment(jinja2.Environment):
    logger = logging.getLogger(__name__ + ".DefaultJinja2Environment")

    def __init__(self):
        loader = jinja2.PrefixLoader({
            mname: jinja2.PackageLoader(mname, path.name)
            for mname, paths in templates_module_loader.registry.items()
            for path in paths
        })

        opts = {
            "trim_blocks": True,
            "lstrip_blocks": True,
            "keep_trailing_newline": True,
        }
        jinja2.Environment.__init__(self, loader=loader, **opts)

        # add filters
        for k, v in filters_registry.registry.items():
            self.filters[k] = v        

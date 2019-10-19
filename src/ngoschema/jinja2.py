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
import os
import subprocess
import tempfile
from builtins import object
from builtins import str

import inflection
import jinja2
import jinja2.parser
import six
from future.utils import with_metaclass
from ngoschema.utils import templates_module_loader

from .schema_metaclass import SchemaMetaclass
from .document import Document
from .object_handlers import handler_registry, FileObjectHandler

from . import utils
from .query import Query

# default jinja2 environment instance
_default_jinja_env = None

_jinja2_globals = {}
_jinja2_globals['Query'] = Query
_jinja2_globals['enumerate'] = enumerate
_jinja2_globals['len'] = len
_jinja2_globals['str'] = str
_jinja2_globals['list'] = list

def resolve_ref_schema(ref):
    from .resolver import get_resolver
    return get_resolver().resolve(ref)[1]

_jinja2_globals['resolve_ref_schema'] = resolve_ref_schema

def extend_jinja2_globals(**globals):
    _jinja2_globals.update(**globals)

def default_jinja2_env():
    """
    Return the default Jinja2 Environment with prefixed modules
    """
    global _default_jinja_env
    if _default_jinja_env is None:
        _default_jinja_env = ModulePrefixedJinja2Environment(extensions=['jinja2.ext.loopcontrols'])
        _default_jinja_env.globals.update(_jinja2_globals)
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

    def __call__(self, **obj):
        # ctx = context.as_dict() if hasattr(context,'as_dict') else context
        return self._template.render(**obj)


def get_variables(source, remove_this=True):
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
            var.append(t.value)
    return vars if not remove_this \
        else [v.replace('this.', '').replace('self.', '') for v in vars]

# ADDITIONAL FILTERS FROM INFLECTION

filters_registry = utils.GenericClassRegistry()


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
    _extra_opts = {
        "trim_blocks": True,
        "lstrip_blocks": True,
        "keep_trailing_newline": True,
    }

    def __init__(self, **opts):
        loader = jinja2.PrefixLoader({
            mname: jinja2.PackageLoader(mname, path.name)
            for mname, paths in templates_module_loader.items()
            for path in paths
        })

        jinja2.Environment.__init__(self, loader=loader, **opts, **self._extra_opts)
        self.globals.update(_jinja2_globals)

        # add filters
        for k, v in filters_registry.items():
            self.filters[k] = v


@handler_registry.register()
class Jinja2FileObjectHandler(with_metaclass(SchemaMetaclass, FileObjectHandler)):
    __schema__ = "http://numengo.org/draft-05/ngoschema/object-handlers#/definitions/Jinja2FileObjectHandler"

    def __init__(self, template=None, environment=None, context=None, protectedRegions=None, **kwargs):
        """
        Serializer based on a jinja template. Template is loaded from
        environment. If no environment is provided, use the default one
        `default_jinja2_env`
        """
        FileObjectHandler.__init__(self, template=template, **kwargs)
        self._jinja = environment or default_jinja2_env()
        self._jinja.globals.update(_jinja2_globals)
        self._context = context or {}
        self._protected_regions = self._jinja.globals['protected_regions'] = protectedRegions or {}

    def pre_commit(self):
        return self._context

    def deserialize_data(self):
        raise Exception("not implemented")

    def serialize_data(self, data):
        self.logger.info("DUMP template '%s' file %s", self.template, self.document.filepath)
        self.logger.debug("data:\n%r ", data)

        stream = self._jinja.get_template(self.template).render(data)
        return six.text_type(stream)


@handler_registry.register()
class Jinja2MacroFileObjectHandler(with_metaclass(SchemaMetaclass, Jinja2FileObjectHandler)):
    __schema__ = "http://numengo.org/draft-05/ngoschema/object-handlers#/definitions/Jinja2MacroFileObjectHandler"

    def serialize_data(self, data):
        macro_args = self.macroArgs.for_json()
        if 'protected_regions' not in macro_args:
            macro_args.append('protected_regions')
        args = [k for k in macro_args if k in data]
        to_render = "{%% from '%s' import %s %%}{{%s(%s)}}" % (
            self.template, self.macroName, self.macroName, ', '.join(args))
        try:
            template = self._jinja.from_string(to_render)
            context = self._context.copy()
            context.update(**data)
            return template.render(context)
        except Exception as er:
            self.logger.error('SERIALIZE Jinja2MacroFileObjectHandler: %s', er)
            raise er


@handler_registry.register()
class Jinja2MacroTemplatedPathFileObjectHandler(with_metaclass(SchemaMetaclass, Jinja2MacroFileObjectHandler)):
    __schema__ = "http://numengo.org/draft-05/ngoschema/object-handlers#/definitions/Jinja2MacroTemplatedPathFileObjectHandler"

    def serialize_data(self, data):
        self.logger.info('SERIALIZE Jinja2MacroFileObjectHandler')
        try:
            tpath = TemplatedString(self.templatedPath)(**self._context)
        except Exception as er:
            self.logger.error('SERIALIZE Jinja2MacroTemplatedPathFileObjectHandler: %s', er)
        fpath = self.outputDir.joinpath(tpath)
        self.document = self.document or Document()
        self.document.filepath = fpath
        if not fpath.parent.exists():
            os.makedirs(str(fpath.parent))
        stream = Jinja2MacroFileObjectHandler.serialize_data(self, data)
        if fpath.suffix in ['.h', '.c', '.cpp']:
            tf = tempfile.NamedTemporaryFile(mode='w+b', suffix=fpath.suffix, dir=fpath.parent, delete=False)
            tf.write(stream.encode('utf-8'))
            tf.close()
            stream = subprocess.check_output(
                'clang-format %s' % tf.name, cwd=str(self.outputDir), shell=True)
            stream = stream.decode('utf-8')
            os.remove(tf.name)
        return stream

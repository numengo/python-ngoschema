# *- coding: utf-8 -*-
"""
Jinja2 serializer and custom filters

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import io
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

from . import utils
from .decorators import SCH_PATH_DIR_EXISTS
from .decorators import assert_arg
from .serializers import Serializer
from .serializers import serializer_registry
from .query import Query

templates_module_loader = utils.GenericModuleFileLoader('templates')

def load_module_templates(module_name):
    templates_module_loader.register(module_name)

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
        self._templated_str = templated_str
        self._template = default_jinja2_env().from_string(templated_str)
        self._has_dot = regex_has_dot.search(templated_str) is not None

    def __call__(self, **obj):
        # ctx = context.as_dict() if hasattr(context,'as_dict') else context
        if self._has_dot:
            return self._template.render(**obj)
        return self._template.render(**obj)


@serializer_registry.register()
class Jinja2Serializer(Serializer):
    logger = logging.getLogger(__name__)

    def __init__(self, template, environment=None):
        """
        Serializer based on a jinja template. Template is loaded from
        environment. If no environment is provided, use the default one
        `default_jinja2_env` 
        """
        self.jinja = environment or default_jinja2_env()
        self.jinja.globals.update(_jinja2_globals)
        self.template = template

    def dump(self,
             objs,
             path,
             overwrite=False,
             encoding="utf-8",
             logger=None,
             **opts):
        __doc__ = Serializer.dump.__doc__
        logger = logger or self.logger
        logger.info("DUMP template '%s' file %s", self.template, path)
        logger.debug("data:\n%r ", objs)

        if path.exists() and not overwrite:
            raise IOError("file '%s' already exists" % str(path))
        with io.open(str(path), 'w', encoding=encoding) as outfile:
            stream = self.dumps(objs, encoding=encoding, **opts)
            stream = six.text_type(stream)
            outfile.write(stream)

    def dumps(self, objs, **opts):
        data = objs.for_json() if hasattr(objs, "for_json") else objs
        data = utils.process_collection(data, **opts)
        return self.jinja.get_template(self.template).render(data)

    @assert_arg(2, SCH_PATH_DIR_EXISTS)
    def dump_macro(self,
                   macro_name,
                   output_dir,
                   templated_path,
                   overwrite=True,
                   encoding="utf-8",
                   protected_regions=None,
                   macro_args=[],
                   context=None,
                   **kwargs):
        """
        Serializes a jinja2 macro into a file by given by a possibly templated filepath.
        Missing directories are created.
        If output already exists with exact same content, file is not overwritten.

        :param macro_name: macro name in the template file
        :param output_dir: existing output directory
        :param templated_path: templated relative path of output
        :param protected_regions: an optional dictionary of protected regions (key: region canonical name, value: string)
        :param macro_args: macro list of arguments
        :param context: context used by jinja to render template
        """

        relpath = TemplatedString(templated_path)(**context)
        path = output_dir.joinpath(relpath)
        context = context or kwargs

        if path.exists() and not overwrite:
            raise IOError("file '%s' already exists" % str(path))

        stream = self.dumps_macro(
                macro_name,
                protected_regions=protected_regions,
                macro_args=macro_args,
                context=context)
        stream = six.text_type(stream)

        if not path.parent.exists():
            os.makedirs(str(path.parent))

        if path.suffix in ['.h', '.c', '.cpp']:
            tf = tempfile.NamedTemporaryFile(mode='w+b', suffix=path.suffix, dir=path.parent, delete=True)
            tf.write(stream.encode('utf-8'))
            stream = subprocess.check_output(
                'clang-format %s' % tf.name, cwd=str(output_dir), shell=True)
            tf.close()
            stream = stream.decode('utf-8')

        if path.exists():
            with io.open(str(path), 'r', encoding=encoding) as f:
                if stream == f.read():
                    self.logger.info("File '%s' already exists with same content. Not overwriting.", path)
                    return

        with io.open(str(path), 'w', encoding=encoding) as outfile:
            self.logger.info("DUMP macro %s of template '%s' file %s", macro_name, self.template, path)
            self.logger.debug("data:\n%r ", utils.any_pprint(context))
            outfile.write(stream)

    def dumps_macro(self, 
                    macro_name,
                    protected_regions=None,
                    macro_args=[],
                    context=None,
                    **kwargs):
        """
        Serializes a jinja2 macro

        :param macro_name: macro name in the template file
        :param protected_regions: an optional dictionary of protected regions (key: region canonical name, value: string)
        :param macro_args: macro list of arguments
        :param context: context used by jinja to render template
        """
        context = context or kwargs
        #args = ['arg%i'%i for i in range(len(macro_args))]
        #args = ['arg%i'%i for i in range(len(macro_args))]
        #ctx = { "arg%i"%i: o for i, o in enumerate(macro_args)}
        if 'protected_regions' not in macro_args:
            macro_args.append('protected_regions')

        self.jinja.globals['protected_regions'] = protected_regions or {}

        #context['protected_regions'] = protected_regions or {}
        args = [k for k in macro_args if k in context]
        #args += ['%s=%s' % (k, k) for k in context.keys() if k not in macro_args]
        #context['Query'] = Query
        to_render = "{%% from '%s' import %s %%}{{%s(%s)}}" % (
            self.template, macro_name, macro_name, ', '.join(args))
        try:
            template = self.jinja.from_string(to_render)
            return template.render(**context)
        except Exception as er:
            self.logger.info(er)
            raise er


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
    _extra_opts = {
        "trim_blocks": True,
        "lstrip_blocks": True,
        "keep_trailing_newline": True,
    }

    def __init__(self, **opts):
        loader = jinja2.PrefixLoader({
            mname: jinja2.PackageLoader(mname, path.name)
            for mname, paths in templates_module_loader.registry.items()
            for path in paths
        })

        jinja2.Environment.__init__(self, loader=loader, **opts, **self._extra_opts)
        self.globals.update(_jinja2_globals)

        # add filters
        for k, v in filters_registry.registry.items():
            self.filters[k] = v

# *- coding: utf-8 -*-
"""
Misc utilities

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import copy
import importlib
import inspect
import logging
import pathlib
import re
import subprocess
import sys
from builtins import object
from builtins import str

import inflection
import six
from ngofile.pathlist import PathList
from past.builtins import basestring

from ._qualname import qualname
from .decorators import take_arrays
from .exceptions import InvalidValue


class GenericRegistry(object):
    def __init__(self):
        self.registry = {}

    def register(self, name=None):
        def f(functor):
            self.registry[name
                          if name is not None else functor.__name__] = functor
            return functor

        return f

    def __call__(self, name):
        return self.registry.get(name)


class GenericModuleFileLoader(object):
    def __init__(self, subfolder_name):
        self.registry = {}
        self.subfolderName = subfolder_name

    def register(self, module, subfolder_name=None):
        m = importlib.import_module(module)
        subfolder_name = subfolder_name or self.subfolderName
        subfolder = pathlib.Path(
            m.__file__).with_name(subfolder_name).resolve()
        if subfolder.exists():
            if module not in self.registry:
                self.registry[module] = []
            self.registry[module].append(subfolder)
        return subfolder

    def preload(self,
                includes=["*"],
                excludes=[],
                recursive=False,
                serializers=[]):
        from .document import get_document_registry
        all_paths = list(sum(self.registry.values(), []))
        for d in all_paths:
            get_document_registry().\
                register_from_directory(d,
                                        includes=includes,
                                        excludes=excludes,
                                        recursive=recursive,
                                        serializers=serializers)

    def find(self, name):
        """
        find first name/pattern in loader's pathlist

        :param name: path or pattern
        :rtype: path
        """
        name = name.replace('\\', '/')
        if '/' in name:
            module, path = name.split('/', 1)
            if module in self.registry:
                return PathList(*self.registry[module]).pick_first(path)
        all_paths = list(sum(self.registry.values(), []))
        return PathList(*all_paths).pick_first(name)


def gcs(*classes):
    """
    Return the greatest common superclass of input classes
    """
    mros = [x.mro() for x in classes]
    for x in mros[0]:
        if all([x in mro for mro in mros]):
            return x


def is_basestring(value):
    """
    Test if value is a basestring
    """
    return isinstance(value, basestring) and not isinstance(value, str)


def is_string(value):
    """
    Test if value is a string
    """
    return isinstance(value, (str, basestring))


def is_pattern(value):
    """
    Test if value is a pattern, ie contains {{ }} formatted content 
    """
    return is_string(value) and ("{{" in value or "{%" in value)


def is_expr(value):
    """
    Test if value is an expression and starts with `
    """
    return is_string(value) and value.strip().startswith("`")


def fullname(obj):
    if is_module(obj):
        return str(obj).split("'")[1]
    qn = getattr(obj, "__qualname__", None) or qualname(obj)
    mn = obj.__module__
    if mn is None or mn == str.__class__.__module__:  # avoid builtin
        return qn
    return mn + "." + qn


def import_from_string(value):
    """
    Imports a symbol from a string
    """
    poss = [m.start() for m in re.finditer(r"\.", "%s." % value)]
    # going backwards
    for pos in reversed(poss):
        try:
            m = value[0:pos]
            ret = importlib.import_module(m)
            for a in value[pos + 1:].split("."):
                if not a:
                    continue
                ret = getattr(ret, a, None)
                if not ret:
                    raise InvalidValue(
                        "%s is not an importable object" % value)
            return ret
        except Exception as er:
            continue
    raise InvalidValue("%s is not an importable object" % value)


def is_module(value):
    """
    Test if value is a module
    """
    return inspect.ismodule(value)


def is_class(value):
    """
    Test if value is a class
    """
    return inspect.isclass(value)


def is_instance(value):
    """
    Test if value is an instance of a class
    """
    if getattr(value, "__class__"):
        return isinstance(value,
                          value.__class__) and not inspect.isclass(value)
    return False


def is_callable(value):
    """
    Test if value is a class
    """
    return is_instance(value) and hasattr(value, "__call__")


def is_static_method(value):
    """
    Test if value is a static method
    """
    return type(value) is staticmethod


def is_class_method(value):
    """
    Test if value is a class method
    """
    return type(value) is classmethod


def is_method(value,
              with_callable=True,
              with_static=True,
              with_class=True,
              with_method_descriptor=True):
    """
    Test if value is a method
    """
    if with_callable and is_callable(value):
        return True
    if with_static and is_static_method(value):
        return True
    if with_class and is_class_method(value):
        return True
    if with_method_descriptor and inspect.ismethoddescriptor(value):
        return True
    return inspect.ismethod(value)


def is_function(value, with_callable=True):
    """
    Test if value is a function
    """
    if with_callable and is_callable(value):
        return True
    return inspect.isfunction(value)


def is_imported(value):
    """
    Test if a symbol is importable/imported
    """
    return is_class(value) or is_method(value) or is_module(
        value) or is_function(value)


def is_importable(value):
    """
    Test if value is imported symbol or importable string
    """
    if is_string(value):
        try:
            value = import_from_string(value)
            return True
        except Exception as er:
            return False
    return is_imported(value)


def is_mapping(value):
    """
    Test if value is a mapping (dict, ordered dict, ...)
    """
    if isinstance(value, collections.Mapping):
        return True
    return False


def is_sequence(value):
    """
    Test if value is a sequence (list, tuple, deque)
    """
    if isinstance(value,
                  collections.Sequence) and not isinstance(value, basestring):
        return True
    if isinstance(value, collections.deque):
        return True
    return False


def is_collection(value):
    """
    Test if value is a list, set, tuple or dict
    """
    if is_mapping(value):
        return True
    if is_sequence(value):
        return True
    if isinstance(value, collections.Set):
        return True
    return False


def to_list(x, default=None):
    if x is None:
        return default
    if not is_sequence(x):
        return [x]
    elif isinstance(x, list):
        return x
    else:
        return list(x)


def to_set(x):
    if x is None:
        return set()
    if not isinstance(x, set):
        return set(to_list(x))
    else:
        return x


def apply_through_collection(coll, func, recursive=True):
    """
    Generic method to go through a complex collection
    and apply a transformation function on elements
    """
    #if is_mapping(coll):
    if isinstance(coll, dict):
        for k, v in coll.items():
            func(coll, k)
            # if recursive and (is_sequence(v) or is_mapping(v)):
            if recursive and isinstance(v, (list, dict)):
                apply_through_collection(coll[k], func, True)
    #elif is_sequence(coll):
    elif isinstance(coll, list):
        for i, v in enumerate(coll):
            func(coll, i)
            #if recursive and (is_sequence(v) or is_mapping(v)):
            if recursive and isinstance(v, (list, dict)):
                apply_through_collection(coll[i], func, True)


def only_keys(icontainer, keys, recursive=False):
    """
    Keep only specific keys in a container

    :param icontainer: input container
    :param keys: keys to keep
    :type keys: list
    :param recursive: process container recursively
    """
    # can't use apply_through_collection because we would delete while iterating
    ocontainer = copy.deepcopy(icontainer)

    def delete_fields_not_of(container, fields, recursive):
        if is_mapping(container):
            keys = set(container.keys())
            to_del = fields.intersection(keys)
            left = keys.difference(fields)
            for k in to_del:
                del container[k]
            if recursive:
                for k in left:
                    delete_fields_not_of(container[k], fields, recursive)
        elif is_sequence(container):
            for i, v in enumerate(container):
                delete_fields_not_of(container[i], fields, recursive)
        return container

    ocontainer = delete_fields_not_of(ocontainer, set(keys), recursive)
    return ocontainer


def but_keys(icontainer, keys, recursive=False):
    """
    Remove specific keys in a container

    :param icontainer: input container
    :param keys: keys to remove
    :type keys: list
    :param recursive: process container recursively
    """
    # can't use apply_through_collection because we would delete while iterating
    ocontainer = copy.deepcopy(icontainer)

    def delete_fields(container, fields, recursive):
        if is_mapping(container):
            keys = set(container.keys())
            to_del = fields.intersection(keys)
            left = keys.difference(fields)
            for k in to_del:
                del container[k]
            if recursive:
                for k in left:
                    delete_fields(container[k], fields, recursive)
        elif is_sequence(container):
            for i, v in enumerate(container):
                delete_fields(container[i], fields, recursive)
        return container

    ocontainer = delete_fields(ocontainer, set(keys), recursive)
    return ocontainer


def process_collection(data,
                       only=(),
                       but=(),
                       many=False,
                       replace_refs=False,
                       object_class=None,
                       object_from_schema=None,
                       **opts):
    """
    process a collection keeping some/only fields.
    If a json-schema is provided, an object is constructed according
    to the schema.
    If a class is provided, an object is constructed from the
    data provided.

    :param only: only keys to keep
    :param but: keys to exclude
    :param many: process collection as a list/sequence. if collection is
    a dictionary and many=True, values are processed
    """
    logger = opts.get('logger') or logging.getLogger(__name__)

    if many:
        datas = list(data) if is_sequence(data) else data.values()
        return [
            process_collection(
                d, only, but, object_class=object_class, **opts) for d in datas
        ]

    if replace_refs:
        from .document import resolve_ref

        # first replace relative canonical names before expanding $ref s
        cn = data.get('canonicalName')
        if cn:
            def _replace_relative_refs(coll, key, cname):
                value = coll[key]
                try:
                    if value[0] == '#' and '/' not in value:
                        if cname:
                            coll[key] = value.replace('#', '%s.' % cname , 1)
                        else:
                            return value[1:]
                except Exception:
                    pass
            
            apply_through_collection(data, 
                                     lambda c, k: _replace_relative_refs(c, k, cn), 
                                     recursive=True)

        def _replace_refs(coll, key):
            if isinstance(coll[key], dict) and '$ref' in coll[key]:
                ref = coll[key]['$ref']
                try:
                    #coll[key] = copy.deepcopy(resolve_ref(ref))
                    coll[key] = resolve_ref(ref)
                    # replace internal canonical name references
                    cn = coll[key].get('canonicalName')
                    if cn:
                        apply_through_collection(coll[key], 
                                     lambda c, k: _replace_relative_refs(c, k, cn), 
                                     recursive=True)
                except Exception as er:
                    logger.warning(
                        'unable to resolve reference %s', ref, exc_info=True)

        apply_through_collection(data, _replace_refs, recursive=True)

    if only:
        rec = opts.get("fields_recursive", False)
        data = only_keys(data, only, rec)

    if but:
        rec = opts.get("fields_recursive", False)
        data = but_keys(data, but, rec)

    if object_class is not None:
        return object_class(**data)

    if object_from_schema:
        from .classbuilder import ClassBuilder
        from .resolver import get_resolver
        resolver = get_resolver()
        schema = object_from_schema
        nm = schema['title'] if 'title' in schema else schema.get(
            'id', 'Nameless')
        nm = inflection.parameterize(six.text_type(nm), '_')
        object_class = ClassBuilder(resolver).construct(nm, schema)
        return object_class(**data)

    return data


def logging_call(popenargs,
                 logger=None,
                 stdout_log_level=logging.DEBUG,
                 stderr_log_level=logging.ERROR,
                 **kwargs):
    """
    Variant of subprocess.call that accepts a logger instead of stdout/stderr,
    and logs stdout messages via logger.debug and stderr messages via
    logger.error.

    inspired from code https://gist.github.com/1402841/231d4ae00325892ad30f6d9587446bc55c56dcb6
    """
    _logger = logger or logging.getLogger(__name__)
    out, err = subprocess.Popen(
        popenargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        **kwargs).communicate()
    #print out, err
    enc = sys.stdout.encoding or "cp850"
    if out:

        _logger.log(stdout_log_level, six.text_type(out, enc, errors='ignore'))
    if err:
        _logger.log(stderr_log_level, six.text_type(err, enc, errors='ignore'))


def grouper( page_size, iterable ):
    """group iterable by pages of page_size and generate an iterator on pages"""
    page= []
    for item in iterable:
        page.append( item )
        if len(page) == page_size:
            yield page
            page= []
    yield page
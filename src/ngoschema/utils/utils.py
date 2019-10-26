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
import itertools
import logging
import pathlib
import re
import subprocess
import sys
from builtins import str
from contextlib import contextmanager
import threading
import  weakref
from urllib.parse import urlsplit

import six
from ngofile.pathlist import PathList
from past.types import basestring

from ngoschema.utils._qualname import qualname
from ngoschema.exceptions import InvalidValue
from collections import OrderedDict as odict
from collections import Mapping, MutableMapping


class _KeyModifierMapping(MutableMapping):

    @classmethod
    def key_modifier(cls, value):
        """method to override"""
        return value

    @classmethod
    def _k(cls, value):
        return value.lower() if is_string(value) else value

    def __init__(self, *args, **kwargs):
        self._dict = {}
        temp_dict = dict(*args, **kwargs)
        for key, value in temp_dict.items():
            self._dict[self.__class__._k(key)] = value

    def __getitem__(self, key):
        return self._dict[self.__class__._k(key)]

    def __setitem__(self, key, value):
        self._dict[self.__class__._k(key)] = value

    def __delitem__(self, key):
        del self._dict[self.__class__._k(key)]

    def __contains__(self, key):
        return self.__class__._k(key) in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

class CaseInsensitiveDict(_KeyModifierMapping):

    @classmethod
    def key_modifier(cls, key):
        return key.lower()

class UriDict(_KeyModifierMapping):

    @classmethod
    def key_modifier(cls, key):
        return urlsplit(key).geturl()


class Registry(Mapping):

    def __init__(self):
        self._registry = collections.OrderedDict()

    def __repr__(self):
        return repr(self._registry)

    def __getitem__(self, key):
        return self._registry[key]

    def __iter__(self):
        return six.iterkeys(self._registry)

    def __len__(self):
        return len(self._registry)

    def register(self, key, value):
        self._registry[key] = value

    def unregister(self, key):
        del self._registry[key]

class WeakRegistry(Registry):

    def __init__(self):
        self._registry = weakref.WeakValueDictionary()

    def __getitem__(self, key):
        # callv weak reference
        return self._registry[key]()


class GenericClassRegistry(Registry):

    def register(self, name=None):
        def f(functor):
            self._registry[name if name is not None
                           else functor.__name__] = functor
            return functor

        return f


class GenericModuleFileLoader(Registry):

    def __init__(self, subfolder_name):
        Registry.__init__(self)
        self.subfolderName = subfolder_name

    def register(self, module, subfolder_name=None):
        m = importlib.import_module(module)
        subfolder_name = subfolder_name or self.subfolderName
        subfolder = pathlib.Path(
            m.__file__).parent.joinpath(subfolder_name).resolve()
        if subfolder.exists():
            if module not in self._registry:
                self._registry[module] = []
            self._registry[module].append(subfolder)
        return subfolder

    def preload(self,
                includes=["*"],
                excludes=[],
                recursive=False,
                serializers=[]):
        from .document import get_document_registry
        all_paths = list(sum(self._registry.values(), []))
        for d in all_paths:
            get_document_registry().\
                register_from_directory(d,
                                        includes=includes,
                                        excludes=excludes,
                                        recursive=recursive,
                                        serializers=serializers)

    def find_one(self, name):
        """
        find first name/pattern in loader's pathlist

        :param name: path or pattern
        :rtype: path
        """
        name = name.replace('\\', '/')
        if '/' in name:
            module, path = name.split('/', 1)
            if module in self._registry:
                return PathList(*self._registry[module]).pick_first(path)
        all_paths = list(sum(self._registry.values(), []))
        return PathList(*all_paths).pick_first(name)


def gcs(*classes):
    """
    Return the greatest common superclass of input classes
    """
    mros = [x.mro() for x in classes]
    for x in mros[0]:
        if all([x in mro for mro in mros]):
            return x

# http://code.activestate.com/recipes/577748-calculate-the-mro-of-a-class/
def mro(*bases):
    """Calculate the Method Resolution Order of bases using the C3 algorithm.

    Suppose you intended creating a class K with the given base classes. This
    function returns the MRO which K would have, *excluding* K itself (since
    it doesn't yet exist), as if you had actually created the class.

    Another way of looking at this, if you pass a single class K, this will
    return the linearization of K (the MRO of K, *including* itself).
    """
    seqs = [list(C.__mro__) for C in bases] + [list(bases)]
    res = []
    while True:
      non_empty = list(filter(None, seqs))
      if not non_empty:
          # Nothing left to process, we're done.
          return tuple(res)
      for seq in non_empty:  # Find merge candidates among seq heads.
          candidate = seq[0]
          not_head = [s for s in non_empty if candidate in s[1:]]
          if not_head:
              # Reject the candidate.
              candidate = None
          else:
              break
      if not candidate:
          raise TypeError("inconsistent hierarchy, no C3 MRO is possible")
      res.append(candidate)
      for seq in non_empty:
          # Remove candidate.
          if seq[0] == candidate:
              del seq[0]

import functools
from jsonschema._types import is_bool
from jsonschema._types import is_integer
from jsonschema._types import is_null
from jsonschema._types import is_number
is_bool = functools.partial(is_bool, None)
is_integer = functools.partial(is_integer, None)
is_null = functools.partial(is_null, None)
is_number = functools.partial(is_number, None)

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
                    raise ValueError(
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


def apply_through_collection(coll, func, recursive=True, level=0, **func_kwargs):
    """
    Generic method to go through a complex collection
    and apply a transformation function 'func' on each element
    func can modify the collection on the fly

    func needs 3 arguments:
        * the collection
        * the key (string for dict or int for sequences)
        * the level of depth in collection
        * it is also given the additional func_kwargs keyword arguments
    """
    if not coll:
        return
    is_map = is_mapping(coll)
    for i, k in enumerate(list(coll.keys()) if is_map else coll):
        func(coll, k if is_map else i, level=level, **func_kwargs)
        if recursive:
            v = coll.get(k) if is_map else (
                coll[i] if i < len(coll) else
                None)
            if is_collection(v):
                apply_through_collection(v, func, recursive, level=level+1, **func_kwargs)


def filter_collection(data,
                      only=(),
                      but=(),
                      recursive=False):
    """
    process a collection keeping some/only fields.

    :param only: only keys to keep
    :param but: keys to exclude
    """

    def _filter_keys(container, keys, keep=True):
        if is_mapping(container):
            for k in keys.intersection(container.keys()):
                if not keep:
                    container.pop(k)
                elif recursive:
                    _filter_keys(container[k], keys, keep, recursive)
        elif is_sequence(container):
            for v in container:
                _filter_keys(v, keys, keep, recursive)
        return container

    if only or but:
        data = copy.deepcopy(data)
        if only:
            data = _filter_keys(data, set(only), keep=True)
        if but:
            data = _filter_keys(data, set(but), keep=False)
    return data


def nested_dict_iter(nested, separator='.'):
    """
    generator going through a nested dictionary and returning a canonical name / value
    """
    for key, value in nested.items():
        if isinstance(value, collections.Mapping):
            for inner_key, inner_value in nested_dict_iter(value):
                yield f'{key}{separator}{inner_key}', inner_value
        else:
            yield key, value

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


@contextmanager
def casted_as(instance, cls):
    """context manager to cast an instance as a parent class"""
    instance_cls = instance.__class__
    if cls not in instance_cls.mro():
        raise AttributeError("'%s' is not a parent of '%s'" % (cls, instance))
    instance.__class__ = cls
    yield instance
    instance.__class__ = instance_cls

class Bracket:
    _context = None
    _pos = (None, None)
    _br = None

    def __repr__(self):
        if self._context:
            return '<Bracket %s %s >' % (self._pos, self._context[self._pos[0]: self._pos[1]+1])
        else:
            return '<Bracket (, ) >'

    def __init__(self, context, pos, bracket='('):
        self._context = context
        self._br, self._cbr = self.get_brackets(bracket)
        assert len(pos)==2 and pos[0] < pos[1] and context[pos[0]] == self._br and context[pos[1]] == self._cbr
        self._pos = pos

    @staticmethod
    def get_brackets(bracket):
        brs = ['()', '[]', '{}', '<>']
        for br in brs:
            if bracket in br:
                return br
        raise InvalidValue('unknown bracket type %s (only %s)' % (bracket, ''.join(brs)))

    def is_in(self, other):
        return self._pos[0] < other._pos[0] and other._pos[1] > self._pos[1]

    def content(self):
        return self._context[self._pos[0]+1 : self._pos[1]]

    def find_closing_bracket(context, bracket='('):
        br, cbr = Bracket.get_brackets(bracket)
        o_brs = []
        for i, s in enumerate(context):
            if s == br:
                o_brs.append(i)
            if s == cbr:
                obr_, cbr_ = o_brs.pop(), i
                if not o_brs:
                    return (obr_, cbr_), context[obr_+1:cbr_]

    @staticmethod
    def find_brackets(context, bracket='('):
        br, cbr = Bracket.get_brackets(bracket)
        res = []
        o_brs = []
        for i, s in enumerate(context):
            if s == br:
                o_brs.append(i)
            if s == cbr:
                pos = (o_brs.pop(), i)
                res.append(
                    Bracket(context=context,
                            pos=pos,
                            bracket=bracket))
        return res

    @staticmethod
    def find_nested_brackets(context, bracket='('):
        all = Bracket.find_closed_brackets(context, bracket)

        def order_brackets(pos_brs):
            reg = odict({pos_brs.pop(): odict()})
            def do_order(pos, registry):
                for k in set(registry):
                    if pos.is_in(k):
                        do_order(pos, registry[k])
                        break
                else:
                    registry[pos] = odict()
            for pos in reversed(pos_brs):
                do_order(pos, reg)
            def do_reverse(registry):
                res = odict(reversed(list(registry.items())))
                for r in res.values():
                    do_reverse(r)
                return res
            return do_reverse(reg)

        return order_brackets(all)

    @staticmethod
    def find_function_content(context, f_name, pos=0):
        f_name = f_name.rstrip('(').strip()
        f_call = '%s(' % f_name
        p = context.find(f_call, context)
        brs = Bracket.find_brackets(context)

def threadsafe_counter(init_value=1):
    """Return a threadsafe counter function.
    credit: sqlachemy """
    lock = threading.Lock()
    counter = itertools.count(init_value)

    # avoid the 2to3 "next" transformation...
    def _next():
        lock.acquire()
        try:
            return next(counter)
        finally:
            lock.release()

    return _next

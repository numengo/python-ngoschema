# *- coding: utf-8 -*-
"""
Misc utilities

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import collections
from pyrsistent import pmap
import copy
import importlib
import inspect
import itertools
import logging
import pathlib
import datetime
import re
import subprocess
import sys
from builtins import str
import contextlib
import threading
import weakref
from urllib.parse import urlsplit
import functools

import six
from ngofile.pathlist import PathList
from past.types import basestring
from jsonschema._types import is_integer

from ngoschema.utils._qualname import qualname
from ngoschema.exceptions import InvalidValue
from collections import OrderedDict as odict
from collections import Mapping, MutableMapping


class ReadOnlyChainMap(Mapping):

    def __init__(self, *maps):
        self._maps = [m for m in maps]

    @property
    def maps(self):
        return self._maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __contains__(self, key):
        return any(key in m or {} for m in self._maps)

    def reversed_keys(self):
        viewed = set()
        for m in reversed(self._maps):
            if isinstance(m, ReadOnlyChainMap):
                for k in m.reversed_keys():
                    if k not in viewed:
                        viewed.update([k])
                        yield k
            else:
                for k in m or {}:
                    if k not in viewed:
                        viewed.update([k])
                        yield k

    def __iter__(self):
        viewed = set()
        for m in self._maps:
            for k in m or {}:
                if k not in viewed:
                    viewed.update([k])
                    yield k

    def __len__(self):
        return len(set().union(*self._maps))

    def new_child(self, *maps, **kwargs):
        return ReadOnlyChainMap(kwargs, *maps, *self._maps)

    def __repr__(self):
        from .str_utils import shorten
        return '<ReadOnlyChainMap %s>' % shorten(self.merged)

    def __str__(self):
        return str(self.merged)

    _maps_flattened = None
    @property
    def maps_flattened(self):
        if self._maps_flattened is None:
            mf = []
            for m in self._maps:
                if isinstance(m, ReadOnlyChainMap):
                    mf.extend(m.maps_flattened)
                else:
                    mf.append(m)
            self._maps_flattened = mf
        return self._maps_flattened

    @property
    def merged(self):
        ret = dict()
        for m in self.maps:
            for k in set(m.keys()).difference(ret.keys()):
                ret[k] = m[k]
        return ret


class Context(ReadOnlyChainMap):

    def __init__(self, *parents, **local):
        self._local = local
        self._parents = parents
        ReadOnlyChainMap.__init__(self, local, *parents)

    def __enter__(self):
        return copy.deepcopy(self)

    def __exit__(self, type, value, traceback):
        pass

    def __repr__(self):
        return repr(list(self._maps))

    def create_child(self, *parents, **local):
        'Make a child context, inheriting enable_nonlocal unless specified'
        if not parents and not local:
            return self
        if local:
            parents = (local, ) + parents
        return Context(*parents, *self._maps)

    def prepend(self, mapping):
        self._maps.insert(0, mapping)

    def append(self, mapping):
        self._maps.append(mapping)

    def find_instance(self, cls, default=None, exclude=None, reverse=False):
        gen = (m for m in self.maps if isinstance(m, cls) and m is not exclude)
        if reverse:
            gen = reversed(gen)
        return next(gen, default)

    def __hash__(self):
        return hash(repr(sorted(self.merged.items())))


class _KeyModifierMapping(MutableMapping):

    @classmethod
    def key_modifier(cls, value):
        """method to override"""
        return value

    def __init__(self, *args, **kwargs):
        self._dict = {}
        temp_dict = dict(*args, **kwargs)
        for key, value in temp_dict.items():
            self._dict[self.__class__.key_modifier(key)] = value

    def __getitem__(self, key):
        return self._dict[self.__class__.key_modifier(key)]

    def __setitem__(self, key, value):
        self._dict[self.__class__.key_modifier(key)] = value

    def __delitem__(self, key):
        del self._dict[self.__class__.key_modifier(key)]

    def __contains__(self, key):
        return self.__class__.key_modifier(key) in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return repr(self._dict)


class CaseInsensitiveDict(_KeyModifierMapping):

    @classmethod
    def key_modifier(cls, key):
        return key.lower()


class UriDict(_KeyModifierMapping):

    @classmethod
    def key_modifier(cls, key):
        return str(urlsplit(key).geturl()).lower()


class Registry(Mapping):
    _parent_registries = []

    def __init__(self, *parent_registries):
        self._parent_registries = parent_registries
        self._registry = collections.OrderedDict()

    def __repr__(self):
        return repr(self._registry)

    def __getitem__(self, key):
        return self._registry[key]

    def __iter__(self):
        return six.iterkeys(self._registry)

    def __len__(self):
        return len(self._registry)

    def __contains__(self, key):
        return key in self._registry

    def register(self, key, value):
        self._registry[key] = value
        for pr in self._parent_registries:
            Registry.register(pr, key, value)

    def unregister(self, key):
        del self._registry[key]
        for pr in self._parent_registries:
            Registry.unregister(pr, key)


class WeakRegistry(Registry):

    def __init__(self, *parent_registries):
        Registry.__init__(self, *parent_registries)
        self._registry = weakref.WeakValueDictionary()

    def __getitem__(self, key):
        # callv weak reference
        return self._registry[key]()


class GenericClassRegistry(Registry):
    _registry = {}

    def register(self, name=None):
        def f(functor):
            n = name if name is not None else functor.__name__
            #self._registry[n] = functor
            #for pr in self._parent_registries:
            #    pr._registry[n]
            Registry.register(self, n, functor)
            #self._registry[name if name is not None
            #               else functor.__name__] = functor
            return functor

        return f

    def get(self, id, default=None):
        return self._registry.get(id)

    def contains(self, id):
        return id in self._registry


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

is_integer = functools.partial(is_integer, None)


def is_string(value):
    """
    Test if value is a string
    """
    return isinstance(value, (str, basestring))


def fullname(obj):
    if inspect.ismodule(obj):
        return str(obj).split("'")[1]
    qn = getattr(obj, "__qualname__", None) or qualname(obj)
    mn = obj.__module__
    if mn is None or mn == str.__class__.__module__:  # avoid builtin
        return qn
    return mn + "." + qn


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
    if isinstance(value, weakref.WeakSet):
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


def to_none_single_list(x):
    xl = to_list(x)
    if xl is not None:
        if len(xl) == 1:
            return xl[0]
        if len(xl) > 1:
            return xl


def reduce_coll(coll):
    """function to reduce a collection
    delete empty elements
    make unique item lists as single element
    """
    def do_reduce(coll, key, level):
        v = coll[key]
        if is_mapping(v):
            if not any(v.values()):
                coll[key] = to_none_single_list(v.keys())
        if is_sequence(v):
            coll[key] = to_none_single_list(v)
        if not coll[key]:
            del coll[key]

    return apply_through_collection(coll, do_reduce)


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
            if is_mapping(v) or isinstance(v, list):
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


@contextlib.contextmanager
def casted_as(instance, cls):
    """context manager to cast an instance as a parent class"""
    instance_cls = instance.__class__
    if cls not in instance_cls.__mro__:
        raise AttributeError("'%s' is not a parent of '%s'" % (cls, instance))
    instance.__class__ = cls
    yield instance
    instance.__class__ = instance_cls


def class_casted_as(cls, other):
    """return a class casted to another"""
    if other not in cls.__mro__:
        raise AttributeError("'%s' is not a parent of '%s'" % (other, cls))
    # get all attributes of cls not in other mro
    attrs = dict(ReadOnlyChainMap(*[b.__dict__ for b in cls.__mro__ if b not in other.__mro__]))
    # add public attributes of other mro
    attrs.update({k: v for k, v in ReadOnlyChainMap(*[b.__dict__ for b in other.__mro__]).items()
                  if not k.startswith('_')})
    return type(cls.__name__, (other, ), attrs)


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


def split_path(path):
    """ return a path as a list of attributes and key, index"""
    paths = []
    for part in path.split('.'):
        for key in part.split('['):
            key = key.strip('[]')
            paths.append(int(key) if is_integer(key) else key)
    return paths


def get_descendant(obj, key_list):
    """
    Get descendant in an object/dictionary by providing the path as a list of keys
    :param obj: object to iterate
    :param key_list: list of keys
    """
    if is_string(key_list):
        key_list = split_path(key_list)
    k0 = key_list[0]

    try:
        child = obj[k0]
    except Exception as er:
        child = None
    return get_descendant(child, key_list[1:]) \
        if child and len(key_list) > 1 else child


def topological_sort(data):
    """" sort a dependency tree """
    # http://rosettacode.org/wiki/Topological_sort#Python
    from functools import reduce
    if not data:
        return {}
    for k, v in data.items():
        v.discard(k) # Ignore self dependencies
    extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
    data.update({item: set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item,dep in data.items() if not dep)
        if not ordered:
            break
        yield ordered
        #yield ' '.join(sorted(ordered))
        data = {item: (dep - ordered) for item,dep in data.items()
                if item not in ordered}
    assert not data, "A cyclic dependency exists amongst %r" % data


@contextlib.contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = pathlib.Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

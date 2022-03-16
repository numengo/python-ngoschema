# *- coding: utf-8 -*-
""" decorators

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import inspect
import sys
import functools
import weakref
import six
import wrapt
from wrapt import decorator

from pprint import pformat
from pyrsistent import pmap
from jsonschema.exceptions import ValidationError

from .exceptions import InvalidValue

# about decorators and why using wrapt
# https://hynek.me/articles/decorators/


def take_arrays(narg1=0, narg2=-1, flatten=False):
    """
    Decorator for functions/methods to take a list input and retrieve a list as
    a result

    :param narg1: index of argument to use as criteria
    :param narg2: index of an optional second argument (can be a list of same
                  size, or a scalar)
    :param flatten: flatten results
    :rtype: returns a list if the input argument is a list
    """

    def to_decorate(wrapped):
        sig = inspect.getargspec(wrapped)

        @wrapt.decorator
        def wrapper(method, instance, args, kwargs):
            # case first argument is an array
            if type(args[narg1]) in (list, set, tuple):
                ret = []
                new_args = list(args)
                # only first argument is an array
                if (narg2 == -1 or not type(args[narg2]) in (list, set, tuple)
                        or len(args[narg2]) == 1):
                    for v in args[narg1]:
                        new_args[narg1] = v
                        ret.append(wrapped(*new_args, **kwargs))
                # both are list
                else:
                    # same size - call with zipped values
                    if len(args[narg1]) == len(args[narg2]):
                        for v1, v2 in zip(args[narg1], args[narg2]):
                            new_args[narg1] = v1
                            new_args[narg2] = v2
                            ret.append(wrapped(*new_args, **kwargs))
                    # different size
                    else:
                        raise InvalidValue(
                            "arguments %s and %s must be of same size" %
                            (narg1, narg2))
            else:
                # if the first one is not a string, ignore and call func
                return wrapped(*args, **kwargs)
            if flatten:
                return [item for sublist in ret for item in sublist]
            return ret

        decorated = wrapper(wrapped)

        doc = [wrapped.__doc__.strip()] if wrapped.__doc__ else []
        doc.append(
            "Argument '%s' can take an array, " % (sig.args[narg1]) +
            "and the function will perfom the operation on each element " +
            "and return the results as a list.")
        if narg2 != -1:
            doc.append(
                "Arguments '%s' and '%s'" %
                (sig.args[narg1], sig.args[narg2]) +
                " can take arrays of same size, and the function will perfom " +
                "the operation in parallel and return the results as a list.")
        if flatten:
            doc.append("The resulting list of lists if flattened.")

        wrapt.FunctionWrapper.__setattr__(decorated, "__doc__", "\n".join(doc))

        return decorated

    return to_decorate


logger = logging.getLogger(__name__)


def assert_arg(arg, typ, **schema):
    """
    Decorator to add a schema to validate a given argument against a json-schema.
    If the decorated function has a keyword argument `assert_args`, it is used as
    a flag to enable/disable argument validation/conversion.

    :param arg: argument to convert/validate, can be position (start 0) or name
    :type type: Type subclass
    :param schema: json-schema for the type
    """
    validator = typ(**schema)

    def to_decorate(wrapped):
        # find argument in signature
        arg_i = None
        arg_s = arg
        try:
            sig = inspect.getargspec(wrapped)
            if type(arg) is int:
                arg_i = arg
                arg_s = sig.args[arg]
            elif arg in sig.args:
                arg_i = sig.args.index(arg)
                arg_s = arg
        except Exception as er:
            logger.error(er)
            raise
            # if no inspection possible (if creating type metaprogramming)

        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwargs):

            # make assert optional with kwargs
            assert_args = kwargs.pop('assert_args', True)
            if not assert_args:
                return wrapped(*args, **kwargs)

            arg_i2 = arg_i if not instance and arg_i is not None else arg_i - 1
            args = list(args)
            try:
                if arg_s in kwargs:
                    kwargs[arg_s] = validator(kwargs[arg_s], validate=True)
                elif type(arg_i2) is int and arg_i2 < len(args):
                    args[arg_i2] = validator(args[arg_i2], check=True, validate=True)
                else:
                    # must be a default value, assume it s correct!
                    pass
                    #raise Exception("error with argument definition (%s,%i)"%(arg_s, arg_i2))
            except (ValidationError, InvalidValue) as er:
                if arg_s in kwargs:
                    raise ValidationError(
                        "%s=%r is not valid. %s" % (arg_s, kwargs[arg_s], er))
                elif type(arg_i) is int and arg_i2 < len(args):
                    raise ValidationError(
                        "%s=%r is not valid. %s" % (arg_s, args[arg_i2], er))
            return wrapped(*args, **kwargs)

        decorated = wrapper(wrapped)

        try:
            doc = (
                (wrapped.__doc__ or "").strip() + "\n\nArgument '%s' is " % arg +
                "automatically type converted and validated against %s."
                % pformat(validator))

            wrapt.FunctionWrapper.__setattr__(decorated, "__doc__", doc)
        except Exception as er:
            logger.error(er)
            raise

        return decorated

    return to_decorate


def _format_call_msg(funcname, args, kwargs):
    """
    Format a call message
    """
    return "%s(%s)" % (
        funcname,
        ", ".join(["%r" % a for a in args] +
                  ["%s=%r" % (a, v) for a, v in kwargs.items()]),
    )


@wrapt.decorator
def log_exceptions(method, instance, args, kwargs):
    """
    log calls to a function/method with its arguments and the exceptions
    that might be raised.

    SHOULDN T BE USED FOR __init__, use log_init instead
    """
    # special case happening for getters/setters
    if instance is None:
        instance = args[0]
    try:
        if hasattr(instance, "_logger"):
            instance._logger.debug(
                "CALL %s",
                _format_call_msg(
                    "%r.%s" % (instance, getattr(method, '__name__', 'unknown')),
                    args, kwargs))
        return method(*args, **kwargs)
    except Exception as er:
        etype, value, trace = sys.exc_info()
        if hasattr(instance, "_logger"):
            instance._logger.error(
                "CALL %s",
                _format_call_msg(
                    "%r.%s" % (instance, getattr(method, '__name__', 'unknown')),
                    args, kwargs) +
                "\n\tERROR %s: %s" % (etype.__name__, value), exc_info=True)
        try:
            six.reraise(etype, value, trace)
        finally:
            del trace  # to avoid circular refs


@wrapt.decorator
def log_init(init, instance, args, kwargs):
    """
    log init of instance and possible exceptions
    """
    instance._logger.info(
        "%s",
        _format_call_msg("INIT <%s>.__init__" % instance.__class__.__name__,
                         args, kwargs))
    try:
        return init(*args, **kwargs)
    except Exception as er:
        etype, value, trace = sys.exc_info()
        instance._logger.error(
            "CALL %s\n\tERROR: %s: %s",
            _format_call_msg(
                "INIT <%s>.__init__" % instance.__class__.__name__, args,
                kwargs), etype.__name__, value)
        try:
            six.reraise(etype, value, trace)
        finally:
            del trace  # to avoid circular refs


def assert_prop(*args2check):
    """
    Assert some properties/attributes are defined in instance

    :param args2check: list of property/attribute to check as defined
    """

    def to_decorate(wrapped):
        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwargs):
            for prop in args2check:
                if getattr(instance, prop, None) is None:
                    raise AttributeError("%s is not defined." % prop)
            return wrapped(*args, **kwargs)

        decorated = wrapper(wrapped)

        doc = (wrapped.__doc__ or "").strip()
        for prop in args2check:
            doc += "\nProperty %s is asserted to be defined before call." % prop
        wrapt.FunctionWrapper.__setattr__(decorated, "__doc__", doc)

        return decorated

    return to_decorate


def depend_on_prop(*prop_names):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        return wrapped(*args, **kwargs)
    return wrapper


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


class memoized_property(object):
    """A read-only @property that is only evaluated once."""

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result

    def _reset(self, obj):
        memoized_property.reset(obj, self.__name__)

    @classmethod
    def reset(cls, obj, name):
        obj.__dict__.pop(name, None)


def memoized_method(*lru_args, **lru_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            self_weak = weakref.ref(self)
            @functools.wraps(func)
            @functools.lru_cache(*lru_args, **lru_kwargs)
            def cached_method(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)
            # can t use setattr as it conflicts with __setattr__ of protocol base
            object.__setattr__(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)
        return wrapped_func
    return decorator

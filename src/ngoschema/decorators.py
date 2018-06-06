# *- coding: utf-8 -*-
""" decorators

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import logging
import sys
import six
import inspect
import wrapt
from builtins import object
from builtins import str
from pprint import pformat

from python_jsonschema_objects.validators import ValidationError

from .exceptions import InvalidValue
from .validators import convert_validate

_ = gettext.gettext

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
            if type(args[narg1]) in [list, set, tuple]:
                ret = []
                new_args = list(args)
                # only first argument is an array
                if (
                    narg2 == -1
                    or not type(args[narg2]) in [list, set, tuple]
                    or len(args[narg2]) == 1
                ):
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
                            _(
                                "arguments %s and %s must be of same size"
                                % (narg1, narg2)
                            )
                        )
            else:
                # if the first one is not a string, ignore and call func
                return wrapped(*args, **kwargs)
            if flatten:
                return [item for sublist in ret for item in sublist]
            return ret

        decorated = wrapper(wrapped)

        doc = [wrapped.__doc__.strip()] if wrapped.__doc__ else []
        doc.append(
            "Argument '%s' can take an array, " % (sig.args[narg1])
            + "and the function will perfom the operation on each element "
            + "and return the results as a list."
        )
        if narg2 != -1:
            doc.append(
                "Arguments '%s' and '%s'" % (sig.args[narg1], sig.args[narg2])
                + " can take arrays of same size, and the function will perfom "
                + "the operation in parallel and return the results as a list."
            )
        if flatten:
            doc.append("The resulting list of lists if flattened.")

        wrapt.FunctionWrapper.__setattr__(decorated, "__doc__", "\n".join(doc))

        return decorated

    return to_decorate


def assert_arg(arg, schema):
    """
    Decorator to add a schema to validate a given argument against a json-schema

    :param arg: argument to convert/validate, can be position (start 0) or name
    :type arg: [str, int]
    :param schema: json-schema for the type
    :type schema: dict
    """

    def to_decorate(wrapped):
        # find argument in signature
        sig = inspect.getargspec(wrapped)
        if type(arg) is int:
            arg_i = arg
            arg_s = sig.args[arg]
        elif arg in sig.args:
            arg_i = sig.args.index(arg)
            arg_s = arg
        else:
            arg_i = None
            arg_s = arg

        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwargs):
            new_args = list(args)
            if instance:
                new_args.insert(0, instance)

            try:
                if arg_s in kwargs:
                    kwargs[arg_s] = convert_validate(kwargs[arg_s], schema)
                elif type(arg_i) is int and arg_i < len(new_args):
                    new_args[arg_i] = convert_validate(new_args[arg_i], schema)
                else:
                    raise Exception("unknown error")
            except ValidationError as er:
                if arg_s in kwargs:
                    raise ValidationError(
                        _("%s=%r is not valid. %s") % (arg_s, kwargs[arg_s], er)
                    )
                elif type(arg_i) is int and arg_i < len(new_args):
                    raise ValidationError(
                        _("%s=%r is not valid. %s") % (arg_s, new_args[arg_i], er)
                    )
            if instance:
                new_args.pop(0)
            return wrapped(*new_args, **kwargs)

        decorated = wrapper(wrapped)

        doc = (
            (wrapped.__doc__ or "").strip()
            + "\nArgument '%s' is " % arg
            + "automatically type converted and validated against this schema %s."
            % pformat(schema)
        )

        wrapt.FunctionWrapper.__setattr__(decorated, "__doc__", doc)

        return decorated

    return to_decorate


def _format_call_msg(funcname, args, kwargs):
    """
    Format a call message
    """
    return "%s(%s)" % (
        funcname,
        ", ".join(
            ["%r" % a for a in args] + ["%s=%r" % (a, v) for a, v in kwargs.items()]
        ),
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
        if hasattr(instance, "logger"):
            instance.logger.debug(
                "CALL "
                + _format_call_msg("%r.%s" % (instance, method.__name__), args, kwargs)
            )
        return method(*args, **kwargs)
    except Exception as er:
        etype, value, trace = sys.exc_info()
        if hasattr(instance, "logger"):
            instance.logger.error(
                "CALL "
                + _format_call_msg("%r.%s" % (instance, method.__name__), args, kwargs)
                + "\n\tERROR %s: %s" % (etype.__name__, value)
            )
        try:
            six.reraise(etype, value, trace)
        finally:
            del trace  # to avoid circular refs


@wrapt.decorator
def log_init(init, instance, args, kwargs):
    """
    log init of instance and possible exceptions
    """
    instance.logger.info(
        _format_call_msg(
            "INIT <%s>.__init__" % instance.__class__.__name__, args, kwargs
        )
    )
    try:
        init(*args, **kwargs)
    except Exception as er:
        etype, value, trace = sys.exc_info()
        instance.logger.error(
            "CALL "
            + _format_call_msg(
                "INIT <%s>.__init__" % instance.__class__.__name__, args, kwargs
            )
            + "\n\tERROR %s: %s" % (etype.__name__, value)
        )
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
                    raise AttributeError(_("%s is not defined." % prop))
            return wrapped(*args, **kwargs)

        decorated = wrapper(wrapped)

        doc = (wrapped.__doc__ or "").strip()
        for prop in args2check:
            doc += "\nProperty %s is asserted to be defined before call." % prop
        wrapt.FunctionWrapper.__setattr__(decorated, "__doc__", doc)

        return decorated

    return to_decorate

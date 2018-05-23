# *- coding: utf-8 -*-
""" decorators

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import gettext
import sys
from builtins import object
from builtins import str
from pprint import pformat

import six

from .exceptions import InvalidValue

_ = gettext.gettext


def _format_call_msg(object, args=None, kwargs=None):
    """
    Format a call message
    """
    msg = "%s" % object
    if args:
        msg = _('%s\n\twith args:\n%s' % (msg, pformat(args)))
    if kwargs:
        msg = _('%s\n\twith kwargs:\n%s' % (msg, pformat(kwargs)))
    return msg


def log_exceptions(method):
    """
    Decoractor to log exceptions in instance logger
    """

    @functools.wraps(method)
    def exception_wrapper(instance, *args, **kwargs):
        try:
            instance.logger.debug(
                _format_call_msg('CALL %r.%s' % (instance, method.__name__),
                                 args, kwargs))
            return method(instance, *args, **kwargs)
        except Exception as er:
            etype, value, trace = sys.exc_info()
            instance.logger.error(
                _format_call_msg('CALL %r.%s ERROR %s (%s)' %
                                 (instance, method.__name__, etype.__name__,
                                  value), args, kwargs))
            try:
                six.reraise(etype, value, trace)
            finally:
                del trace  # to avoid circular refs

    return exception_wrapper


def log_init(method):
    """
    Decorator to add log to init method
    """

    @functools.wraps(method)
    def init_logger_wrapper(instance, *args, **kwargs):
        instance.logger.info(
            _format_call_msg('INIT %r' % instance, args, kwargs))
        return method(instance, *args, **kwargs)

    return init_logger_wrapper


def assert_arg(arg, validator):
    """
    Decorator to add a validator on a given argument
    """

    def decorated(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_args = list(args)
            try:
                if type(arg) is int and arg < len(args):
                    try:
                        new_args[arg] = validator(args[arg])
                    except Exception as er:
                        if is_list(args[arg]):
                            new_args[arg] = [validator(a) for a in args[arg]]
                        else:
                            raise InvalidValue()
                elif not type(arg) is int:
                    kwargs[arg] = validator(kwargs[arg])
            except Exception as er:
                if type(arg) is int:
                    msg = _('arg at position %i is not valid (%s)' %
                            (arg, args[arg]))
                else:
                    msg = _('keyword arg %s is not valid (%s)' % (arg,
                                                                  kwargs[arg]))
                raise InvalidValue(msg)

            return func(*new_args, **kwargs)

        return wrapper

    return decorated


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

    def decorated(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # case first argument is an array
            if type(args[narg1]) in [list, set, tuple]:
                ret = []
                new_args = list(args)
                # only first argument is an array
                if narg2 == -1 or not type(
                        args[narg2]) in [list, set, tuple] or len(
                            args[narg2]) == 1:
                    for v in args[narg1]:
                        new_args[narg1] = v
                        ret.append(func(*new_args, **kwargs))
                # both are list
                else:
                    # same size - call with zipped values
                    if len(args[narg1]) == len(args[narg2]):
                        for v1, v2 in zip(args[narg1], args[narg2]):
                            new_args[narg1] = v1
                            new_args[narg2] = v2
                            ret.append(func(*new_args, **kwargs))
                    # different size
                    else:
                        raise InvalidValue(
                            _('arguments %s and %s must be of same size' %
                              (narg1, narg2)))
            else:
                # if the first one is not a string, ignore and call func
                return func(*args, **kwargs)
            if flatten:
                return [item for sublist in ret for item in sublist]
            return ret

        doc = [wrapper.__doc__] if wrapper.__doc__ else []
        if narg2 != -1:
            doc.append(
                'Arguments in position %i and %i can take arrays of same size, and the function will perfom the operation in parallel and return the result as a list.'
                % (narg1 + 1, narg2 + 1))
        else:
            doc.append(
                'Argument in position %i can take an array, and the function will perfom the operation on each element and return the result as a list.'
                % (narg1 + 1))
        if flatten:
            doc.append('The resulting list of lists if flattened.')
        wrapper.__doc__ = '\n'.join(doc)
        return wrapper

    return decorated


def assert_prop(instance, *args):
    def decorated(func):
        for prop in args:
            # look in schema ?
            if prop not in list(instance.keys()):
                raise exceptions.PropertyNotInSchema(prop)
            # look in validated data
            if not instance.get(prop):
                raise exceptions.PropertyUndefined(prop)

        @functools.wraps(func)
        def wrapper(instance, *args, **kwargs):
            return func(instance, *args, **kwargs)

        return wrapper

    return decorated

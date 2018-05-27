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
import six
import inspect
from builtins import object
from builtins import str
from pprint import pformat

from python_jsonschema_objects.validators import ValidationError

from .exceptions import InvalidValue
from .validators import convert_validate

_ = gettext.gettext


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

        doc = [wrapper.__doc__.strip()] if wrapper.__doc__ else []
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


def assert_arg(arg, schema):
    """
    Decorator to add a schema to validate a given argument
    """

    def decorated(func):
        sig = inspect.getargspec(func)
        arg_ = arg
        if sig.defaults and type(arg) is int and arg >= (len(sig.args)-len(sig.defaults)):
            arg_ = sig.args[arg]
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_args = list(args)
            try:
                if type(arg_) is int and arg < len(args):
                    new_args[arg_] = convert_validate(args[arg_], schema)
                elif not type(arg_) is int and arg_ in kwargs:
                    kwargs[arg] = convert_validate(kwargs[arg], schema)
            except Exception as er:
                if type(arg_) is int:
                    raise InvalidValue(_('arg "%s"(=%s) is not valid. %s') %
                                      (sig.args[arg_], args[arg_], er.message))
                else:
                    raise InvalidValue(_('arg "%s"(=%s) is not valid. %s') %
                                        (arg_, kwargs[arg_], er.message))
                raise InvalidValue(msg)

            return func(*new_args, **kwargs)

        wrapper.__doc__ = ((wrapper.__doc__ or '').strip() +
        '\nArgument %r is ' % arg +
        'automatically type converted and validated against this schema %s.'
        % pformat(schema))
        return wrapper

    return decorated

def _format_call_msg(funcname, args, kwargs):
    return '%s(%s)'%(funcname,', '.join(['%s'%a for a in args]
                     +['%s=%s'%(a,v) for a, v in kwargs.items()]))


def log_exceptions(method):
    """
    Decoractor to log exceptions in instance logger
    """

    @functools.wraps(method)
    def exception_wrapper(instance, *args, **kwargs):
        try:
            sig = inspect.getargspec(method)
            instance.logger.debug('CALL ' +
                _format_call_msg('%r.%s' % (instance, method.__name__),
                                 args, kwargs))
            return method(instance, *args, **kwargs)
        except Exception as er:
            etype, value, trace = sys.exc_info()
            sig = inspect.getargspec(method)
            instance.logger.error('CALL ' +
                _format_call_msg('%r.%s' % (instance, method.__name__),
                                 args, kwargs) +
                '\n\tERROR %s: %s'% (etype.__name__, value))
            try:
                six.reraise(etype, value, trace)
            finally:
                del trace  # to avoid circular refs

    return exception_wrapper


def log_init(method):
    """
    Decorator to add log to init method
    """
    sig = inspect.getargspec(method)

    @functools.wraps(method)
    def init_logger_wrapper(instance, *args, **kwargs):
        method(instance, *args, **kwargs)
        instance.logger.info(
            _format_call_msg('INIT %r' % instance, args, kwargs))

    return init_logger_wrapper


def assert_prop(instance, *args):
    def decorated(func):
        for prop in args:
            # look in schema ?
            if prop not in instance._properties:
                raise AttributeError(_("No property %s."%prop))
            # look in validated data
            if instance._properties.get(prop,None) is None:
                raise ValidationError(_('%s is not defined.'%prop))

        @functools.wraps(func)
        def wrapper(instance, *args, **kwargs):
            return func(instance, *args, **kwargs)

        wrapper.__doc__ = ((wrapper.__doc__ or '').strip() +
        '\nProperties %r are asserted to be defined in instance.' % args)
        return wrapper

    return decorated

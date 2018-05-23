# *- coding: utf-8 -*-
"""
Utilities for learning about live objects, including modules, classes, instances,
functions, and methods

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
created on 02/01/2018
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import ast
import gettext
import importlib
import inspect
import itertools
import types
from builtins import next
from builtins import object
from builtins import str
from builtins import zip

from ._string_utils import is_string
from ._utils import import_from_string
from .doc_rest_parser import parse_docstring
from .exceptions import InvalidValue

_ = gettext.gettext


class Argument(object):
    """
    Class for function/method attributes
    """
    doc = None
    _typ = None
    _default = None

    def __init__(self, name, doc=None, typ=None):
        self.name = name
        self.doc = doc
        self._typ = typ
        self._has_default = False

    def __repr__(self):
        ret = '<arg %s' % self.name
        if self._has_default:
            ret += '=%s' % self.default
        return ret + '>'

    @property
    def default(self):
        if self._has_default:
            return self._default
        return

    @default.setter
    def default(self, value):
        self._has_default = True
        self._default = value

    @property
    def type(self):
        return self._typ


# global variale used in visit_FunctionDef
# set by inspectors when inspecting a class/function
_module = None


def visit_FunctionDef(node):
    """ ast node visitor """
    doc = parse_docstring(ast.get_docstring(node))
    _short_desc = doc['shortDescription']
    _long_desc = doc['longDescription']

    doc_params = doc['params']
    _returns = doc['returns']

    docs = [
        doc_params[a.id]['doc'] if a.id in doc_params else None
        for a in node.args.args
    ]
    types = [
        doc_params[a.id]['type']
        if a.id in doc_params and 'type' in doc_params[a.id] else None
        for a in node.args.args
    ]

    _params = [
        Argument(arg.id, doc, typ)
        for arg, doc, typ in zip(node.args.args, docs, types)
    ]

    _keywords = node.args.kwarg
    _varargs = node.args.vararg
    _defaults = [ast.literal_eval(d) for d in node.args.defaults]
    for d, p in zip(reversed(_defaults), reversed(_params)):
        p.default = d
    _decorators = []
    for n in node.decorator_list:
        name = ''
        if isinstance(n, ast.Call):
            name = n.func.attr if isinstance(n.func,
                                             ast.Attribute) else n.func.id
            args = [ast.literal_eval(d) for d in n.args]
        else:
            name = n.attr if isinstance(n, ast.Attribute) else n.id
            args = []
        dec = getattr(_module, name, None)
        if not dec:
            dec = name
        else:
            dec = FunctionInspector(dec)
            for a, p in zip(args, dec.parameters):
                p.default = a
        _decorators.append(dec)
    return _short_desc, _long_desc, _returns, _params, _keywords, _varargs, _decorators


class FunctionInspector(object):
    """
    Class to inspect a function
    """

    def __init__(self, function=None, **kwargs):
        """
        FunctionInspector is normally initialized giving it a function
        """
        self.name = None
        self.doc = None
        self.shortDescription = None
        self.longDescription = None
        self.returns = None
        self.parameters = []
        self.keywords = None
        self.varargs = None
        self.decorators = []

        for k, v in list(kwargs.items()):
            setattr(self, k, v)
        if function:
            self._from_function(function)

    def has_param(self, param):
        return any([p.name == param for p in self.parameters])

    def _from_function(self, function):
        global _module
        if is_string(function):
            function = import_from_string(function)
        if not inspect.isfunction(function) and not inspect.ismethod(function):
            raise InvalidValue(
                _('%r is not a function or a method' % function))
        self.function = function
        self.name = function.__name__
        self.doc = self.function.__doc__.strip()
        _module = importlib.import_module(function.__module__)
        self.module = _module
        self.moduleName = _module.__name__

        def _visit_FunctionDef(node):
            if node.name == self.name and node.lineno == self.function.__code__.co_firstlineno:
                sd, ld, rt, ps, kw, va, decs = visit_FunctionDef(node)
                self.shortDescription = sd
                self.longDescription = ld
                self.returns = rt
                self.parameters = ps
                self.keywords = kw
                self.varargs = va
                self.decorators = decs

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = _visit_FunctionDef
        node_iter.visit(ast.parse(inspect.getsource(_module)))

    def __repr__(self):
        return '<FunctionInsp %s>' % self.name.__repr__()


class ClassInspector(object):
    """
    Class to inspect a class
    """

    def __init__(self, klass):
        self.name = None
        self.doc = None
        self.shortDescription = None
        self.longDescription = None
        self.attributes = {}
        self.attributesInherited = {}
        self.properties = {}
        self.propertiesInherited = {}
        self.methods = {}
        self.methodsInherited = {}
        self.mro = []
        self._from_class(klass)

    def _from_class(self, klass):
        global _module
        if is_string(klass):
            klass = import_from_string(klass)
        if not inspect.isclass(klass):
            raise InvalidValue(_('%r is not a class' % klass))

        self.klass = klass
        self.name = klass.__name__
        self.doc = klass.__doc__
        doc = parse_docstring(klass.__doc__)
        self.shortDescription = doc['shortDescription']
        self.longDescription = doc['longDescription']
        _module = importlib.import_module(klass.__module__)
        self.module = _module
        self.moduleName = _module.__name__

        ms = inspect.getmembers(klass, inspect.ismethod)
        ds = inspect.getmembers(klass, inspect.isdatadescriptor)
        self.properties = {n: d for n, d in ds if isinstance(d, property)}
        self.attributes = {n: d for n, d in ds if not isinstance(d, property)}

        def _visit_FunctionDef_class(node):
            sd, ld, rt, ps, kw, va, decs = visit_FunctionDef(node)
            mi = FunctionInspector(
                name=node.name,
                shortDescription=sd,
                longDescription=ld,
                returns=rt,
                parameters=ps,
                keywords=kw,
                varargs=va,
                decorators=decs)
            mi.function = getattr(self.klass, node.name, None)
            mi.doc = mi.function.__doc__
            mi.module = self.module
            mi.moduleName = self.moduleName
            mi.isStatic = isinstance(mi.function, types.FunctionType)
            # remove first argument if not static
            if not mi.isStatic:
                mi.parameters.pop(0)
            self.methods[node.name] = mi

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = _visit_FunctionDef_class
        node = ast.parse(inspect.getsource(self.klass))
        node_iter.visit(node)

        self.mro = []
        for mro in inspect.getmro(self.klass)[1:]:
            if mro.__module__ in ['future.types.newobject', '__builtin__']:
                break
            ci_mro = ClassInspector(mro)
            self.mro.append(ci_mro)
            self.attributesInherited.update(ci_mro.attributes)
            self.propertiesInherited.update(ci_mro.properties)
            self.methodsInherited.update(ci_mro.methods)

    def __repr__(self):
        return '<ClassInsp %s>' % self.name

    @property
    def init(self):
        return self.methods.get('__init__', None)

    @property
    def methodsAll(self):
        return dict(
            itertools.chain(self.methods.iteritems(),
                            self.methodsInherited.iteritems()))

    @property
    def methodsPublic(self):
        return {
            n: m
            for n, m in self.methodsAll()
            if n not in list(self.properties.keys(
            ) + self.propertiesInherited.keys()) and not n.startswith('_')
        }


def gcs(*instances):
    mros = (type(ins).mro() for ins in instances)
    mro = next(mros)
    common = set(mro).intersection(*mros)
    return next((x for x in mro if x in common), None)


def inspect_file(file_):
    """
    Retrieves the list of function names and the list of class names of a python
    source file

    :param file_: file path
    :type file_: [str, path]
    """
    r = open(str(file_), 'r')
    t = ast.parse(r.read())
    return ([d.name for d in t.body if isinstance(d, ast.FunctionDef)],
            [d.name for d in t.body if isinstance(d, ast.ClassDef)], [
                d.targets[0].id for d in t.body
                if isinstance(d, ast.Assign) and hasattr(d.targets[0], 'id')
                and d.targets[0].id[0].isupper()
            ])

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
import importlib
import inspect
import itertools
import logging
from builtins import next
from builtins import object
from builtins import str
from builtins import zip

import six

from .doc_rest_parser import parse_docstring
from .doc_rest_parser import parse_type_string
from ngoschema.exceptions import InvalidValue
from ngoschema.utils import import_from_string
from ngoschema.utils import is_string

logger = logging.getLogger(__name__)

EXCLUDED_MODULES = [
    None, str.__class__.__module__, "future.types.newobject", "__builtin__",
    '_abcoll', 'abc', 'collections.abc'
]


class Argument(object):
    """
    Class for function/method attributes
    """

    def __init__(self, name, doc=None, doctype=None):
        self.name = name
        self._has_default = False
        self._doc = doc
        self._type = None
        if doctype:
            try:
                self._type = parse_type_string(doctype)
            except Exception as er:
                logger.error(
                    "impossible to parse valid schema from type doc %s",
                    doctype)

    def __repr__(self):
        ret = "<arg %s" % self.name
        if self._has_default:
            ret += "=%s" % self.default
        return ret + ">"

    @property
    def doc(self):
        return self._doc

    @property
    def type(self):
        return self._type

    @property
    def default(self):
        if self._has_default:
            return self._default
        return

    @default.setter
    def default(self, value):
        self._has_default = True
        self._default = value


# global variale used in visit_FunctionDef
# set by inspectors when inspecting a class/function
_module = None


def _id(arg):
    return getattr(arg, "id", None) or getattr(arg, "arg")


def ast_name(ast_attr):
    if isinstance(ast_attr, ast.Attribute):
        return ast_attr.attr
    if isinstance(ast_attr, (ast.Name, ast.Call)):
        return _id(ast_attr)
    return ast.literal_eval(ast_attr)


def visit_FunctionDef(node):
    """ ast node visitor """
    doc = parse_docstring(ast.get_docstring(node))
    _short_desc = doc["shortDescription"]
    _long_desc = doc["longDescription"]

    doc_params = doc["params"]
    _returns = doc["returns"]

    docs = [
        doc_params[_id(a)].get("doc", None) if _id(a) in doc_params else None
        for a in node.args.args
    ]
    doctypes = [
        doc_params[_id(a)]["type"]
        if _id(a) in doc_params and "type" in doc_params[_id(a)] else None
        for a in node.args.args
    ]

    _params = [
        Argument(_id(arg), doc, doctype)
        for arg, doc, doctype in zip(node.args.args, docs, doctypes)
    ]

    _keywords = node.args.kwarg.arg if hasattr(node.args.kwarg,
                                               'arg') else node.args.kwarg
    _varargs = node.args.vararg.arg if hasattr(node.args.vararg,
                                               'arg') else node.args.vararg
    _defaults = [ast.literal_eval(d) for d in node.args.defaults]
    for d, p in zip(reversed(_defaults), reversed(_params)):
        p.default = d

    decorators = []
    for n in node.decorator_list:
        name = ""
        if isinstance(n, ast.Call):
            name = ast_name(n.func)
            args = [ast_name(d) for d in n.args]
        else:
            name = ast_name(n)
            args = []
        dec = getattr(_module, name, None)
        if not dec:
            dec = name
        else:
            dec = FunctionInspector(dec)
            for a, p in zip(args, dec.parameters):
                p.default = a
        decorators.append(dec)
    return _short_desc, _long_desc, _returns, _params, _keywords, _varargs, decorators


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
        if not (inspect.isfunction(function) or inspect.ismethod(function)
                or type(function) in [staticmethod, classmethod]):
            raise InvalidValue("%r is not a function or a method" % function)
        self.function = function
        self.doc = self.function.__doc__
        if self.doc:
            self.doc = self.doc.strip()

        if not type(function) in [staticmethod, classmethod]:
            self.name = getattr(function, "__name__", None)
            _module = importlib.import_module(function.__module__)
        else:
            self.name = getattr(function, "__name__", None)
            _module = importlib.import_module(function.__class__.__module__)
        self.module = _module
        self.moduleName = _module.__name__
        if self.moduleName in EXCLUDED_MODULES:
            return

        def _visit_FunctionDef(node):
            if (node.name == self.name
                    and node.lineno == self.function.__code__.co_firstlineno):
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
        return "<FunctionInsp %s>" % repr(self.name)


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
            raise InvalidValue("%r is not a class" % klass)

        self.klass = klass
        self.name = klass.__name__
        self.doc = klass.__doc__
        if self.doc:
            self.doc = self.doc.strip()
            doc = parse_docstring(klass.__doc__)
            self.shortDescription = doc["shortDescription"]
            self.longDescription = doc["longDescription"]
        else:
            self.shortDescription = None
            self.longDescription = None
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
                decorators=decs,
            )
            mi.function = getattr(self.klass, node.name, None)
            mi.doc = mi.function.__doc__
            mi.module = self.module
            mi.moduleName = self.moduleName
            mi.isStatic = "staticmethod" in mi.decorators
            # remove first argument if not static
            if not mi.isStatic:
                mi.parameters.pop(0)
            self.methods[node.name] = mi

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = _visit_FunctionDef_class

        # avoid builtin
        def is_builtin(obj):
            mn = obj.__module__
            return (mn in EXCLUDED_MODULES)

        if not is_builtin(self.klass):
            node = ast.parse(inspect.getsource(self.klass))
            node_iter.visit(node)

        self.mro = []
        for mro in inspect.getmro(self.klass)[1:]:
            if is_builtin(mro):
                break
            ci_mro = ClassInspector(mro)
            self.mro.append(ci_mro)
            self.attributesInherited.update(ci_mro.attributes)
            self.propertiesInherited.update(ci_mro.properties)
            self.methodsInherited.update(ci_mro.methods)

    def __repr__(self):
        return "<ClassInsp %s>" % self.name

    @property
    def init(self):
        return self.methods.get("__init__", None)

    @property
    def methodsAll(self):
        return dict(
            itertools.chain(
                six.iteritems(self.methods),
                six.iteritems(self.methodsInherited)))

    @property
    def methodsPublic(self):
        return {
            n: m
            for n, m in self.methodsAll.items()
            if n not in list(self.properties.keys() +
                             self.propertiesInherited.keys())
            and not n.startswith("_")
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
    r = open(str(file_), "r")
    t = ast.parse(r.read())
    return (
        [d.name for d in t.body if isinstance(d, ast.FunctionDef)],
        [d.name for d in t.body if isinstance(d, ast.ClassDef)],
        [
            ast_name(d.targets[0]) for d in t.body
            if isinstance(d, ast.Assign) and (
                hasattr(d.targets[0], "id") or hasattr(d.targets[0], "id"))
            and ast_name(d.targets[0])[0].isupper()
        ],
    )

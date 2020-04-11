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
import builtins
from builtins import next
from builtins import object
from builtins import str
from builtins import zip

import six

from .doc_rest_parser import parse_docstring
from .doc_rest_parser import parse_type_string
from ngoschema import decorators as decorators_mod
from ngoschema.exceptions import InvalidValue
from ngoschema.utils import import_from_string
from ngoschema.utils import is_string, is_class, is_function, is_callable, is_imported, infer_json_schema

logger = logging.getLogger(__name__)

EXCLUDED_MODULES = [
    None, str.__class__.__module__, "future.types.newobject", "__builtin__",
    '_abcoll', 'abc', 'collections.abc'
]


class Argument(object):
    """
    Class for function/method attributes
    """

    def __init__(self, name, schema=None, doc=None, doctype=None):
        self.name = name
        self.default = None
        self.value = None
        self.doc = doc
        self.schema = schema
        if doctype:
            try:
                self.schema = parse_type_string(doctype)
            except Exception as er:
                logger.error("impossible to parse valid schema from type doc %s", doctype)
        assert not is_string(self.schema)

    def __repr__(self):
        ret = "<arg %s" % self.name
        if self.default is not None:
            ret += "=%s" % self.default
        return ret + ">"

    def to_json_schema(self, **ns):
        sch = dict(self.type or {'type': 'object'})
        if self.doc:
            sch['description'] = self.doc
        if self.default:
            sch['default'] = self.default
        return sch

# global variale used in visit_FunctionDef
# set by inspectors when inspecting a class/function
_module = None


def _id(arg):
    return getattr(arg, "id", None) or getattr(arg, "arg")


def ast_name(node):
    if isinstance(node, ast.Call):
        return ast_name(node.func)
    if isinstance(node, ast.Attribute):
        return node.attr
    return getattr(node, "id", None) or getattr(node, "arg", None) or ast.literal_eval(node)


def ast_parts(node):
    parts = []
    if isinstance(node, ast.Attribute):
        parts.append(node.attr)
        parts.extend(ast_parts(node.value))
    if isinstance(node,ast.Name):
        parts.append(getattr(node, "id", None) or getattr(node, "arg"))
    return parts


def ast_eval(node, module=None):
    try:
        return ast.literal_eval(node) if node else node
    except Exception as er:
        from ..utils import import_from_string
        module = module or _module
        to_import = ast_parts(node) + [module.__name__]
        to_import = '.'.join(reversed(to_import))
        return import_from_string(to_import)


def visit_function_def(node):
    """ ast node visitor """
    doc = parse_docstring(ast.get_docstring(node))
    module = _module
    short_desc = doc["short_description"]
    long_desc = doc["long_description"]

    doc_params = doc["params"]
    returns = doc["returns"]

    args = node.args.args
    defs = node.args.defaults
    kwargs = node.args.kwarg
    vargs = node.args.vararg

    docs = [
        doc_params[ast_name(a)].get("doc", None) if ast_name(a) in doc_params else None
        for a in args
    ]
    doctypes = [
        doc_params[ast_name(a)]["type"]
        if ast_name(a) in doc_params and "type" in doc_params[ast_name(a)] else None
        for a in args
    ]

    params = [
        Argument(ast_name(arg), doc=doc, doctype=doctype)
        for arg, doc, doctype in zip(args, docs, doctypes)
    ]
    defaults = [ast_eval(d) for d in defs]
    for d, p in zip(reversed(defaults), reversed(params)):
        p.default = d

    varargs = Argument(ast_name(vargs)) if vargs else None
    keywords = Argument(ast_name(kwargs)) if kwargs else None

    decorators = []
    for n in node.decorator_list:
        name = ast_name(n)
        d_args_val = []
        d_kwargs_val = {}
        if isinstance(n, ast.Call):
            d_args_val = [ast_eval(d, module) for d in n.args]
            d_kwargs_val = {ast_name(kw): ast_eval(kw.value, module) for kw in n.keywords}
        dec = getattr(module, name, None) or getattr(builtins, name, None)
        assert dec, 'impossible to find decorator %s' % name
        if is_function(dec):
            dec = FunctionInspector(dec)
            for a, p in zip(d_args_val, dec.parameters):
                p.value = a
            if len(dec.parameters) < len(d_args_val):
                dec.varargs = d_args_val[len(dec.parameters):]
            if dec.keywords:
                dec.keywords.value = d_kwargs_val
        elif is_class(dec):
            dec = ClassInspector(dec)
            if d_args_val or d_kwargs_val:
                raise Exception('TODO setting value in class from dec args and kwargs values')
        decorators.append(dec)
        # process assert_arg arguments to complete parameter types
        if dec.name == 'assert_arg':
            arg = dec.parameters[0].value
            arg_schema = dec.varargs if dec.varargs is not None else dec.parameters[1].value
            if arg_schema:
                if is_string(arg):
                    for p in params:
                        if p.name == arg:
                            param = p
                            break
                else:
                    param = params[arg]
                param.type = arg_schema
    return short_desc, long_desc, returns, params, keywords, varargs, decorators


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
        self.short_description = None
        self.long_description = None
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
        self.module_name = _module.__name__
        if self.module_name in EXCLUDED_MODULES:
            return

        def _visit_function_def(node):
            if (node.name == self.name
                    and node.lineno == self.function.__code__.co_firstlineno):
                sd, ld, rt, ps, kw, va, decs = visit_function_def(node)
                self.short_description = sd
                self.long_description = ld
                self.returns = rt
                self.parameters = ps
                self.keywords = kw
                self.varargs = va
                self.decorators = decs

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = _visit_function_def
        node_iter.visit(ast.parse(inspect.getsource(self.module)))

    def __repr__(self):
        return "<FunctionInsp %s>" % repr(self.name)


class ClassInspector(object):
    """
    Class to inspect a class
    """

    def __init__(self, cls):
        self.name = None
        self.doc = None
        self.short_description = None
        self.long_description = None
        self.attributes = {}
        self.attributes_inherited = {}
        self.properties = {}
        self.properties_inherited = {}
        self.methods = {}
        self.methods_inherited = {}
        self.mro = []
        self._from_class(cls)

    def _from_class(self, cls):
        global _module
        if is_string(cls):
            cls = import_from_string(cls)
        if not inspect.isclass(cls):
            raise InvalidValue("%r is not a class" % cls)

        self.cls = cls
        self.name = cls.__name__
        self.doc = cls.__doc__
        if self.doc:
            self.doc = self.doc.strip()
            doc = parse_docstring(cls.__doc__)
            self.short_description = doc["short_description"]
            self.long_description = doc["long_description"]
        else:
            self.short_description = None
            self.long_description = None
        _module = importlib.import_module(cls.__module__)
        self.module = _module
        self.module_name = _module.__name__

        #ms = inspect.getmembers(cls, inspect.ismethod)
        ds = inspect.getmembers(cls, inspect.isdatadescriptor)
        self.properties = {n: d for n, d in ds if isinstance(d, property)}
        self.attributes = {n: d for n, d in ds if not isinstance(d, property)}

        ds2 = inspect.getmembers(cls, lambda x: not is_callable(x))
        self.attributes = {n: d for n, d in ds2 if not n.startswith('__')}

        def _visit_function_def_class(node):
            global _module
            _module = self.module  # to reset global variable module to current class one
            sd, ld, rt, ps, kw, va, decs = visit_function_def(node)
            mi = FunctionInspector(
                name=node.name,
                short_description=sd,
                long_description=ld,
                returns=rt,
                parameters=ps,
                keywords=kw,
                varargs=va,
                decorators=decs,
            )
            mi.function = getattr(self.cls, node.name, None)
            mi.doc = mi.function.__doc__
            mi.module = self.module
            mi.module_name = self.module_name
            mi.is_staticmethod = "staticmethod" in [f.name for f in mi.decorators]
            mi.is_classmethod = "classmethod" in [f.name for f in mi.decorators]
            # remove first argument if not static
            if not mi.is_staticmethod and len(mi.parameters):
                mi.parameters.pop(0)
            self.methods[node.name] = mi

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = _visit_function_def_class

        # avoid builtin
        def is_builtin(obj):
            mn = obj.__module__
            return (mn in EXCLUDED_MODULES)

        if not is_builtin(self.cls):
            node = ast.parse(inspect.getsource(self.cls))
            node_iter.visit(node)

        self.mro = []
        for mro in inspect.getmro(self.cls)[1:]:
            if is_builtin(mro):
                break
            ci_mro = ClassInspector(mro)
            self.mro.append(ci_mro)
            self.attributes_inherited.update(ci_mro.attributes)
            self.properties_inherited.update(ci_mro.properties)
            self.methods_inherited.update(ci_mro.methods)

    def __repr__(self):
        return "<ClassInsp %s>" % self.name

    @property
    def init(self):
        return self.methods.get("__init__", None)

    @property
    def methods_all(self):
        return dict(
            itertools.chain(
                six.iteritems(self.methods),
                six.iteritems(self.methods_inherited)))

    @property
    def methods_public(self):
        return {
            n: m
            for n, m in self.methods_all.items()
            if n not in list(self.properties.keys() +
                             self.properties_inherited.keys())
            and not n.startswith("_")
        }

    def to_json_schema(self, use_init=True, **ns):
        from ..classbuilder import get_builder
        uri = get_builder().get_cname_ref(f'{self.module_name}.{self.name}', **ns)
        schema = {
            '$id': uri,
            'type': 'object',
            'description': self.doc,
            'title': self.name
        }
        if self.doc is None:
            del schema['description']
        extends = [get_builder().get_cname_ref(f'{m.module_name}.{m.name}', **ns) for m in self.mro]
        if extends:
            schema['extends'] = extends
        props = {k: infer_json_schema(v) for k, v in self.attributes.items()}
        if use_init:
            props_init = {k.name: k.to_json_schema() for k in self.init.parameters}
            props.update(props_init)
        if props:
            schema['properties'] = props
        return schema


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


def module_to_json_schema(module, **ns):
    m = module if is_imported(module) else import_from_string(module)
    defs = {}
    schema = {
        'type': 'object',
        'description': (m.__doc__ or '').strip(),
        'title': m.__name__,
        'definitions': defs
    }
    for name, kls in inspect.getmembers(m, inspect.isclass):
        try:
            defs[name] = ClassInspector(kls).to_json_schema(**ns)
        except Exception as er:
            pass
    for name, mod in inspect.getmembers(m, lambda x: inspect.ismodule(x) and any([x.__name__.startswith(n) for n in ns.keys()])):
        defs[name] = module_to_json_schema(mod, **ns)
    return schema

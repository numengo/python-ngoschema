# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import ast
import inspect

from .doc_rest_parser import parse_docstring
from .. import settings
from .ast import visit_function_def, set_visit_module, ast_name, ast_eval, reindent

EXCLUDED_MODULES = settings.INSPECT_EXCLUDED_MODULES


def inspect_importable(value):
    from ..types.symbols import Importable
    symbol = Importable.convert(value)
    importable = {
        'name': symbol.__name__,
        'symbol': symbol,
    }
    doc = symbol.__doc__
    if doc:
        importable['doc'] = doc.strip()
        doc_parsed = parse_docstring(doc)
        importable['shortDescription'] = doc_parsed["short_description"]
        importable['description'] = doc_parsed["long_description"]
    return importable


def inspect_module(value):
    from ..types.symbols import Module
    value = Module.convert(value)
    return inspect_importable(value)


def inspect_function(value):
    from ..types.symbols import Module
    function = inspect_importable(value)
    symbol = function['symbol']
    function['name'] = getattr(symbol, '__name__', None)
    module = symbol.__module__ if not type(function) in [staticmethod, classmethod] else symbol.__class__.__module__
    function['module'] = Module()(module)
    if module in EXCLUDED_MODULES:
        return function

    def _visit_function_def(node):
        if node.name == function['name']:
            set_visit_module(module)
            function.update(visit_function_def(node))

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = _visit_function_def
    node_iter.visit(ast.parse(reindent(inspect.getsource(symbol))))
    return function


def inspect_function_call(value):
    function_call = inspect_function(value)
    symbol = function_call['symbol']
    module = function_call['module']

    def _visit_function_def(node):
        if node.name == function_call['name'] and node.lineno == symbol.__code__.co_firstlineno:
            set_visit_module(module)
            function_call.update(visit_function_def(node))
            d_args_val = []
            d_kwargs_val = {}
            if isinstance(node, ast.Call):
                d_args_val = [ast_eval(d, module) for d in node.args]
                d_kwargs_val = {ast_name(kw): ast_eval(kw.value, module) for kw in node.keywords}

            for a, p in zip(d_args_val, function_call['arguments']):
                p.value = a
            if len(function_call['arguments']) < len(d_args_val):
                function_call['varargs']['valueLiteral'] = d_args_val[len(function_call['arguments']):]
            if function_call['keywords']:
                function_call['keywords']['valueLiteral'] = d_kwargs_val

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = _visit_function_def
    node_iter.visit(ast.parse(reindent(inspect.getsource(symbol))))
    return function_call


def inspect_class(value):
    from ..types.symbols import Module, Function, Method, Callable
    cls = inspect_importable(value)
    symbol = cls['symbol']
    cls['name'] = symbol.__name__
    cls['name'] = getattr(symbol, '__name__', None)
    module = symbol.__module__
    cls['module'] = Module()(module)
    if module in EXCLUDED_MODULES:
        return cls

    ds = inspect.getmembers(symbol, inspect.isdatadescriptor)
    cls['properties'] = {n: d for n, d in ds if isinstance(d, property)}
    cls['attributes'] = {n: d for n, d in ds if not isinstance(d, property)}

    ds2 = inspect.getmembers(symbol, lambda x: not (Function.check(x) or Callable.check(x)))
    cls['attributes'] = {n: d for n, d in ds2 if not n.startswith('__')}
    cls['methods'] = {}

    def _visit_function_def_class(node):
        set_visit_module(module)
        cls_symbol = getattr(symbol, node.name, None)
        if Function.check(cls_symbol) or Method.check(cls_symbol):
            mi = visit_function_def(node)
            # only testing decorators, but what to do?
            mi['static'] = 'staticmethod' in [f['name'] for f in mi['decorators']]
            mi['class'] = 'classmethod' in [f['name'] for f in mi['decorators']]
            # remove first argument if not static
            if not mi['static'] and len(mi['arguments']):
                mi['arguments'].pop(0)
            cls['methods'][node.name] = mi

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = _visit_function_def_class

    # avoid builtin
    def is_builtin(obj):
        mn = obj.__module__
        return (mn in EXCLUDED_MODULES)

    if not is_builtin(symbol):
        node = ast.parse(reindent(inspect.getsource(symbol)))
        node_iter.visit(node)

    cls['mro'] = []
    cls['attributesInherited'] = {}
    cls['propertiesInherited'] = {}
    cls['methodsInherited'] = {}
    for mro in inspect.getmro(symbol)[1:]:
        if is_builtin(mro):
            break
        ci_mro = inspect_class(mro)
        cls['mro'].append(ci_mro)
        cls['attributesInherited'].update(ci_mro['attributes'])
        cls['propertiesInherited'].update(ci_mro['properties'])
        cls['methodsInherited'].update(ci_mro['methods'])
    return cls
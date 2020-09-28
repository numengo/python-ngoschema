# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import ast
import inspect
from collections import Mapping, Sequence, Set
from inspect import ismethod, ismodule, isfunction, isclass, isdatadescriptor, iscoroutine, isroutine, isbuiltin
from functools import lru_cache

from .doc_rest_parser import parse_docstring
from .. import settings
from .ast import visit_function_def, set_visit_module, ast_name, ast_eval, reindent

EXCLUDED_MODULES = settings.INSPECT_EXCLUDED_MODULES
EXCLUDED_DESCRIPTORS = settings.INSPECT_EXCLUDED_DESCRIPTORS
EXCLUDED_ATTRIBUTES = settings.INSPECT_EXCLUDED_ATTRIBUTES

logger = logging.getLogger(__name__)


def isattr(obj):
    return not (isclass(obj) or ismethod(obj) or isfunction(obj) or ismodule(obj) or isdatadescriptor(obj)
                or isroutine(obj) or isinstance(obj, type))


def infer_type(value):
    from ..protocols import ObjectProtocol
    if value is None:
        return {}
    if isinstance(value, str):
        return {'type': 'string'}
    if isinstance(value, (Sequence, Set)):
        ret = {'type': 'array'}
        if isinstance(value, Set):
            ret['uniqueItems'] = True
        vt = [infer_type(v) for v in value]
        if vt:
            vt0 = vt[0]
            if all([v == vt0 for v in vt]):
                ret['items'] = vt0
            else:
                ret['items'] = vt
        return ret
    if isinstance(value, bool):
        return {'type': 'boolean'}
    if isinstance(value, int):
        return {'type': 'integer'}
    if isinstance(value, float):
        return {'type': 'number'}
    if isinstance(value, type):
        return {'type': 'importable'}
    if isinstance(value, Mapping) and not isinstance(value, ObjectProtocol):
        return {'type': 'object'}
    c = value.__class__
    mro = c.__mro__
    for m in mro:
        if inspect.isabstract(m):
            c = m
            break
    if not isbuiltin(c) and issubclass(c, ObjectProtocol):
        return {'$ref': c._id}
    return {'type': 'object'}


# avoid builtin
def is_builtin(obj):
    mn = obj.__module__
    return not (hasattr(obj, '_id') or mn not in EXCLUDED_MODULES)


@lru_cache(maxsize=512)
def inspect_symbol(value):
    from ..types.symbols import Symbol
    symbol = Symbol.convert(value)
    importable = {
        'symbol': symbol,
    }
    if hasattr(symbol, '__name__'):
        importable['name'] = symbol.__name__
    doc = symbol.__doc__
    if doc:
        doc_parsed = parse_docstring(doc.strip())
        importable.update(doc_parsed)
    return importable


@lru_cache(maxsize=512)
def inspect_module(value, with_functions=True):
    from ..types.symbols import Module
    value = Module.convert(value)
    module = inspect_symbol(value).copy()
    mn = value.__name__
    module['modules'] = [m for n, m in inspect.getmembers(value, inspect.ismodule) if n not in EXCLUDED_MODULES]
    module['classes'] = []
    for n, m in inspect.getmembers(value, inspect.isclass):
        if m.__module__ == mn:
            try:
                module['classes'].append(inspect_class(m, with_functions=with_functions))
            except Exception as er:
                logger.error('Problem processing inspection of class %s' % m)
                logger.error(er, exc_info=True)
    if with_functions:
        module['functions'] = []
        for n, m in inspect.getmembers(value, inspect.isfunction):
            if m.__module__ == mn:
                try:
                    module['functions'].append(inspect_function(m))
                except Exception as er:
                    logger.error('Problem processing inspection of function %s' % m)
                    logger.error(er)  #, exc_info=True)
        if not module['functions']:
            del module['functions']
    return module


@lru_cache(maxsize=512)
def inspect_function(value):
    from ..types.symbols import Module
    function = inspect_symbol(value).copy()
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


@lru_cache(maxsize=512)
def inspect_function_call(value):
    function_call = inspect_function(value).copy()
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
            if function_call['kwargs']:
                function_call['kwargs']['valueLiteral'] = d_kwargs_val

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = _visit_function_def
    node_iter.visit(ast.parse(reindent(inspect.getsource(symbol))))
    return function_call


@lru_cache(maxsize=512)
def inspect_descriptor(value, name=None):
    from ..protocols.object_protocol import PropertyDescriptor
    desc = inspect_symbol(value).copy()
    del desc['symbol']
    if name:
        desc['name'] = name
    if isinstance(value, PropertyDescriptor):
        desc['$schema'] = 'https://numengo.org/ngoschema#/$defs/protocols/$defs/descriptors/$defs/PropertyDescriptor'
        if desc['name'] != value.pname:
            desc['pname'] = value.pname
        desc['ptype'] = dict(value.ptype._schema)
        if value.fget:
            desc['fget'] = inspect_function(value.fget)
        if value.fset:
            desc['fset'] = inspect_function(value.fset)
        if value.fdel:
            desc['fdel'] = inspect_function(value.fdel)
    return desc


@lru_cache(maxsize=128)
def inspect_class(value, with_functions=True):
    from ..types.symbols import Module, Function, Method, Callable, Class
    cls = inspect_symbol(value).copy()
    if 'arguments' in cls:
        del cls['arguments']
    symbol = cls['symbol']
    cls['name'] = getattr(symbol, '__name__', None)
    module = symbol.__module__
    cls['module'] = Module()(module)
    if module in EXCLUDED_MODULES:
        return cls

    mro = []
    for m in inspect.getmro(symbol)[1:]:
        if is_builtin(m):
            continue
        mro.append(m)
        #mro.append(inspect_class(m))
    if mro:
        cls['mro'] = mro
    mro_i = [inspect_class(m, with_functions=with_functions) for m in mro]
    mro_attributes = {a['name']: a for m in mro_i for a in m.get('attributes', [])}
    mro_descriptors = {d['name']: d for m in mro_i for d in m.get('descriptors', [])}

    ds = inspect.getmembers(symbol, inspect.isdatadescriptor)
    descriptors = [inspect_descriptor(d, name=n) for n, d in ds if n not in EXCLUDED_DESCRIPTORS]
    descriptors = [d for d in descriptors if d['name'] not in mro_descriptors]
    _descriptors = {d['name']: d for d in descriptors}

    ds2 = inspect.getmembers(symbol, lambda x: isattr(x))
    attributes = [{'name': n, 'valueLiteral': d} for n, d in ds2 if not n.startswith('__') and n not in EXCLUDED_ATTRIBUTES]
    attributes = [a for a in attributes if a not in mro_attributes.values()]
    # infer attribute types:
    to_pop = []
    for i, a in enumerate(attributes):
        an = a['name']
        at = infer_type(a['valueLiteral'])
        at['default'] = a['valueLiteral']
        if at:
            d = dict(mro_descriptors[an]) if an in mro_descriptors else {'name': an}
            d.setdefault('ptype', {})
            d['ptype'].update(at)
            descriptors.append(d)
            to_pop.append(i)

    for i in reversed(to_pop):
        attributes.pop(i)
    if attributes:
        cls['attributes'] = attributes

    if descriptors:
        cls['descriptors'] = descriptors

    methods = []
    def _visit_function_def_class(node):
        set_visit_module(module)
        cls_symbol = getattr(symbol, node.name, None)
        if Function.check(cls_symbol) or Method.check(cls_symbol):
            mi = visit_function_def(node)
            decs = mi.get('decorators', [])
            #mi['name'] = node.name
            # only testing decorators, but what to do?
            if 'staticmethod' in [f['name'] for f in decs]:
                mi['static'] = True
            if 'classmethod' in [f['name'] for f in decs]:
                mi['class'] = True
            # remove first argument if not static
            if not mi.get('static') and len(mi.get('arguments', [])):
                mi['arguments'].pop(0)
            #if 'arguments' in mi and not mi['arguments']:
            #    del mi['arguments']
            methods.append(mi)

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = _visit_function_def_class

    if not is_builtin(symbol):
        if with_functions:
            try:
                node = ast.parse(reindent(inspect.getsource(symbol)))
                node_iter.visit(node)
            except Exception as er:
                logger.error('Problem processing class %s: %s' % (symbol, er))
                #logger.error(er, exc_info=True)
        else:
            si = getattr(symbol, '__init__', None)
            if si and isfunction(si):
                node = ast.parse(reindent(inspect.getsource(si)))
                node_iter.visit(node)

    for m in methods:
        if m['name'] == '__init__':
            cls['init'] = m
            methods.remove(m)
            break
    if methods:
        cls['methods'] = methods

    return cls


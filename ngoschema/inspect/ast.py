# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import ast
import logging
import inspect
import builtins
import importlib
from pathlib import Path

from .doc_rest_parser import parse_docstring, parse_type_string

# global variale used in visit_FunctionDef
# set by inspectors when inspecting a class/function
_module = None
_module_symbols = {}

logger = logging.getLogger(__name__)


def set_visit_module(module):
    global _module, _module_symbols
    _module = module
    # parse module to get its symbols
    m = importlib.import_module(module)
    _module_symbols = {k: v for k, v in builtins.__dict__.items()}
    source = Path(m.__file__).read_text()
    parsed = ast.parse(source)
    for node in parsed.body:
        if isinstance(node, ast.ImportFrom):
            for n in node.names:
                im_name = '.' * node.level + (node.module or '')
                im = importlib.import_module(im_name, module.rsplit('.', 1)[0] if node.level else None)
                _module_symbols[n.name] = getattr(im, n.name, None)
        elif isinstance(node, ast.Import):
            for n in node.names:
                _module_symbols[n.name] = importlib.import_module(n.name)
        elif isinstance(node, ast.FunctionDef):
            _module_symbols[node.name] = getattr(m, node.name, None)



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
        from ngoschema.utils import import_from_string
        module = module or _module
        to_import = ast_parts(node) + [module]
        to_import = '.'.join(reversed(to_import))
        return import_from_string(to_import)


def visit_function_def(node):
    """ ast node visitor """
    from ..types.literals import String
    from ..types.symbols import Function, Class
    from .inspect_symbols import inspect_function, inspect_function_call, inspect_class
    module = _module
    doc = parse_docstring(ast.get_docstring(node))
    short_desc = doc["short_description"]
    long_desc = doc["long_description"]
    doc_params = doc["params"]
    returns = doc["returns"]

    args = node.args.args
    defs = node.args.defaults
    kwargs = node.args.kwarg
    vargs = node.args.vararg
    args_name = [ast_name(a) for a in args]
    docs = [doc_params[a].get("doc", None) if a in doc_params else None
            for a in args_name]
    doctypes = [doc_params[a]["type"]
                if a in doc_params and "type" in doc_params[a] else None
                for a in args_name]
    params = [{'name': a, 'description': doc, 'doctype': doctype}
              for a, doc, doctype in zip(args_name, docs, doctypes)]
    defaults = [ast_eval(d) for d in defs]
    for d, p in zip(reversed(defaults), reversed(params)):
        p['defaultValueLiteral'] = d

    varargs = {'name': ast_name(vargs)} if vargs else None
    keywords = {'name': ast_name(kwargs)} if kwargs else None

    decorators = []
    for n in node.decorator_list:
        name = ast_name(n)
        d_args_val = []
        d_kwargs_val = {}
        if isinstance(n, ast.Call):
            d_args_val = [ast_eval(d, module) for d in n.args]
            d_kwargs_val = {ast_name(kw): ast_eval(kw.value, module) for kw in n.keywords}
        symbol = _module_symbols.get(name)
        assert symbol, 'impossible to find decorator %s' % name
        if Function.check(symbol):
            from ..utils import qualname
            from ..types import Literal, Boolean, Integer
            dec = inspect_function_call(symbol)
            for a, p in zip(d_args_val, dec['arguments']):
                p['value'] = a
                p['valueLiteral'] = a if String.check(a) or Boolean.check(a, convert=False) or Integer.check(a) else qualname(a)
            if len(dec['arguments']) < len(d_args_val):
                dec['varargs']['valueLiteral'] = d_args_val[len(dec['arguments']):]
            if dec['keywords']:
                dec['keywords']['valueLiteral'] = d_kwargs_val
        elif Class.check(symbol):
            dec = inspect_class(symbol)
            if d_args_val or d_kwargs_val:
                raise Exception('TODO setting value in class from dec args and kwargs values')
        decorators.append(dec)
        # process assert_arg arguments to complete arguments types
        if dec['name'] == 'assert_arg':
            arg = dec['arguments'][0]['valueLiteral']
            arg_schema = dec['varargs']['valueLiteral'] if dec.get('varargs') else dec['arguments'][1]['valueLiteral']
            if arg_schema:
                if String.check(arg):
                    for p in params:
                        if p['name'] == arg:
                            param = p
                            break
                else:
                    param = params[arg]
                param['type'] = arg_schema
    return {
        'shortDescription': short_desc,
        'description': long_desc,
        'return': returns,
        'arguments': params,
        'keywords': keywords,
        'varargs': varargs,
        'decorators': decorators
    }


def reindent(source):
    indent = min([len(line)-len(line.lstrip()) for line in source.split('\n') if line])
    return '\n'.join(l[indent:] for l in source.split('\n'))



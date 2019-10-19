# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import ast
import copy
import inspect
"""
Copyright 2015, Wouter Bolsterlee

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of
conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or other materials
provided with the distribution.
Neither the name of the author nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written
permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
"""
Module to find out the qualified name of a class.
"""

__all__ = ["qualname"]

_cache = {}


class _Visitor(ast.NodeVisitor):
    def __init__(self):
        super(_Visitor, self).__init__()
        self.stack = []
        self.qualnames = {}

    def store_qualname(self, lineno):
        qn = ".".join(n for n in self.stack)
        self.qualnames[lineno] = qn

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.store_qualname(node.lineno)
        self.stack.append("<locals>")
        self.generic_visit(node)
        self.stack.pop()
        self.stack.pop()

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.store_qualname(node.lineno)
        self.generic_visit(node)
        self.stack.pop()


def qualname(obj):
    """Find out the qualified name for a class or function."""

    # For Python 3.3+, this is straight-forward.
    if hasattr(obj, "__qualname__"):
        return obj.__qualname__

    # For older Python versions, things get complicated.
    # Obtain the filename and the line number where the
    # class/method/function is defined.
    try:
        filename = inspect.getsourcefile(obj)
    except TypeError:
        return obj.__qualname__  # raises a sensible error
    if inspect.isclass(obj):
        try:
            _, lineno = inspect.getsourcelines(obj)
        except (OSError, IOError):
            return obj.__qualname__  # raises a sensible error
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        if hasattr(obj, "im_func"):
            # Extract function from unbound method (Python 2)
            obj = obj.im_func
        try:
            code = obj.__code__
        except AttributeError:
            code = obj.func_code
        lineno = code.co_firstlineno
    else:
        return obj.__qualname__  # raises a sensible error

    # Re-parse the source file to figure out what the
    # __qualname__ should be by analysing the abstract
    # syntax tree. Use a cache to avoid doing this more
    # than once for the same file.
    qualnames = _cache.get(filename)
    if qualnames is None:
        with open(filename, "r") as fp:
            source = fp.read()
        node = ast.parse(source, filename)
        visitor = _Visitor()
        visitor.visit(node)
        _cache[filename] = qualnames = visitor.qualnames
        # add treatment to avoid problems with decorators
        lines = source.splitlines()
        orig_qualnames = copy.copy(visitor.qualnames)
        for i, v in orig_qualnames.items():
            i2 = i
            while True:
                if lines[i2 - 1].strip().startswith('@'):
                    i2 += 1
                    qualnames[i2] = v
                else:
                    break
        _cache[filename] = qualnames
    try:
        return qualnames[lineno]
    except KeyError:
        return obj.__qualname__  # raises a sensible error

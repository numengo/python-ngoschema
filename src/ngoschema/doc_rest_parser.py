# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import sys
from builtins import object
from builtins import str
from .str_utils import multiple_replace

# Copyright 2015: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

##### C. ROMAN (NUMENGO) modifies regex to retrieve type of parameters

PARAM_OR_RETURNS_REGEX = re.compile(":(?:param|type|rtype)")
RETURNS_REGEX = re.compile(":rtype:\s*(?P<doc>.*)", re.S)
PARAM_REGEX = re.compile(":param (?P<name>[\*\w]+):\s*(?P<doc>.*?)"
                         "(?:(?=:param)|(?=:type)|(?=:rtype)|(?=:raises)|\Z)",
                         re.S)
TYPE_REGEX = re.compile(":type (?P<name>[\*\w]+):\s*(?P<type>.*?)"
                        "(?:(?=:param)|(?=:type)|(?=:rtype)|(?=:raises)|\Z)",
                        re.S)


def trim(docstring):
    """trim function from PEP-257"""
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Current code/unittests expects a line return at
    # end of multiline docstrings
    # workaround expected behavior from unittests
    if "\n" in docstring:
        trimmed.append("")

    # Return a single string:
    return "\n".join(trimmed)


def reindent(string):
    return "\n".join(l.strip() for l in string.strip().split("\n"))


def parse_docstring(docstring):
    """
    Parse the docstring into its components.

    :param docstring: docstring to parse
    :returns: a dictionary of form
              {
                  "shortDescription": ...,
                  "longDescription": ...,
                  "params": { name: {"type", ..., "doc": ...}},
                  "returns": ...
              }
    """

    short_description = long_description = returns = ""
    params = []

    def add2dict(dic,k,el):
        k = k.strip()
        if not k in dic: dic[k] = {}
        dic[k].update(el)

    if docstring:
        docstring = trim(docstring)

        lines = docstring.split("\n", 1)
        short_description = lines[0]

        if len(lines) > 1:
            long_description = lines[1].strip()

            params_returns_desc = None

            match = PARAM_OR_RETURNS_REGEX.search(long_description)
            if match:
                long_desc_end = match.start()
                params_returns_desc = long_description[long_desc_end:].strip()
                long_description = long_description[:long_desc_end].rstrip()

            if params_returns_desc:
                all = PARAM_REGEX.findall(params_returns_desc)
                params = { name.strip() : { "doc": trim(doc).strip() }
                           for name, doc in PARAM_REGEX.findall(params_returns_desc)}
                types = TYPE_REGEX.findall(params_returns_desc)
                for name, typ in types:
                    add2dict(params,name,{"type": typ.strip()})

                match = RETURNS_REGEX.search(params_returns_desc)
                if match:
                    returns = reindent(match.group("doc"))

    return {
        "doc": docstring,
        "shortDescription": short_description,
        "longDescription": long_description,
        "params": params,
        "returns": returns
    }


class InfoMixin(object):
    @classmethod
    def _get_doc(cls):
        """
        Return documentary of class
        By default it returns docstring of class, but it can be overridden
        for example for cases like merging own docstring with parent
        """
        return cls.__doc__

    @classmethod
    def get_info(cls):
        doc = parse_docstring(cls._get_doc())

        return {
            "name": cls.get_name(),
            "platform": cls.get_platform(),
            "module": cls.__module__,
            "title": doc["shortDescription"],
            "description": doc["longDescription"],
            "parameters": doc["params"],
            "returns": doc["returns"]
        }

def parse_type_string(typestring):
    """
    Parse a type string and returns a json schema compliant type
    """
    # this is not pretty, but it should cover most cases
    typestring = typestring.strip()
    if typestring[0] != '{':
        if typestring.startswith('enum'):
            typestring = '{%s}'%typestring
        else:
            typestring = '{type:%s}'%typestring
    ret = re.sub(r'(\w+)',r'"\1"',typestring)
    aliases = {
        '=': ':',
        '"tuple"' : '"list"',
        '"set"' : '"list", "uniqueItems":True',
        '"bool"' : '"boolean"',
        '"int"' : '"integer"',
        '"float"' : '"number"',
        '"str"' : '"string"',
        '"text"' : '"string"',
        '"dict"' : '"object"',
        '"choice"' : '"enum"',
        '"uri"-"reference"' : '"uri-reference"',
        '"uri"-"template"' : '"uri-template"',
        '"date"-"time"' : '"date-time"',
        '"json"-"pointer"' : '"json-pointer"',
        '"pathlib.Path"': '"path"',
        '"True"' : 'True',
        '"true"' : 'True',
        '"False"' : 'False',
        '"false"' : 'False',
    }
    ret = multiple_replace(ret, aliases)
    return eval(ret)

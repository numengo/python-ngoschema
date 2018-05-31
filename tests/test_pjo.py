# -*- coding: utf-8 -*-
"""
Script to convert *.ngom files from EMF to json format

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from builtins import object
from builtins import str
from past.builtins import basestring


import os, os.path
import logging
from collections import (OrderedDict as odict, Iterable)
import json
import dpath.util
import pathlib
import jsonschema
import re
import copy
from pprint import pprint

#import ngoschema
import python_jsonschema_objects as pjo

from jsonschema import Draft4Validator
from jsonschema.exceptions import ValidationError, RefResolutionError, FormatError

from ngoschema.schemas_loader import load_module_schemas
from ngoschema.resolver import ExpandingResolver, DEFAULT_MS_URI, get_resolver
from ngoschema.validators import NgoDraft02Validator

#logging.basicConfig(level=logging.DEBUG)

#classbuilder.logger.addHandler(logging.StreamHandler())
#import python_jsonschema_objects.classbuilder as classbuilder
#classbuilder.logger.setLevel(logging.INFO)

ms_uri = DEFAULT_MS_URI
defs_uri = 'http://numengo.org/draft-03/defs-schema'

ms = load_module_schemas()
resolver = ExpandingResolver(ms_uri,ms[ms_uri],ms)

def test_builder_ngo_defs():
    try:
        #meta_validator = NgoDraft02Validator(ms[ms_uri], resolver=resolver, format_checker=jsonschema.draft7_format_checker)
        ##meta_validator = NgoDraft02Validator(jsonschema.Draft6Validator.META_SCHEMA)
        #meta_validator.validate(ms[ms_uri])
        ##meta_validator.validate(ms['http://numengo.org/draft-02/defs-schema'])
        #print(ms_uri)

        #builder = pjs.ObjectBuilder(ms[defs_uri])
        resolver = ExpandingResolver(defs_uri, ms[defs_uri], ms)
        #builder = NgoObjectBuilder(ms[defs_uri], resolver=resolver, validatorClass=NgoDraft02Validator)

        # need forked ObjectBuilder
        builder = pjo.ObjectBuilder(ms[defs_uri], resolver=resolver, validatorClass=NgoDraft02Validator)
        ns = builder.build_classes()
        essai = ns.Package

    except ValidationError as er:
        print(er.message)

def test_pjo():
    sch = {
      "title": "Example Schema",
      "type": "object",
      "properties": {
        "firstName": {
            "type": "string"
        },
        "lastName": {
            "type": "string"
        }
      }
    }
    try:
        builder = pjo.ObjectBuilder(sch)
        ns = builder.build_classes()
        Person = ns.ExampleSchema
        p = Person(firstName="James", lastName="Bond")
        p.firstName = 1
        print(p.firstName)
    except Exception as er:
        print(er)

def test_pjo_typed_arrays():
    example_schema = {
      "title": "types arrays",
      "$id": "test#", 
      "type": "object",
      "definitions": {
        "PathList": {
          "additionalProperties": False, 
          "type": "object", 
          "properties": {
            "paths": {
              "type": "array",
              "items": {
                  "type": "#/definitions/Path"
              }
            },
          }
        },
        "Path": {
          "additionalProperties": False, 
          "type": "object", 
          "properties": {
            "path" : { "type": "string"},
            "isFilepath": {
              "readOnly": True, 
              "type": "boolean"
            }
          }
        }
      }
    }
    try:
        builder = pjo.ObjectBuilder(example_schema)
        ns = builder.build_classes()
        PathList = ns.PathList
        Path = ns.Path
        #p1 = Path("a string")
        #p1 = Path(1)
        p1 = Path(path="a string")
        #p2 = Path(path=1)
        pl = PathList(paths=[p1, "a string"])
    except Exception as er:
        print(er)


if __name__ == "__main__":
    test_builder_ngo_defs()
    #test_pjo()
    test_pjo_typed_arrays()

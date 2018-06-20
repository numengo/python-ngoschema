# -*- coding: utf-8 -*-
"""

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import os.path
import logging

from jsonschema import RefResolver

from ngoschema import DEFAULT_MS_URI
from ngoschema.resolver import ExpandingResolver
from ngoschema.resolver import get_resolver
from ngoschema.schemas_loader import get_all_schemas_store
from ngoschema.schemas_loader import load_schema_file

logging.basicConfig(level=logging.INFO)

test_dir = os.path.dirname(os.path.realpath(__file__))
defs_fp = os.path.join(test_dir, "schemas", "ngo-defs-draft-XX.json")
DEFS_URI, DEFS = load_schema_file(defs_fp)
MS_STORE = get_all_schemas_store()

resolver = ExpandingResolver(DEFAULT_MS_URI, MS_STORE[DEFAULT_MS_URI],
                             MS_STORE)
orig_resolver = RefResolver(DEFAULT_MS_URI, MS_STORE[DEFAULT_MS_URI], MS_STORE)


def test_resolver():
    ref1 = "%s#/definitions/Metadata" % DEFAULT_MS_URI
    ref2 = "#/definitions/Metadata"
    assert resolver.resolve(ref1) == resolver.resolve(ref2)
    assert resolver.resolve("http://json-schema.org/geo")


def test_resolve_by_name():
    id, sch = resolver.resolve_by_name("RealVariable")
    assert sch


def test_expand_schema():
    id, sch = resolver.resolve_by_name("ComponentDefinition")
    id, sch2 = orig_resolver.resolve(id)

    if False:
        with open("ComponentDefinition_expanded.json", "w") as outfile:
            json.dump(sch, outfile, indent=2)

        with open("ComponentDefinition.json", "w") as outfile:
            json.dump(sch2, outfile, indent=2)

    assert len(sch["properties"]) > len(sch2["properties"])
    # pprint(sch2)


def test_get_resolver():
    resolver = get_resolver()
    id, sch = resolver.resolve_by_name("ComponentDefinition")


if __name__ == "__main__":
    test_resolver()
    test_resolve_by_name()
    test_expand_schema()
    test_get_resolver()

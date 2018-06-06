# -*- coding: utf-8 -*-
"""
Unit tests for validators of NgoProject

test_validators.py - created on 2018/05/06
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging

from jsonschema import RefResolver

from ngoschema import DEFAULT_MS_URI
from ngoschema import MS_STORE
from ngoschema.resolver import ExpandingResolver
from ngoschema.resolver import get_resolver

logging.basicConfig(level=logging.INFO)

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

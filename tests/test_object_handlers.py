# -*- coding: utf-8 -*-
"""
Unit tests for utilities

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import print_function
from __future__ import unicode_literals

import logging
logging.basicConfig(level=logging.INFO)

from ngomf import variable, variable_group, component, package
from ngoschema import object_registry

r1 = object_registry.ObjectRegistry()
r2 = object_registry.ObjectWeakRegistry()

def test_registry_add():
    v1 = variable.RealVariable(name="v1")
    v2 = variable.RealVariable(name="v2")
    r1.add(v1)
    r1.add(v2)

    r2.add(v1)
    r2.add(v2)

def test_registry_persistence():
    assert len(r1)==2
    assert len(r2)==2
    ks = list(r1.keys())
    for k in ks:
        r1.remove(k)
    print(len(r2))
    assert len(r2)==0

if __name__ == "__main__":
    test_registry_add()
    test_registry_persistence()

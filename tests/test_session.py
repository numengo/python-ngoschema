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

from ngomf.models import variable
from ngoschema.session import session_maker, scoped_session

Session = scoped_session(session_maker())


def test_session():
    s1 = Session()
    s2 = Session()
    v1 = variable.RealVariable(name="v1")
    v2 = variable.RealVariable(name="v2")
    s1.register(v1)
    s2.register(v2)


def test_global_session():
    pass


if __name__ == "__main__":
    test_session()

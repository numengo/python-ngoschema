#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" start-up script to launch all units tests """

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import pytest
    pytest.main()
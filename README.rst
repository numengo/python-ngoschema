========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-ngoschema/badge/?style=flat
    :target: https://readthedocs.org/projects/python-ngoschema
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/numengo/python-ngoschema.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/numengo/python-ngoschema

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/numengo/python-ngoschema?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/numengo/python-ngoschema

.. |requires| image:: https://requires.io/github/numengo/python-ngoschema/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/numengo/python-ngoschema/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/numengo/python-ngoschema/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/numengo/python-ngoschema

.. |version| image:: https://img.shields.io/pypi/v/ngoschema.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/ngoschema

.. |commits-since| image:: https://img.shields.io/github/commits-since/numengo/python-ngoschema/v0.2.2.svg
    :alt: Commits since latest release
    :target: https://github.com/numengo/python-ngoschema/compare/v0.2.2...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/ngoschema.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/ngoschema

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/ngoschema.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/ngoschema

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/ngoschema.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/ngoschema


.. end-badges

Description
===========

I'm Cédric ROMAN.

``ngoschema`` aims at building classes based on a `JSON schema
<https://spacetelescope.github.io/understanding-json-schema/index.html>`_.

User can declare its attributes in a schema (along with their type, default
value) and the class will be built with accessors to check and validate data.

User can add methods and override setters/getters, but the library provides a
boiler plate to automatically create the class, nicely instrumented (with loggers,
exception handling, type checking, data validation, etc...).

Objects created are come with managers to load/save them into files.

Serialization tools are provided that can be used to do code generation.

The library is build on top of `python-jsonschema-object
<https://github.com/cwacek/python-jsonschema-objects>`_, with a lot of hacking,
which allows to create classes
from a JSON-schema.

Both projects use the library `python-jsonchema
<http://python-jsonschema.readthedocs.io/en/latest/validate/>`_, a python
implementation for JSON schema validation.

* Free software: GNU General Public License v3

Installation
============

::

    pip install ngoschema

Documentation
=============

https://python-ngoschema.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |requires|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-ngoschema/badge/?style=flat
    :target: https://readthedocs.org/projects/python-ngoschema
    :alt: Documentation Status

.. |requires| image:: https://requires.io/github/numengo/python-ngoschema/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/numengo/python-ngoschema/requirements/?branch=master

.. |version| image:: https://img.shields.io/pypi/v/ngoschema.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/ngoschema

.. |commits-since| image:: https://img.shields.io/github/commits-since/numengo/python-ngoschema/v1.0.7.svg
    :alt: Commits since latest release
    :target: https://github.com/numengo/python-ngoschema/compare/v1.0.7...master

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

I'm Cedric ROMAN.

``ngoschema`` aims at automate the building of classes based on a `JSON schema
<https://spacetelescope.github.io/understanding-json-schema/index.html>`_.

User can declare all class attributes in a schema (along with their type, default
value) and the class will be built with accessors to check and validate data.

User can add methods and override setters/getters, but the library provides a
boiler plate to automatically create the class, nicely instrumented (with loggers,
exception handling, type checking, data validation, serialization, etc...).

The classbuilder allows to easily load definitions based on a canonical name and a namespace.

Instance of these classes can be iterated and behave as standard collections.

``ngoschema`` aims at being a toolkit for Domain-Driven Design and Model-Driven Architecture.

The library is build on top of `python-jsonchema
<http://python-jsonschema.readthedocs.io/en/latest/validate/>`_, a python
implementation for JSON schema validation.

* Free software: GNU General Public License v3

.. skip-next

Installation
============

To install, with the command line::

    pip install ngoschema

Documentation
=============

https://python-ngoschema.readthedocs.io/

Settings are managed using `simple-settings <https://github.com/drgarcia1986/simple-settings>`__
and can be overriden with configuration files (cfg, yaml, json) or with environment variables
prefixed with NGOSCHEMA_.

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


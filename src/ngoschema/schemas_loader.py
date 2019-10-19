# *- coding: utf-8 -*-
"""
Utilities and classes to deal with validators and resolvers

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import imp
import json
import logging
import collections
import pathlib
import pkgutil
from builtins import str

import inflection
import six

from ngofile.list_files import list_files

from ngoschema.exceptions import SchemaError


def _id_of(schema):
    return schema.get("$id", schema.get("id"))

def _load_schema(name):
    """
    Load a schema from ./schemas/``name``.json and return it.

    """
    data = pkgutil.get_data("ngoschema", "schemas/{0}.json".format(name))
    return json.loads(data.decode("utf-8"), object_pairs_hook=collections.OrderedDict)

def load_schema(schema, schemas_store=None):
    """
    Load a schema to the schema store.

    if no schema store is provided, only the internal schema store is filled.

    :param schema: schema as dictionary
    :type schema: dict
    :param schemas_store: optional schemas_store to fill
    :type schemas_store: dict
    """
    from .resolver import register_doc_with_uri_id, get_uri_doc_store
    uri = _id_of(schema).rstrip('#')
    if not uri and "title" in schema:
        uri = inflection.parameterize(six.text_type(schema["title"]), "_")
    if not uri:
        raise SchemaError(
            "Impossible to load schema because `id (or `$id) and `title fields"
            "are missing.\n%s" % schema)
    if schemas_store is not None:
        schemas_store[uri] = schema
    # add to main registry
    register_doc_with_uri_id(schema, uri)
    return uri, schema


def load_schema_file(schema_path, schemas_store=None):
    """
    Load a schema from a file to the metaschema store
    and returns the schema dictionary.

    :param schema_path: path to file containing schema
    :type schema_path: [string, path]
    :param schemas_store: optional schemas_store to fill
    :type schemas_store: dict
    :rtype: dict
    """
    with open(str(schema_path), "rb") as f:
        schema = json.loads(f.read().decode("utf-8"), object_pairs_hook=collections.OrderedDict)
        schema.setdefault('$id', pathlib.Path(schema_path).stem)
        return load_schema(schema, schemas_store)


def load_module_schemas(module="ngoschema", schemas_store=None):
    """
    Load the schemas of a module that are in the folder module
    as $(MODULEPATH)/schemas/*.json and add them with load_chema_file.
    User can provide an existing schema store to fill, or a new one
    will be created.

    return the loaded schema store

    :param module: module name where to look
    :param schemas_store: optional schemas_store to fill
    :type schemas_store: dict
    :rtype: dict
    """
    from .resolver import register_doc_with_uri_id, get_uri_doc_store
    logger = logging.getLogger(__name__)
    libpath = imp.find_module(module)[1]

    if schemas_store is None:
        schemas_store = get_uri_doc_store()
    for ms in list_files(libpath, "schemas/**.json", recursive=True):
        try:
            load_schema_file(ms, schemas_store)
        except Exception as er:
            logger.error(
                "Impossible to load file %s.\n%s", ms, er, exc_info=True)
    return schemas_store

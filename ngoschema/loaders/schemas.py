# *- coding: utf-8 -*-
"""
Utilities and classes to deal with validators and resolvers

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import collections
import pathlib
import logging
from builtins import str

import inflection
import six

from jsonschema.exceptions import SchemaError

logger = logging.getLogger(__name__)


def _id_of(schema):
    return schema.get("$id", schema.get("id"))


def load_schema(schema, schemas_store=None):
    """
    Load a schema to the schema store.

    if no schema store is provided, only the internal schema store is filled.

    :param schema: schema as dictionary
    :type schema: dict
    :param schemas_store: optional schemas_store to fill
    :type schemas_store: dict
    """
    from ngoschema.resolvers.uri_resolver import UriResolver
    uri = _id_of(schema).rstrip('#')
    if not uri and "title" in schema:
        uri = inflection.parameterize(six.text_type(schema["title"]), "_")
    if not uri:
        raise SchemaError(
            "Impossible to load schema because `id (or `$id) and `title fields"
            "are missing.\n%s" % schema)
    if schemas_store is not None:
        if schema != schemas_store.get(uri, schema):
            logger.info("Overwriting a different schema '%s' is already registered in schema store." % uri)
        schemas_store[uri] = schema
    # add to main registry
    UriResolver.register_doc(schema, uri)
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
        try:
            schema = json.loads(f.read().decode("utf-8"), object_pairs_hook=collections.OrderedDict)
            schema.setdefault('$id', pathlib.Path(schema_path).stem)
            return load_schema(schema, schemas_store)
        except Exception as er:
            logger.error(schema_path)
            logger.error(er, exc_info=True)
            raise

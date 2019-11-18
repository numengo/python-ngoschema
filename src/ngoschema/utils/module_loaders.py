import logging

from ngofile.list_files import list_files
from ngoschema import load_schema_file

from .utils import GenericModuleFileLoader

# loader to register module with a models folder where to look for templates
templates_module_loader = GenericModuleFileLoader('templates')

def load_module_templates(module_name):
    templates_module_loader.register(module_name)


# loader to register module with a transforms folder where to look for model transformations
transforms_module_loader = GenericModuleFileLoader('transforms')

def load_module_transforms(module_name):
    transforms_module_loader.register(module_name)


# loader to register module with a models folder where to look for objects
objects_module_loader = GenericModuleFileLoader('objects')

def load_module_objects(module_name):
    objects_module_loader.register(module_name)

# loader to register module with a models folder where to look for objects
schemas_module_loader = GenericModuleFileLoader('schemas')


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
    from ..resolver import get_uri_doc_store
    schema_folder = schemas_module_loader.register(module)

    logger = logging.getLogger(__name__)

    if schemas_store is None:
        schemas_store = get_uri_doc_store()
    for ms in list_files(schema_folder, "**.json", recursive=True):
        try:
            load_schema_file(ms, schemas_store)
        except Exception as er:
            logger.error(
                "Impossible to load file %s.\n%s", ms, er, exc_info=True)
    return schemas_store

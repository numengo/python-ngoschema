import logging

from ngofile.list_files import list_files

from ..schemas_loader import load_schema_file
from .utils import GenericModuleFileLoader

# loader to register module with a models folder where to look for templates
templates_module_loader = GenericModuleFileLoader('templates')

# loader to register module with a transforms folder where to look for model transformations
transforms_module_loader = GenericModuleFileLoader('transforms')

# loader to register module with a models folder where to look for objects
objects_module_loader = GenericModuleFileLoader('objects')

# loader to register module with a models folder where to look for static files
static_module_loader = GenericModuleFileLoader('static')

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
    from ..resolver import UriResolver
    schema_folder = schemas_module_loader.register(module)

    logger = logging.getLogger(__name__)

    if schemas_store is None:
        schemas_store = UriResolver.get_doc_store()
    if not schema_folder.exists():
        return schemas_store
    for ms in list_files(schema_folder, "**.json", recursive=True):
        try:
            load_schema_file(ms, schemas_store)
        except Exception as er:
            logger.error(
                "Impossible to load file %s.\n%s", ms, er)
    return schemas_store


def register_module(module_name):
    load_module_schemas(module_name)
    for module_loader in GenericModuleFileLoader.module_loaders_registry.values():
        module_loader.register(module_name)

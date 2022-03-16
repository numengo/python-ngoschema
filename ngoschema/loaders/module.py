import logging
import pathlib
import importlib

from ngofile.list_files import list_files
from ngofile.pathlist import PathList

from .schemas import load_schema_file
from ..utils import Registry


def update_default_jinja2_env():
    from ..utils.jinja2 import default_jinja2_env
    default_jinja2_env().update_loader()


class GenericModuleFileLoader(Registry):
    module_loaders_registry = {}

    def __init__(self, subfolder_name, update_function=None):
        Registry.__init__(self)
        self.subfolderName = subfolder_name
        self.update_function = update_function
        GenericModuleFileLoader.module_loaders_registry[subfolder_name] = self

    def register(self, module, subfolder_name=None):
        m = importlib.import_module(module)
        subfolder_name = subfolder_name or self.subfolderName
        subfolder = pathlib.Path(
            m.__file__).parent.joinpath(subfolder_name).resolve()
        if subfolder.exists():
            if module not in self._registry:
                self._registry[module] = []
            if subfolder not in self._registry[module]:
                self._registry[module].append(subfolder)
            if self.update_function:
                self.update_function()
        return subfolder

    def subfolder(self, module):
        return self._registry[module][0]

    def preload(self,
                includes=["*"],
                excludes=[],
                recursive=False,
                serializers=[]):
        from ..models.documents import get_document_registry
        all_paths = list(sum(self._registry.values(), []))
        for d in all_paths:
            get_document_registry().\
                register_from_directory(d,
                                        includes=includes,
                                        excludes=excludes,
                                        recursive=recursive,
                                        serializers=serializers)

    def find_one(self, name):
        """
        find first name/pattern in loader's pathlist (module as "{module}/")

        :param name: path or pattern
        :rtype: path
        """
        name = name.replace('\\', '/')
        if '/' in name:
            module, path = name.split('/', 1)
            if module in self._registry:
                return PathList(*self._registry[module]).pick_first(path)
        all_paths = list(sum(self._registry.values(), []))
        return PathList(*all_paths).pick_first(name)


# loader to register module with a models folder where to look for templates
templates_module_loader = GenericModuleFileLoader('templates', update_function=update_default_jinja2_env)

# loader to register module with a converters folder where to look for model transformations
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
    from ngoschema.resolvers.uri_resolver import UriResolver
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

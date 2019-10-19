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

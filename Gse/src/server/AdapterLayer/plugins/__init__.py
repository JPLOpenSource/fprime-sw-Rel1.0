# Initialize the package 
# __all__ is a list containing the name and path of the plugins

import os
__all__ = []
build_root = os.environ['BUILD_ROOT']
plugin_dir = os.path.join(build_root, "Gse/src/server/AdapterLayer/plugins")

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py': # Ignore all files that are not plugin implementations
        continue
    __all__.append({'name':module[:-3], 'path':os.path.join(plugin_dir, module)}) # Add the module paths to the package variable __all__
del module
del os

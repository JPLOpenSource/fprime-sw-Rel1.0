import imp
import plugins
from server.ServerUtils.server_config import ServerConfig

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

def LoadAdapters():

    object_dict= dict()
    for module_desc in plugins.__all__:
        name = module_desc['name']
        path = module_desc['path']
        mod  = imp.load_source(name, path)
        obj  = mod.GetObject()
        adapter_name = mod.GetAdapterName()
        object_dict[adapter_name] = obj
        
    return object_dict

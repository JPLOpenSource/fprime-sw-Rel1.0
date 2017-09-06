#===============================================================================
# NAME: adapter_utility.py
#
# DESCRIPTION: Contains a utility function for loading protocol adapter plugin module objects.
#
# AUTHOR: David Kooi
#
# EMAIL: david.kooi@nasa.jpl.gov
#        dkooi@ucsc.edu
#
#
# Copyright 2017, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

import imp
import plugins
from server.ServerUtils.server_config import ServerConfig

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

def LoadAdapters():
    """
    Iterate through the names and path of all the 
    plugin files. 

    Use imp to get an instance of the adapter object.
    """
    object_dict= dict()
    for module_desc in plugins.__all__:
        name = module_desc['name']
        path = module_desc['path']
        mod  = imp.load_source(name, path)
        
        obj  = mod.GetObject()              # Call module function for object
        adapter_name = mod.GetAdapterName() # Call module function for name
        object_dict[adapter_name] = obj
        
    return object_dict

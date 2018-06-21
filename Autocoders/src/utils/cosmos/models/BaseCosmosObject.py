#!/bin/env python
#===============================================================================
# NAME: CosmosObjectAbs.py
#
# DESCRIPTION: This abstract class is inherited by events, commands, and channels 
# in order to give them their most basic shared fields for the cheetah templates 
# i.e. user, date, source, etc.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from utils.cosmos.util import CosmosUtil

class BaseCosmosObject(object):
    """
    This abstract class represents the commonality between COSMOS channels,
    events, and commands.
    """
    
    def __init__(self, comp_name, comp_type, source):
        """
        @param comp_name: Component name of channel
        @param comp_type: Component type of channel
        @param source: XML source file of channel
        """
        self.comp_name = comp_name
        self.component_string = comp_name + "::" + comp_type
        self.source = source

        self.endianness = CosmosUtil.CMD_TLM_ENDIANNESS
        self.type_dict = {}
        self.min_dict = {}
        self.max_dict = {}
        self.default_dict = {}
        CosmosUtil.fill_cosmos_dicts(self.type_dict, self.min_dict, self.max_dict, self.default_dict)
        
    def get_source(self):
        """
        XML file location of instance
        """
        return self.source
    def get_endianness(self):
        """
        Packet endianness
        """
        return self.endianness
    def get_component_string(self):
        """
        Combination of component name and component type
        """
        return self.component_string
    def get_comp_name(self):
        """
        Component name
        """
        return self.comp_name
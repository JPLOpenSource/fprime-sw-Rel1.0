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

import os
import sys
import time
import datetime

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
        
        # Calculate date and user
        d = datetime.datetime.now()
        self.date = d.strftime("%A, %d, %B, %Y")
        self.user = os.environ['USER']
        
        self.endianness = "BIG_ENDIAN" # HARDCODED FOR FPRIME
        self.type_dict = {}
        self.min_dict = {}
        self.max_dict = {}
        self.default_dict = {}
        self.init_cosmos_dicts()
                
    def init_cosmos_dicts(self):
        """
        Initializes the FPrime type -> COSMOS type dict type_dicts,
        and each of the min, max, and default value dicts
        """
        self.type_dict["F32"] = (32, "FLOAT")
        self.type_dict["F64"] = (64, "FLOAT")
        self.type_dict["U8"] = (8, "UINT")
        self.type_dict["U16"] = (16, "UINT")
        self.type_dict["U32"] = (32, "UINT")
        self.type_dict["U64"] = (64, "UINT")
        self.type_dict["I8"] = (8, "INT")
        self.type_dict["I16"] = (16, "INT")
        self.type_dict["I32"] = (32, "INT")
        self.type_dict["I64"] = (64, "INT")
        self.type_dict["bool"] = (16, "BOOLEAN", "UINT")
        self.type_dict["string"] = (0, "STRING")
        self.type_dict["ENUM"] = (32, "ENUM", "UINT")
        
        self.min_dict["F32"] = -10000.0
        self.min_dict["F64"] = -100000.0
        self.min_dict["U8"] = 0
        self.min_dict["U16"] = 0
        self.min_dict["U32"] = 0
        self.min_dict["U64"] = 0
        self.min_dict["I8"] = -128
        self.min_dict["I16"] = -1000 #-32768
        self.min_dict["I32"] = -10000 #-2147483648
        self.min_dict["I64"] = -10000#-9223372036854775808
        self.min_dict["bool"] = 0
        self.min_dict["string"] = ""
        self.min_dict["ENUM"] = self.min_dict["U32"]
        
        self.max_dict["F32"] = 10000.0
        self.max_dict["F64"] = 100000.0
        self.max_dict["U8"] = 255
        self.max_dict["U16"] = 1000  #65535
        self.max_dict["U32"] = 10000 #4294967295
        self.max_dict["U64"] = 10000#18446744073709551615
        self.max_dict["I8"] = 127
        self.max_dict["I16"] = 32767
        self.max_dict["I32"] = 10000 #2147483647
        self.max_dict["I64"] = 10000 #9223372036854775807
        self.max_dict["bool"] = 1
        self.max_dict["string"] = "" # Dont use this, should be set elsewhere to value from topology
        self.max_dict["ENUM"] = self.max_dict["U32"]
        
        self.default_dict["F32"] = 0.0
        self.default_dict["F64"] = 0.0
        self.default_dict["U8"] = 0
        self.default_dict["U16"] = 0
        self.default_dict["U32"] = 0
        self.default_dict["U64"] = 0
        self.default_dict["I8"] = 0
        self.default_dict["I16"] = 0
        self.default_dict["I32"] = 0
        self.default_dict["I64"] = 0
        self.default_dict["bool"] = False
        self.default_dict["string"] = "String" # Dont use this, should be set elsewhere to value from topology
        self.default_dict["ENUM"] = 0
        
    def get_date(self):
        """
        Date instance was created
        """
        return self.date
    def get_user(self):
        """
        User who created the instance
        """
        return self.user
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
#!/bin/env python
#===============================================================================
# NAME: CosmosChannel.py
#
# DESCRIPTION: This class represents a channel within COSMOS to conveniently
# store all the values necessary for the cheetah template to generate channels.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from utils.cosmos.models import AbstractCosmosObject

class CosmosChannel(AbstractCosmosObject.AbstractCosmosObject):
    """
    This class represents a channel within COSMOS to conveniently store 
    all the values necessary for the cheetah template to generate channels.
    """
    
    def __init__(self, comp_name, comp_type, source, ch_id, name, comment):
        """
        @param param:  comp_name: Component name of channel
        @param comp_type: Component type of channel
        @param source: XML source file of channel
        @param ch_id: ID of channel
        @param comment: Channel description
        """
        super(CosmosChannel, self).__init__(comp_name, comp_type, source)
        self.id = ch_id
        self.ch_name = name
        self.ch_desc = comment
        self.value_bits = 0
        self.value_type = "ERROR: Value item type not set"
        self.format_string = "ERROR: Value item not set"
        self.types = []
    
    def set_arg(self, type, enum_name, enum, format_string):
        """
        Changes the COSMOS argument "VALUE" attached to the channel instance
        @param type: Fprime version of argument data type (U16 as opposed to COSMOS's 16 UINT)
        @param enum_name: Name of argument's enum (blank if true)
        @param enum: tuple containing name of enum as well as all name / value pairs, None if doesn't exist
        @param format_string: Optional formatting attachment for COSMOS "VALUE" argument
        """
        cosmos_type = self.type_dict[type]
        self.value_bits = cosmos_type[0]
        self.value_type = (cosmos_type[1] if not (cosmos_type[1] == "ENUM") else cosmos_type[2])
        # print enum_name
        
        # Handle units by setting nonexistant string to blank string for COSMOS template
        if format_string == None:
            format_string = ""
        self.format_string = format_string
        
        # Handle enum
        channel_enum_types = []
        count = 0
        if not enum == None:
            num = 0
            for item in enum[1]:
                if item[1] == None:
                    channel_enum_types.append((item[0], num))
                else:
                    channel_enum_types.append((item[0], int(item[1])))
                num += 1
        self.types = channel_enum_types

    def get_id(self):
        """
        Channel ID
        """
        return self.id
    def get_ch_name(self):
        """
        Channel name
        """
        return self.ch_name
    def get_ch_desc(self):
        """
        Channel description
        """
        return self.ch_desc
    def get_value_bits(self):
        """
        Number of bits in COSMOS "VALUE" argument
        """
        return self.value_bits
    def get_value_type(self):
        """
        COSMOS type of "VALUE" argument
        """
        return self.value_type
    def get_format_string(self):
        """
        Optional format string of "VALUE" argument
        """
        return self.format_string
    def get_types(self):
        """
        Enum's items
        """
        return self.types
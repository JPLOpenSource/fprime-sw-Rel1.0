#!/bin/env python
#===============================================================================
# NAME: CosmosEvent.py
#
# DESCRIPTION: This class represents an event within COSMOS to conveniently
# store all the values necessary for the cheetah template to generate events.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from utils.cosmos.models import BaseCosmosObject

class CosmosEvent(BaseCosmosObject.BaseCosmosObject):
    """
    This class represents an event within COSMOS to conveniently store 
    all the values necessary for the cheetah template to generate command.
    """
    
    class EventItem:
        """
        This class represents a COSMOS argument (item) attached to an event within 
        the COSMOS event config files.
        """
        def __init__(self, name, desc, bits, type, types, is_block = False):
            """
            @param name: Name of argument
            @param desc: Command description
            @param bits: Number of bits in argument
            @param type: COSMOS type for argument
            @param types: Contains enum data if is an enum
            @param is_block: Flag if value derived by extra COSMOS script for multi-string packet
            """
            self.name = name.upper()
            self.desc = desc
            self.bits = bits
            self.type = type
            self.types = types
            self.block = is_block
            self.neg_offset = False
            self.derived = False
            self.bit_offset = 0
            self.template_string = ""
            
        def convert_to_tuple(self):
            """
            Cheetah templates can't iterate over a list of classes, so
            converts all data into a Cheetah-friendly tuple
            (IS_BLOCK, IS_DERIVED, NAME, DESCRIPTION, TEMPLATE_STRING, TYPES, HAS_NEG_OFFSET, NEG_OFFSET, BITS, TYPE)
            """
            return (self.block, self.derived, self.name, self.desc, self.template_string, self.types, self.neg_offset, self.bit_offset, self.bits, self.type)
    
        def add_neg_offset_fields(self, bit_offset):
            """
            Sets flag representing whether there is an offset attached to field
            and adds a negative offset
            @param bit_offset: Number of bits from end of packet
            """
            self.bit_offset = bit_offset
            self.neg_offset = True
            self.block = False
            self.derived = False

        def add_derived_fields(self):
            """
            Sets flag representing whether there is multiple strings
            in the packet.  Handles using a separate script in config/lib/
            directory.  Template string must be attached to all arguments
            
            Template String Example For Third Argument(caps are real strings,
            lowercase w/ underscores are variable integer values):
            "bits_from_start_of_packet START arg1_bits arg1_data_type arg2_bits
            arg2_data_type arg3_bits arg3_data_type"
            """
            self.derived = True
            self.block = False
            self.neg_offset = False
    
    def __init__(self, comp_name, comp_type, source, name, evr_id, comment , severity, format_string):
        """
        @param comp_name: Name of event's component
        @param comp_type: Type of event's component
        @param source: XML source file of event
        @param name: Event name
        @param evr_id: Event ID
        @param comment: Event description
        @param severity: XML attribute "severity" found within XML source file
        @param format_string: XML attribute "format_string" found within XML source file
        """
        super(CosmosEvent, self).__init__(comp_name, comp_type, source)
        self.id = evr_id
        self.evr_name = name
        self.evr_desc = comment
        self.severity = severity
        self.format_string = format_string
        self.evr_items = []
        self.names = []
        self.non_len_names = []
        
    def add_block(self):
        """
        Adds a COSMOS item of type BLOCK to packet
        """
        item = self.EventItem("name", "desc", 0, "type", [], True)
        self.evr_items.append(item)
        
    def convert_items_to_cheetah_list(self, list):
        """
        Cheetah templates can't iterate over a list of classes, so
        converts all data into a Cheetah-friendly list of tuples
        (NAME, DESCRIPTION, ENUM, HAS_BIT_OFFSET, BIT_OFFSET, BITS, TYPE, MIN, MAX, DEFAULT)
        """
        temp = []
        
        for i in list:
            temp.append(i.convert_to_tuple())
        
        return temp
        
    def add_item(self, name, desc, bits, type, enum_name, enum, evr_type, bit_offset):
        """
        Adds an item to the event packet
        @param name: Name of item
        @param desc: Comment of item
        @param bits: Number of bits in item
        @param type: Fprime version of argument data type (U16 as opposed to COSMOS's 16 UINT)
        @param enum_name: Name of enum
        @param enum: Tuple with enum data
        @param evr_type: NEG_OFFSET: one string with more items after, DERIVED: multi-strings
        @param bit_offset: Contains an offset from back of packet
        """
        # Add the length item into the packet for the following string
        if type == 'string':
            if evr_type == 'DERIVED':
                len_item = self.EventItem(name + "_length", "Length of String Arg", 16, "UINT", [])
                len_item.add_derived_fields()
                self.evr_items.append(len_item)
            else:
                len_item = self.EventItem(name + "_length", "Length of String Arg", 16, "UINT", [])
                self.evr_items.append(len_item)
        
        cosmos_type = self.type_dict[type]
        value_type = (cosmos_type[1] if not (cosmos_type[1] == "ENUM" or cosmos_type[1] == "BOOLEAN") else cosmos_type[2])
        
        # Handle enum
        event_enum_types = []
        count = 0
        if not enum == None:
            num = 0
            for item in enum[1]:
                if item[1] == None:
                    event_enum_types.append((item[0], num))
                else:
                    event_enum_types.append((item[0], int(item[1])))
                num += 1
        types = event_enum_types
        
        # Set flag for each evr_type
        if evr_type == 'NEG_OFFSET':
            item = self.EventItem(name, desc, bits, value_type, types)
            item.add_neg_offset_fields(bit_offset)
        elif evr_type == 'DERIVED':
            item = self.EventItem(name, desc, bits, value_type, types)
            item.add_derived_fields()
        else:
            item = self.EventItem(name, desc, bits, value_type, types)
            
        # Append item to proper lists
        self.non_len_names.append(name)
        self.names.append(name)
        self.evr_items.append(item)
        
        # Fix format string for enums (in COSMOS %d for enum must be %s)
        if not enum == None:
            self.fix_format_str(len(self.evr_items) - 1)
        
        
    def fix_format_str(self, search_index):
                
        # Fix enums from %d to %s for COSMOS
        char_indexes = [i for i, ch in enumerate(self.format_string) if ch == "%"]
        
        ignore = False
        count = 0
        # Find count = search_index of "%" indexes in the format string and replace the following character (d in %d) with s (s in %s)
        for index in char_indexes:
            if ignore:
                ignore = False
            elif len(self.format_string) > index + 1 and not self.format_string[index + 1] == "%":
                if self.format_string[index + 1] == "d" and count == search_index:
                    self.format_string = self.format_string[:index + 1] + "s" + self.format_string[index + 2:]
                    break
            elif len(self.format_string) > index + 1:
                ignore = True
            count += 1
        
    def update_neg_offset(self):
        """
        Called when there are arguments after a string,
        determines their offset from the back of the packet.
        Only called when there is a single string 
        """
        reverse = False
        for item in self.evr_items:
            if item.type == 'STRING' and not item.block:
                reverse = True
                break
        
        count = 0
        if reverse:
            for item in reversed(self.evr_items):
                if item.type == 'STRING':
                    break
                count += item.bits
                item.bit_offset = count * -1
                
    def update_template_strings(self):
        """
        Calculates the template string for each item in packet with multiple strings
        
        Template String Example For Third Argument(caps are real strings,
        lowercase w/ underscores are variable integer values):
        "bits_from_start_of_packet START arg1_bits arg1_data_type arg2_bits
        arg2_data_type arg3_bits arg3_data_type"
        """
        # THIS AMOUNT IS HARDCODED, CHANGES WITH DIFFERENT PACKETS
        total_pre_item_bits = 256
        aggregate = str(total_pre_item_bits) + " START"
        for item in self.evr_items:
            if not item.block:
                item.template_string = aggregate + " " + str(item.bits) + " " + item.type
                aggregate = item.template_string
                
    def get_evr_items(self):
        """
        List of items in packet
        """
        return self.evr_items
    def get_evr_items_cosmos(self):
        """
        List of Cheetah-friendly tuples (see conversion method docs)
        """
        return self.convert_items_to_cheetah_list(self.evr_items)
    def get_names(self):
        """
        Event names
        """
        return self.names
    def get_nonlen_names(self):
        """
        List of items other than the length items appended before strings
        """
        return self.non_len_names
    def get_id(self):
        """
        Event ID
        """
        return self.id
    def get_evr_name(self):
        """
        Event name
        """
        return self.evr_name
    def get_evr_desc(self):
        """
        Event description
        """
        return self.evr_desc
    def get_severity(self):
        """
        XML attribute "severity" found within XML source file
        """
        return self.severity
    def get_format_string(self):
        """
        XML attribute "format_string" found within XML source file
        """
        return self.format_string

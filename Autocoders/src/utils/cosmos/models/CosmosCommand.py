#!/bin/env python
#===============================================================================
# NAME: CosmosCommand.py
#
# DESCRIPTION: This class represents a command within COSMOS to conveniently
# store all the values necessary for the cheetah template to generate commands.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

# Contains all Cosmos utility methods and interface / protocol variable data that isnt autocoded
from utils.cosmos.util import CosmosUtil

from utils.cosmos.models import BaseCosmosObject

class CosmosCommand(BaseCosmosObject.BaseCosmosObject):
    """
    This class represents a command within COSMOS to conveniently store 
    all the values necessary for the cheetah template to generate command.
    """
    
    class CommandItem:
        """
        This class represents a COSMOS argument (item) attached to a command within 
        the COSMOS command config files.
        """
        def __init__(self, name, desc, bits, type, types, min_val, max_val, default):
            """
            @param name: Name of argument
            @param desc: Command description
            @param bits: Number of bits in argument
            @param type: COSMOS type for argument
            @param types: Contains enum data if is an enum
            @param min_val: Minimum value for argument
            @param max_val: Maximum value for argument
            @param default: Default value for argument
            """
            self.name = name.upper()
            self.desc = desc
            self.bits = bits
            self.type = type
            self.types = types
            self.min_val = min_val
            self.max_val = max_val
            self.default = default
            if type == 'STRING':
                self.default = '"' + self.default + '"'
            self.neg_offset = False
            self.bit_offset = 0
    
        def add_neg_offset_fields(self, bit_offset):
            """
            Sets flag representing whether there is an offset attached to field
            and adds a negative offset
            @param bit_offset: Number of bits from end of packet
            """
            self.bit_offset = bit_offset
            self.neg_offset = True
    
    def __init__(self, comp_name, comp_type, source, name, opcode, comment, mnemonic, priority, sync, full):
        """
        @param comp_name: Name of command's component
        @param comp_type: Type of command's component
        @param source: XML source file of command
        @param name: Command name
        @param opcode: Opcode of command
        @param comment: Comment attached to command
        @param mnemonic: XML attribute "mnemonic" found within XML source file
        @param priority: XML attribute "priority" found within XML source file
        @param sync: XML attribute "sync" found within XML source file
        @param full: XML attribute "full" found within XML source file
        """
        super(CosmosCommand, self).__init__(comp_name, comp_type, source)
        self.opcode = opcode
        self.cmd_name = name
        self.cmd_desc = comment
        self.mnemonic = mnemonic
        self.priority = priority
        self.sync = sync
        self.full = full
        self.cmd_items = []
        
    def add_item(self, name, type, comment, bits, enum_name, enum, neg_offset):
        """
        Adds an item to the command packet
        @param name: Name of item
        @param type: Fprime version of argument data type (U16 as opposed to COSMOS's 16 UINT)
        @param comment: Description for item
        @param bits: Number of bits in item
        @param enum_name: Name of enum
        @param enum: Tuple with enum data
        @param neg_offset: Contains an offset from back of packet
        """
        # Add an item to the command packet corresponding to the length of the following string item
        if type == 'string':
            len_item = self.CommandItem(name + "_length", "Length of String Arg", 16, "UINT", [], CosmosUtil.MIN_DICT["U16"], CosmosUtil.MAX_DICT["U16"], CosmosUtil.DEFAULT_DICT["U16"])
            self.cmd_items.append(len_item)
        
        cosmos_type = CosmosUtil.TYPE_DICT[type]
        value_type = (cosmos_type[1] if not (cosmos_type[1] == "ENUM" or cosmos_type[1] == "BOOLEAN") else cosmos_type[2])
        
        # Handle enum
        cmd_enum_types = []
        count = 0
        if not enum == None:
            num = 0
            for item in enum[1]:
                if item[1] == None:
                    cmd_enum_types.append((item[0], num))
                else:
                    cmd_enum_types.append((item[0], int(item[1])))
                num += 1
        types = cmd_enum_types
        
        min_val = CosmosUtil.MIN_DICT[type]
        max_val = CosmosUtil.MAX_DICT[type]
        default = CosmosUtil.DEFAULT_DICT[type]
        
        # Create item instance
        if neg_offset:
            item = self.CommandItem(name, comment, bits, value_type, types, min_val, max_val, default)
            item.add_neg_offset_fields(0)
        else:
            item = self.CommandItem(name, comment, bits, value_type, types, min_val, max_val, default)
        self.cmd_items.append(item)
        
    def update_neg_offset(self):
        """
        Called when there are arguments after a string,
        determines their offset from the back of the packet.
        Only called when there is a single string 
        (multi-strings not supported by COSMOS commands)
        """
        # Find location of the only string argument
        reverse = False
        for arg in self.cmd_items:
            if arg.type == 'STRING':
                reverse = True
                break
        
        count = 0
        if reverse:
            for item in reversed(self.cmd_items):
                if item.type == 'STRING':
                    break
                count += item.bits
                item.bit_offset = count * -1
                
    def get_cmd_items(self):
        """
        List of items in packet
        """
        return self.cmd_items
    def get_opcode(self):
        """
        Opcode
        """
        return self.opcode
    def get_cmd_name(self):
        """
        Command name
        """
        return self.cmd_name
    def get_cmd_desc(self):
        """
        Command description
        """
        return self.cmd_desc
    def get_mnemonic(self):
        """
        XML attribute "mnemonic" found within XML source file
        """
        return self.mnemonic
    def get_priority(self):
        """
        XML attribute "priority" found within XML source file
        """
        return self.priority
    def get_sync(self):
        """
        XML attribute "sync" found within XML source file
        """
        return self.sync
    def get_full(self):
        """
        XML attribute "full" found within XML source file
        """
        return self.full

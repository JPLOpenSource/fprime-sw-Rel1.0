#!/bin/env python
#===============================================================================
# NAME: CosmosTopParser.py
#
# DESCRIPTION: This class parses a topology file within its parse_topology()
# method and saves the channels, events, and commands to list-instance-variables.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from utils.cosmos.models import CosmosCommand
from utils.cosmos.models import CosmosChannel
from utils.cosmos.models import CosmosEvent

class CosmosTopParser():
    """
    This class takes an XML topology parser that has parsed the topology XML files
    and instantiates CosmosChannels, CosmosEvents, and CosmosCommands from the data
    in the topology parser.
    """
    
    def __init__(self):
        """
        Init
        """
        self.channels = []
        self.events = []
        self.commands = []
        
    def get_bits_from_type(self, type):
        """
        @param type: Fprime type
        @return: Number of bits in given Fprime type
        """
        if type == 'F32':
            return 32
        elif type == 'F64':
            return 64
        elif type == 'U8':
            return 8
        elif type == 'U16':
            return 16
        elif type == 'U32':
            return 32
        elif type == 'U64':
            return 64
        elif type == 'I8':
            return 8
        elif type == 'I16':
            return 16
        elif type == 'I32':
            return 32
        elif type == 'I64':
            return 64
        elif type == 'bool':
            return 16
        elif type == 'string':
            return 0
        elif type == 'ENUM':
            return 32
        else:
            print "UNSUPPOPRTED DATA TYPE IN CosmosTopParser.py"
                
    def parse_topology(self, topology, overwrite = True):
        """
        Takes a topology XML file and puts all channel, event, and command
        data into CosmosChannel, CosmosEvent, and CosmosCommand class instances
        for easier matching with cheetah template arguments in writer classes
        @param topology: XML topology parser
        @param overwrite: Flag whether to overwrite channels, events, and commands lists
        """
        if overwrite:
            self.channels = []
            self.events = []
            self.commands = []
        
        
        for inst in topology.get_instances():
            comp_name = inst.get_name()
            comp_type = inst.get_type()
            base_id = inst.get_base_id()
            if '0x' in base_id:
                base_id = int(base_id, 16)
            else:
                base_id = int(base_id)
            comp_parser = inst.get_comp_xml()
            #
            # Parse command data here...
            #
            if 'get_commands' in dir(comp_parser):
                cmds = comp_parser.get_commands()
                for cmd in cmds:
                    opcode = cmd.get_opcodes()[0]
                    if '0x' in opcode:
                        opcode = int(opcode, 16)
                    else:
                        opcode = int(opcode)
                    opcode += base_id
                    n = cmd.get_mnemonic()
                    c = cmd.get_comment()
                    m = cmd.get_mnemonic()
                    p = cmd.get_priority()
                    s = cmd.get_sync()
                    f = cmd.get_full()
                    source = comp_parser.get_xml_filename()
                    cosmos_cmd = CosmosCommand.CosmosCommand(comp_name, comp_type, source, n, opcode, c, m, p, s, f)
                    
                    # Count strings to see if 2 (if so needs block argument)
                    string_count = 0
                    args = cmd.get_args()
                    for arg in args:
                        t = arg.get_type()
                        if t == 'string':
                            string_count += 1
                    
                    use_block = False
                    if string_count >= 2:
                        use_block = True
                    #
                    # Parse command arg data here...
                    #
                    num = 0
                    flip_bits = False
                    for arg in args:
                        n = arg.get_name()
                        t = arg.get_type()
                        c = arg.get_comment()
                        # s = arg.get_size() Not currently used in template file
                        enum_name = "None"
                        if type(t) is type(tuple()):
                            enum = t
                            enum_name = t[0][1]
                            t = t[0][0]
                        num += 1
                        bits = self.get_bits_from_type(t)
                        #
                        # Parse command enum here
                        #
                        if t == 'ENUM':
                            num2 = 0
                            for item in enum[1]:
                                if item[1] == None:
                                    pass
                                else:
                                    num2 = int(item[1])
                                num2 += 1
                        
                        neg_offset = False       
                        if flip_bits:
                            neg_offset = 'NEG_OFFSET'
                            
                        if t == 'string':
                            flip_bits = True
                        
                        if not use_block:        
                            cosmos_cmd.add_item(n, t, c, bits, enum_name, enum, neg_offset)
                        else:
                            print "ERROR: multi-string commands not supported in COSMOS"
                    if flip_bits:
                        cosmos_cmd.update_neg_offset()
                    self.commands.append(cosmos_cmd)       
            #
            # Parse event data here...
            #
            if "get_events" in dir(comp_parser):
                evrs = comp_parser.get_events()
                for evr in evrs:
                    evr_id =evr.get_ids()[0]
                    if '0x' in evr_id:
                        evr_id = int(evr_id, 16)
                    else:
                        evr_id = int(evr_id)
                    evr_id += base_id
                    n = evr.get_name()
                    comment = evr.get_comment()
                    s = evr.get_severity()
                    f = evr.get_format_string()
                    source = comp_parser.get_xml_filename()
                    cosmos_evr = CosmosEvent.CosmosEvent(comp_name, comp_type, source, n, evr_id, comment, s, f)
                    
                    # Count strings to see if 2 (if so needs block)
                    string_count = 0
                    args = evr.get_args()
                    for arg in args:
                        t = arg.get_type()
                        if t == 'string':
                            string_count += 1
                    
                    use_block = False
                    if string_count >= 2:
                        use_block = True
                        cosmos_evr.add_block()
                    #
                    # Parse event enums here...
                    #
                    flip_bits = False
                    bit_count = 0
                    for arg in args:
                        n = arg.get_name()
                        t = arg.get_type()
                        s = arg.get_size()
                        c = arg.get_comment()
                        enum_name = "None"
                        enum = None
                        if type(t) is type(tuple()):
                            enum = t
                            enum_name = t[0][1]
                            t = t[0][0]

                        # Handle argument type
                        bits = self.get_bits_from_type(t)
                        bit_offset = 0
                        evr_type = 'NORMAL'
                        if use_block:
                            evr_type = 'DERIVED'
                        elif flip_bits:
                            evr_type = 'NEG_OFFSET'
                            
                        if t == 'string':
                            flip_bits = True
                            
                        cosmos_evr.add_item(n, c, bits, t, enum_name, enum, evr_type, bit_offset)
                    if flip_bits:
                        cosmos_evr.update_neg_offset()
                    if use_block:
                        cosmos_evr.update_template_strings()
                    self.events.append(cosmos_evr)
            #
            # Parse channel data here...
            #
            if "get_channels" in dir(comp_parser):
                channels = comp_parser.get_channels()
                for ch in channels:
                    ch_id = ch.get_ids()[0]
                    if '0x' in ch_id:
                        ch_id = int(ch_id, 16)
                    else:
                        ch_id = int(ch_id)
                    ch_id += base_id
                    n     = ch.get_name()
                    t     = ch.get_type()
                    enum_name = "None"
                    enum = None
                    if type(t) is type(tuple()):
                        enum = t
                        enum_name = t[0][1]
                        t = t[0][0]
                    c = ch.get_comment()
                    source = comp_parser.get_xml_filename()
                    cosmos_ch = CosmosChannel.CosmosChannel(comp_name, comp_type, source, ch_id, n, c)
                    cosmos_ch.set_arg(t, enum_name, enum, ch.get_format_string())
                    self.channels.append(cosmos_ch)
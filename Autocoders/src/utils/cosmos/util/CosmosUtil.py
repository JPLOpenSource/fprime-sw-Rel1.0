#!/bin/env python
#===============================================================================
# NAME: DeploymentUtil.py
#
# DESCRIPTION: This class contains all constant data fields which may need altering if
# Fprime's packet header items change or if the user wants to change port numbers
# for read and writer.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

"""
This class contains static data and methods that should be changed for each individual deployment
including header sizes, port numbers, etc.
"""

#
# DEPLOYMENT VARIABLES
#
    
# Total number of bits in the Event header items (Alter the file _ref_tlm_evr_hdr.txt in the events directory as well)
EVR_HEADER_SIZE_BITS = 256
    
# Endianness for commands and telemetry
CMD_TLM_ENDIANNESS = "BIG_ENDIAN"
    
# SERVER VARIABLES
WRITE_PORT = 5000
READ_PORT = 5000
READ_TIMEOUT = 10
WRITE_TIMEOUT = 10
PROTOCOL_NAME_W = "RefProtocol"
PROTOCOL_NAME_R = "RefProtocol"
LEN_BIT_OFFSET_W = 32
LEN_BIT_OFFSET_R = 72
LEN_BIT_SIZE_W = 32
LEN_BIT_SIZE_R = 32
LEN_VAL_OFFSET_W = 8
LEN_VAL_OFFSET_R = 13
BYTES_PER_COUNT_W = 1
BYTES_PER_COUNT_R = 1
ENDIANNESS_W = "BIG_ENDIAN"
ENDIANNESS_R = "BIG_ENDIAN"
DISCARD_LEADING_W = 0
DISCARD_LEADING_R = 0
SYNC_W = "5A5A5A5A"
SYNC_R = "413541352047554920"
HAS_MAX_LENGTH_W = "nil"
HAS_MAX_LENGTH_R = "nil"
FILL_LS_W = "true"
FILL_LS_R = "true"
    
#
# COSMOS-SPECIFIC VALUES
#
    
def get_bits_from_type(type):
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
    
    
def fill_cosmos_dicts(type_dict,min_dict, max_dict, default_dict):
    """
    Initializes the FPrime type -> COSMOS type dict type_dicts,
    and each of the min, max, and default value dicts (STORED IN BaseCosmosObject)
    @param type_dict: Number of bits and name of COSMOS for Fprime types
    @param min_dict: Minimum values for each Fprime type
    @param max_dict: Maximum values for each Fprime type
    @param default_dict: Default values for each Fprime type
    """
    type_dict["F32"] = (32, "FLOAT")
    type_dict["F64"] = (64, "FLOAT")
    type_dict["U8"] = (8, "UINT")
    type_dict["U16"] = (16, "UINT")
    type_dict["U32"] = (32, "UINT")
    type_dict["U64"] = (64, "UINT")
    type_dict["I8"] = (8, "INT")
    type_dict["I16"] = (16, "INT")
    type_dict["I32"] = (32, "INT")
    type_dict["I64"] = (64, "INT")
    type_dict["bool"] = (16, "BOOLEAN", "UINT")
    type_dict["string"] = (0, "STRING")
    type_dict["ENUM"] = (32, "ENUM", "UINT")
        
    min_dict["F32"] = -10000.0
    min_dict["F64"] = -100000.0
    min_dict["U8"] = 0
    min_dict["U16"] = 0
    min_dict["U32"] = 0
    min_dict["U64"] = 0
    min_dict["I8"] = -128
    min_dict["I16"] = -1000 #-32768
    min_dict["I32"] = -10000 #-2147483648
    min_dict["I64"] = -10000#-9223372036854775808
    min_dict["bool"] = 0
    min_dict["string"] = ""
    min_dict["ENUM"] = min_dict["U32"]
        
    max_dict["F32"] = 10000.0
    max_dict["F64"] = 100000.0
    max_dict["U8"] = 255
    max_dict["U16"] = 1000  #65535
    max_dict["U32"] = 10000 #4294967295
    max_dict["U64"] = 10000#18446744073709551615
    max_dict["I8"] = 127
    max_dict["I16"] = 32767
    max_dict["I32"] = 10000 #2147483647
    max_dict["I64"] = 10000 #9223372036854775807
    max_dict["bool"] = 1
    max_dict["string"] = "" # Dont use this, should be set elsewhere to value from topology
    max_dict["ENUM"] = max_dict["U32"]
        
    default_dict["F32"] = 0.0
    default_dict["F64"] = 0.0
    default_dict["U8"] = 0
    default_dict["U16"] = 0
    default_dict["U32"] = 0
    default_dict["U64"] = 0
    default_dict["I8"] = 0
    default_dict["I16"] = 0
    default_dict["I32"] = 0
    default_dict["I64"] = 0
    default_dict["bool"] = False
    default_dict["string"] = "String" # Dont use this, should be set elsewhere to value from topology
    default_dict["ENUM"] = 0    

#
# EVENTS
#
        
def update_template_strings(evr_items):
    """
    Calculates the template string for each item in packet with multiple strings
    
    Template String Example For Third Argument(caps are real strings,
    lowercase w/ underscores are variable integer values):
    "bits_from_start_of_packet START arg1_bits arg1_data_type arg2_bits
    arg2_data_type arg3_bits arg3_data_type"
    """

    total_pre_item_bits = EVR_HEADER_SIZE_BITS
    aggregate = str(total_pre_item_bits) + " START"
    for item in evr_items:
        if not item.block:
            item.template_string = aggregate + " " + str(item.bits) + " " + item.type
            aggregate = item.template_string

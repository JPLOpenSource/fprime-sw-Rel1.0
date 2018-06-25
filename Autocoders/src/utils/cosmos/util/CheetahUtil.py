#!/bin/env python
#===============================================================================
# NAME: CheetahUtil.py
#
# DESCRIPTION: This class contains the methods that format data into the ways
# which Cheetah templates desire it.
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

import CosmosUtil

"""
This class contains static data and methods should be altered in order to change the behavior of
Cheetah templates.
"""
#
# COSMOS OUTPUT STYLING
#
DATE = datetime.datetime.now().strftime("%A, %d, %B, %Y")
USER = os.environ['USER']

#
# CHANNELS
#
def convert_ch_limits(limits):
    """
    Converts the Fprime limits tuple into a Cosmos limits tuple, because they have different orderings
    and different necessary data.  Orange limits are not supported in COSMOS
    Fprime limits: (low_red, low_orange, low_yellow, high_yellow, high_orange, high_red)
    Cosmos limits: (persistence, limits_state, red_low, yellow_low, yellow_high, red_high)
    @param limits: tuple containing Fprime limits
    @return: A list containing 1 Cosmos limits tuple: list is for easy Cheetah iteration
    """
    if not limits[0] and not limits[1] and not limits[2] and not limits[3] and not limits[4] and not limits[5]:
        return []
    print limits
    lr = limits[0]
    ly = limits[2]
    hy = limits[3]
    hr = limits[5]
    
    # Cosmos requires all limits to be set, so set to number out of range
    if not lr:
        lr = CosmosUtil.MIN_DICT['I64']
    if not ly:
        ly = CosmosUtil.MIN_DICT['I64']
    if not hr:
        hr = CosmosUtil.MAX_DICT['I64']
    if not hy:
        hy = CosmosUtil.MAX_DICT['I64']
    
    return [(CosmosUtil.LIMIT_PERSISTENCE, CosmosUtil.LIMIT_LIMITS_STATE, lr, ly, hy, hr)]
    
#
# COMMANDS
#
def cmd_convert_to_tuple(cmd_item):
    """
    Cheetah templates can't iterate over a list of classes, so
    converts all data into a Cheetah-friendly tuple
    (NAME, DESCRIPTION, ENUM, HAS_BIT_OFFSET, BIT_OFFSET, BITS, TYPE, MIN, MAX, DEFAULT)
    The class CommandItem that this method implicitly uses is located within the CommandItem class 
    """
    return (cmd_item.name, cmd_item.desc, cmd_item.types, cmd_item.neg_offset, cmd_item.bit_offset, cmd_item.bits,
            cmd_item.type, cmd_item.min_val, cmd_item.max_val, cmd_item.default)    
    
def cmd_convert_items_to_cheetah_list(list):
    """
    Cheetah templates can't iterate over a list of classes, so
    converts all data into a Cheetah-friendly list of tuples
    (NAME, DESCRIPTION, ENUM, HAS_BIT_OFFSET, BIT_OFFSET, BITS, TYPE, MIN, MAX, DEFAULT)
    """
    temp = []
        
    for i in list:
        temp.append(cmd_convert_to_tuple(i))
        
    return temp
#
# EVENTS
#

def evr_convert_to_tuple(evr_item):
    """
    Cheetah templates can't iterate over a list of classes, so
    converts all data into a Cheetah-friendly tuple
    (IS_BLOCK, IS_DERIVED, NAME, DESCRIPTION, TEMPLATE_STRING, TYPES, HAS_NEG_OFFSET, NEG_OFFSET, BITS, TYPE)
    The class EventItem that this method implicitly uses is located within the CosmosEvent class 
    """
    return (evr_item.block, evr_item.derived, evr_item.name, evr_item.desc, evr_item.template_string, evr_item.types,
            evr_item.neg_offset, evr_item.bit_offset, evr_item.bits, evr_item.type)    

    
def evr_convert_items_to_cheetah_list(list):
    """
    Cheetah templates can't iterate over a list of classes, so
    converts all data into a Cheetah-friendly list of tuples
    (NAME, DESCRIPTION, ENUM, HAS_BIT_OFFSET, BIT_OFFSET, BITS, TYPE, MIN, MAX, DEFAULT)
    """
    temp = []
        
    for i in list:
        temp.append(evr_convert_to_tuple(i))
        
    return temp

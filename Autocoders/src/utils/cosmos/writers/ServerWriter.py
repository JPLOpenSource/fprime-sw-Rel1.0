#!/bin/env python
#===============================================================================
# NAME: ServerWriter.py
#
# DESCRIPTION: This writer generates the cmd_tlm_server.txt file in COSMOS/config/targets
# /DEPLOYMENT_NAME/ directory that contains configuration data for the cosmos
# target interface.
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
import logging

from utils.cosmos.writers import AbstractCosmosWriter

from utils.cosmos.templates import Cosmos_Server

class ServerWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This class generates the server definition file in
    cosmos_directory/COSMOS/config/targets/deployment_name.upper()/
    """
    
    def __init__(self, parser, deployment_name, cosmos_directory):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        """
        super(ServerWriter, self).__init__(parser, deployment_name, cosmos_directory)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Open file
        fl = open(self.destination + "cmd_tlm_server.txt", "w")
        print "Server Interface File Created"
        
        # Initialize and fill cheetah template
        cs = Cosmos_Server.Cosmos_Server()
        
        cs.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        cs.user = os.environ['USER']
        cs.target_name = self.deployment_name.upper()
        cs.write_port = 5000
        cs.read_port = 5000
        cs.read_timeout = 10
        cs.write_timeout = 10
        cs.protocol_name_w = "RefProtocol"
        cs.protocol_name_r = "RefProtocol"
        cs.len_bit_offset_w = 32
        cs.len_bit_offset_r = 72
        cs.len_bit_size_w = 32
        cs.len_bit_size_r = 32
        cs.len_val_offset_w = 8
        cs.len_val_offset_r = 13
        cs.bytes_per_count_w = 1
        cs.bytes_per_count_r = 1 
        cs.endianness_w = "BIG_ENDIAN"
        cs.endianness_r = "BIG_ENDIAN"
        cs.discard_leading_w = 0
        cs.discard_leading_r = 0
        cs.sync_w = "5A5A5A5A"
        cs.sync_r = "413541352047554920"
        cs.has_max_length_w = "nil"
        cs.has_max_length_r = "nil"
        cs.fill_ls_w = "true"
        cs.fill_ls_r = "true"
                    
        msg = cs.__str__()
                    
        fl.writelines(msg)
        fl.close()

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

from utils.cosmos.writers import AbstractCosmosWriter

from utils.cosmos.util import CheetahUtil
from utils.cosmos.util import CosmosUtil

from utils.cosmos.templates import Server

class ServerWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This class generates the server definition file in
    cosmos_directory/config/targets/deployment_name.upper()/
    """
    
    def __init__(self, cmd_tlm_data, deployment_name, cosmos_directory):
        """
        @param cmd_tlm_data: Tuple containing lists channels [0], commands [1], and events [2]
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        """
        super(ServerWriter, self).__init__(cmd_tlm_data, deployment_name, cosmos_directory)
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/config/targets/" + deployment_name.upper() + "/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Open file
        fl = open(self.destination + "cmd_tlm_server.txt", "w")
        if CosmosUtil.VERBOSE:
            print "Server Interface File Created"
        
        # Initialize and fill cheetah template
        cs = Server.Server()
        
        cs.date = CheetahUtil.DATE
        cs.user = CheetahUtil.USER
        cs.target_name = self.deployment_name.upper()
        cs.write_port = CosmosUtil.WRITE_PORT
        cs.read_port = CosmosUtil.READ_PORT
        cs.read_timeout = CosmosUtil.READ_TIMEOUT
        cs.write_timeout = CosmosUtil.WRITE_TIMEOUT
        cs.protocol_name_w = CosmosUtil.PROTOCOL_NAME_W
        cs.protocol_name_r = CosmosUtil.PROTOCOL_NAME_R
        cs.len_bit_offset_w = CosmosUtil.LEN_BIT_OFFSET_W
        cs.len_bit_offset_r = CosmosUtil.LEN_BIT_OFFSET_R
        cs.len_bit_size_w = CosmosUtil.LEN_BIT_SIZE_W
        cs.len_bit_size_r = CosmosUtil.LEN_BIT_SIZE_R
        cs.len_val_offset_w = CosmosUtil.LEN_VAL_OFFSET_W
        cs.len_val_offset_r = CosmosUtil.LEN_VAL_OFFSET_R
        cs.bytes_per_count_w = CosmosUtil.BYTES_PER_COUNT_W
        cs.bytes_per_count_r = CosmosUtil.BYTES_PER_COUNT_R
        cs.endianness_w = CosmosUtil.ENDIANNESS_W
        cs.endianness_r = CosmosUtil.ENDIANNESS_R
        cs.discard_leading_w = CosmosUtil.DISCARD_LEADING_W
        cs.discard_leading_r = CosmosUtil.DISCARD_LEADING_R
        cs.sync_w = CosmosUtil.SYNC_W
        cs.sync_r = CosmosUtil.SYNC_R
        cs.has_max_length_w = CosmosUtil.HAS_MAX_LENGTH_W
        cs.has_max_length_r = CosmosUtil.HAS_MAX_LENGTH_R
        cs.fill_ls_w = CosmosUtil.FILL_LS_W
        cs.fill_ls_r = CosmosUtil.FILL_LS_R
                    
        msg = cs.__str__()
                    
        fl.writelines(msg)
        fl.close()

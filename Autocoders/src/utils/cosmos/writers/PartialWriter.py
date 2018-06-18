#!/bin/env python
#===============================================================================
# NAME: PartialWriter.py
#
# DESCRIPTION: This writer generates the partial files (start with _) in 
# the COSMOS/config/targets/DEPLOYMENT_NAME/cmd_tlm/* directories that contain 
# configuration data for each channel, command, and event as well as the partial
# file in the COSMOS/config/targets/DEPLOYMENT_NAME/tools/data_viewer/ directory.
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
import re

from utils.cosmos.writers import AbstractCosmosWriter

from utils.cosmos.templates import Channel_Partial
from utils.cosmos.templates import Command_Partial
from utils.cosmos.templates import Event_Partial
from utils.cosmos.templates import Data_Viewer_Partial

class PartialWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This class generates each of the files that the user must input their own data into:
    _tlm_chn_hdr.txt: Channel header file that contains all shared channel definition fields
    _cmds_hdr.txt: Command header file that contains all shared command definition fields
    _tlm_evr_hdr.txt: Event header file that contains all shared event definition fields
    _user_dataviewers.txt: Contains all user/inputted data viewer fields
    """
    
    def __init__(self, parser, deployment_name, cosmos_directory):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        """
        super(PartialWriter, self).__init__(parser, deployment_name, cosmos_directory)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destinations = {
            cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/channels/_" + deployment_name.lower() + "_tlm_chn_hdr.txt": Channel_Partial.Channel_Partial(),
            cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/commands/_" + deployment_name.lower() + "_cmds_hdr.txt": Command_Partial.Command_Partial(),
            cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/events/_" + deployment_name.lower() + "_tlm_evr_hdr.txt": Event_Partial.Event_Partial(),
            cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/tools/data_viewer/_user_dataviewers.txt": Data_Viewer_Partial.Data_Viewer_Partial()
            }
        
                    
    def write(self):
        """
        Generates the file
        """
        for destination in self.destinations.keys():
            if not os.path.exists(destination):
                fl = open(destination, "w")
                
                # All partial Cheetah template files do not contain variables, so can just be spit back out
                tmpl = self.destinations[destination]
                
                msg = tmpl.__str__()
                
                fl.writelines(msg)
                fl.close()
                
                print destination + " Created"
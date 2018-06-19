#!/bin/env python
#===============================================================================
# NAME: ConfigTlmViewerWriter.py
#
# DESCRIPTION: This writer generates the tlm_viewer.txt in COSMOS/config/
# tools/tlm_viewer/ directory that defines the existing targets for the 
# tlm_viewer application
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

from utils.cosmos.writers import BaseConfigWriter

from utils.cosmos.templates import Tlm_Viewer_Config

class ConfigTlmViewerWriter(BaseConfigWriter.BaseConfigWriter):
    """
    This class generates the tlm viewer config file in
    cosmos_directory/COSMOS/config/tools/tlm_viewer/
    """
    
    def __init__(self, parser, deployment_name, cosmos_directory, old_definition=None):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        @param old_definition: COSMOS target name that you want to remove
        """
        super(ConfigTlmViewerWriter, self).__init__(parser, deployment_name, cosmos_directory, old_definition)
        self.repeated_names = {}
        self.token = "AUTO_TARGET"
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/tools/tlm_viewer/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Add target to list of lines that will always be written
        ignored_lines = []
        if self.deployment_name and not self.deployment_name == "":
            ignored_lines.append(self.token + " " + self.deployment_name.upper())
        
        # Open file for reading if exists already and parse all old targets
        names = []
        fl_loc = self.destination + 'tlm_viewer.txt'
        if os.path.isfile(fl_loc):
            names = self.read_for_token(fl_loc, self.token, ignored_lines)
            print "Tlm Viewer Tool Config Altered"
        else:
            print "Tlm Viewer Tool Config Created"
                
        for line in ignored_lines:
            names.append(line.split(" ")[1])
        
        # Open file
        fl = open(fl_loc, "w")
        
        # Initialize and fill Cheetah template 
        tv = Tlm_Viewer_Config.Tlm_Viewer_Config()
         
        tv.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        tv.user = os.environ['USER']
        tv.names = names
                     
        msg = tv.__str__()
                     
        fl.writelines(msg)
        fl.close()

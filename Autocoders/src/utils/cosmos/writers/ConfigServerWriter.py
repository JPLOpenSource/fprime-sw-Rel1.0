#!/bin/env python
#===============================================================================
# NAME: ConfigServerWriter.py
#
# DESCRIPTION: This writer generates the cmd_tlm_server.txt in COSMOS/config/
# tools/cmd_tlm_server directory that defines the existing targets for the cmd_tlm_server
# application
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

from utils.cosmos.templates import Server_Config

class ConfigServerWriter(BaseConfigWriter.BaseConfigWriter):
    """
    This class generates the data viewer config file in
    cosmos_directory/COSMOS/config/tools/data_viewer/
    """
    
    def __init__(self, parser, deployment_name, cosmos_directory, old_definition=None):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        @param old_definition: COSMOS target name that you want to remove
        """
        super(ConfigServerWriter, self).__init__(parser, deployment_name, cosmos_directory, old_definition)
        self.repeated_names = {}
        self.token = "INTERFACE_TARGET"
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/tools/cmd_tlm_server/"
        
                    
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
        fl_loc = self.destination + 'cmd_tlm_server.txt'
        if os.path.isfile(fl_loc):
            names = self.read_for_token(fl_loc, self.token, ignored_lines)
            print "Cmd Tlm Server Config Altered"
        else:
            print "Cmd Tlm Server Config Created"
                
        for line in ignored_lines:
            names.append(line.split(" ")[1])
        
        # Open file
        fl = open(fl_loc, "w")
         
        # Initialize and fill Cheetah template
        sc = Server_Config.Server_Config()
         
        sc.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        sc.user = os.environ['USER']
        sc.names = names
                     
        msg = sc.__str__()
                     
        fl.writelines(msg)
        fl.close()

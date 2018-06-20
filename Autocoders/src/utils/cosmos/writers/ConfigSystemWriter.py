#!/bin/env python
#===============================================================================
# NAME: ConfigConfig_SystemWriter.py
#
# DESCRIPTION: This writer generates the system.txt in COSMOS/config/
# system/ folder that defines the existing targets for the entire cosmos
# system
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

from utils.cosmos.writers import BaseConfigWriter

from utils.cosmos.templates import Config_System

class ConfigSystemWriter(BaseConfigWriter.BaseConfigWriter):
    """
    This class generates the system config file in
    cosmos_directory/config/system/
    """
    
    def __init__(self, cmd_tlm_data, deployment_name, cosmos_directory, old_definition=None):
        """
        @param cmd_tlm_data: Tuple containing lists channels [0], commands [1], and events [2]
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        @param old_definition: COSMOS target name that you want to remove
        """
        super(ConfigSystemWriter, self).__init__(cmd_tlm_data, deployment_name, cosmos_directory, old_definition)
        self.token = "DECLARE_TARGET"
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/config/system/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Add target to list of lines that will always be written
        ignored_lines = []
        ignored_lines.append((self.token + " SYSTEM"))
        if self.deployment_name and not self.deployment_name == "":
            ignored_lines.append(self.token + " " + self.deployment_name.upper())        
        
        # Open file for reading if exists already and parse all old targets
        names = []
        fl_loc = self.destination + 'system.txt'
        if os.path.isfile(fl_loc):
            names = self.read_for_token(fl_loc, self.token, ignored_lines)
            print "Config_System.txt Altered"
        else:
            print "Config_System.txt Created"
            
        for line in ignored_lines:
            names.append(line.split(" ")[1])
        
        # Open file
        fl = open(fl_loc, "w")
        
        # Initialize and fill Cheetah template 
        s = Config_System.Config_System()
         
        s.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        s.user = os.environ['USER']
        s.names = names
                     
        msg = s.__str__()
                     
        fl.writelines(msg)
        fl.close()

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

from utils.cosmos.writers import AbstractConfigWriter

from utils.cosmos.templates import Tlm_Viewer_Config

class ConfigTlmViewerWriter(AbstractConfigWriter.AbstractConfigWriter):
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
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/tools/tlm_viewer/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Add target to list of lines that will always be written
        user_definitions = []
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("AUTO_TARGET " + self.deployment_name.upper())
        
        # Open file for reading if exists already and parse all old targets
        names = []
        if os.path.isfile(self.destination + 'tlm_viewer.txt'):
            fl = open(self.destination + "tlm_viewer.txt", "r")
            
            lines = re.findall(".*AUTO_TARGET.*", fl.read())
            bad_lines = []
            for line in lines:
                line = line.strip()
                if line[0] == '#' or not line[:11] == 'AUTO_TARGET' or " ".join(line.strip().split(" ")[0:2]) in user_definitions:
                    bad_lines.append(line)
                    
            for line in bad_lines:
                lines.remove(line)
                    
            for line in lines:
                line = line.split(" ")
                if not self.old_definition or not line[1] == self.old_definition:
                    names.append(line[1])
                            
            fl.close()
            print "Tlm Viewer Tool Config Altered"
        else:
            print "Tlm Viewer Tool Config Created"
                
        for line in user_definitions:
            names.append(line.split(" ")[1])
        
        # Open file
        fl = open(self.destination + "tlm_viewer.txt", "w")
        
        # Initialize and fill Cheetah template 
        tv = Tlm_Viewer_Config.Tlm_Viewer_Config()
         
        tv.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        tv.user = os.environ['USER']
        tv.names = names
                     
        msg = tv.__str__()
                     
        fl.writelines(msg)
        fl.close()

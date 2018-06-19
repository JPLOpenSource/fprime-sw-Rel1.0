#!/bin/env python
#===============================================================================
# NAME: ConfigDataViewerWriter.py
#
# DESCRIPTION: This writer generates the data_viewer.txt in COSMOS/config/
# tools/data_viewer/ directory that defines the existing targets for the data_viewer
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

from utils.cosmos.writers import AbstractConfigWriter

from utils.cosmos.templates import Data_Viewer_Config

class ConfigDataViewerWriter(AbstractConfigWriter.AbstractConfigWriter):
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
        super(ConfigDataViewerWriter, self).__init__(parser, deployment_name, cosmos_directory, old_definition)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/tools/data_viewer/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Add target to list of lines that will always be written
        user_definitions = []
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("TARGET_COMPONENT " + self.deployment_name.upper())
        
        # Open file for reading if exists already and parse all old targets
        names = []
        if os.path.isfile(self.destination + 'data_viewer.txt'):
            file_exists = True
            fl = open(self.destination + "data_viewer.txt", "r")
            
            # lines = re.findall(".*TARGET_COMPONENT.*", fl.read())
            bad_lines = []
            # Critical section is the area that we want to append to / delete lines from, post-critical and pre-critical are just appended
            reached_critical_section = False
            for line in fl.readlines():
                line = line.strip()
                if line[0] == '#' or not line[:16] == 'TARGET_COMPONENT' or " ".join(line.strip().split(" ")[0:2]) in user_definitions:
                    bad_lines.append(line)
                    
            for line in bad_lines:
                lines.remove(line)
                    
            for line in lines:
                line = line.split(" ")
                if not self.old_definition or not line[1] == self.old_definition:
                    names.append(line[1])
                            
            fl.close()
            print "Data Viewer Tool Config Altered"
        else:
            print "Data Viewer Tool Config Created"
            
        for line in user_definitions:
            names.append(line.split(" ")[1])
        
        # Open file
        fl = open(self.destination + "data_viewer.txt", "w")
         
        # Initialize and fill Cheetah template
        dv = Data_Viewer_Config.Data_Viewer_Config()
         
        dv.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        dv.user = os.environ['USER']
        dv.names = names
                     
        msg = dv.__str__()
                     
        fl.writelines(msg)
        fl.close()

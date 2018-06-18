#!/bin/env python
#===============================================================================
# NAME: ConfigSystemWriter.py
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
import re

from utils.cosmos.writers import AbstractConfigWriter

from utils.cosmos.templates import System

class ConfigSystemWriter(AbstractConfigWriter.AbstractConfigWriter):
    """
    This class generates the system config file in
    cosmos_directory/COSMOS/config/system/
    """
    
    def __init__(self, parser, deployment_name, cosmos_directory, old_definition=None):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        @param old_definition: COSMOS target name that you want to remove
        """
        super(ConfigSystemWriter, self).__init__(parser, deployment_name, cosmos_directory, old_definition)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/system/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Add target to list of lines that will always be written
        user_definitions = ["DECLARE_TARGET SYSTEM"]
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("DECLARE_TARGET " + self.deployment_name.upper())        
        
        # Open file for reading if exists already and parse all old targets    
        names = []
        if os.path.isfile(self.destination + 'system.txt'):
            fl = open(self.destination + "system.txt", "r")
            
            lines = re.findall(".*DECLARE_TARGET.*", fl.read())
            
            bad_lines = []
            for line in lines:
                line = line.strip()
                if line[0] == '#' or not line[:14] == 'DECLARE_TARGET' or " ".join(line.strip().split(" ")[0:2]) in user_definitions:
                    bad_lines.append(line)
                    
            for line in bad_lines:
                lines.remove(line)
                    
            for line in lines:
                line = line.split(" ")
                if not self.old_definition or not line[1] == self.old_definition:
                    names.append(line[1])
                
            fl.close()
            print "System.txt Altered"
        else:
            print "System.txt Created"
            
        for line in user_definitions:
            names.append(line.split(" ")[1])
        
#         # Open file
        fl = open(self.destination + "system.txt", "w")
        
        # Initialize and fill Cheetah template 
        s = System.System()
         
        s.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        s.user = os.environ['USER']
        s.names = names
                     
        msg = s.__str__()
                     
        fl.writelines(msg)
        fl.close()

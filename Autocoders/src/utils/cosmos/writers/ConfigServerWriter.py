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

from utils.cosmos.writers import AbstractConfigWriter

from utils.cosmos.templates import Server_Config

class ConfigServerWriter(AbstractConfigWriter.AbstractConfigWriter):
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
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/tools/cmd_tlm_server/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Add target to list of lines that will always be written
        user_definitions = []
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("INTERFACE_TARGET " + self.deployment_name.upper())
        
        # Open file for reading if exists already and parse all old targets
        names = []
        if os.path.isfile(self.destination + 'cmd_tlm_server.txt'):
            fl = open(self.destination + "cmd_tlm_server.txt", "r")
            
            lines = re.findall(".*INTERFACE_TARGET.*", fl.read())
            bad_lines = []
            for line in lines:
                print "LINE EXISTS: " + line
                line = line.strip()
                if line[0] == '#' or not line[:16] == 'INTERFACE_TARGET' or " ".join(line.strip().split(" ")[0:2]) in user_definitions:
                    print "LINE IS BAD: " + line + " " + line[:16]
                    bad_lines.append(line)
                    
            for line in bad_lines:
                lines.remove(line)
                    
            for line in lines:
                line = line.split(" ")
                if not self.old_definition or not line[1] == self.old_definition:
                    names.append(line[1])
                            
            fl.close()
            print "Cmd Tlm Server Config Altered"
        else:
            print "Cmd Tlm Server Config Created"
                
        for line in user_definitions:
            names.append(line.split(" ")[1])
        
        # Open file
        fl = open(self.destination + "cmd_tlm_server.txt", "w")
         
        # Initialize and fill Cheetah template
        sc = Server_Config.Server_Config()
         
        sc.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        sc.user = os.environ['USER']
        sc.names = names
                     
        msg = sc.__str__()
                     
        fl.writelines(msg)
        fl.close()

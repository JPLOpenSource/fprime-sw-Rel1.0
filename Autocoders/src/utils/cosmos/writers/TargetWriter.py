#!/bin/env python
#===============================================================================
# NAME: TargetWriter.py
#
# DESCRIPTION: This writer generates the target.txt file in COSMOS/config/targets
# /DEPLOYMENT_NAME/ directory that contains configuration data for the cosmos
# target.
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

from utils.cosmos.templates import Target

class TargetWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This class generates the target definition file in
    cosmos_directory/COSMOS/config/targets/deployment_name.upper()/
    """
    
    def __init__(self, parser, deployment_name, cosmos_directory):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        """
        super(TargetWriter, self).__init__(parser, deployment_name, cosmos_directory)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/"
        
                    
    def write(self):
        """
        Generates the file
        """
        # Open file
        fl = open(self.destination + "target.txt", "w")
        print "target.txt Created"
        
        # Initialize and fill cheetah template 
        t = Target.Target()
         
        t.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        t.user = os.environ['USER']
                     
        msg = t.__str__()
                     
        fl.writelines(msg)
        fl.close()

#!/bin/env python
#===============================================================================
# NAME: CommandWriter.py
#
# DESCRIPTION: This writer generates the command files in the COSMOS/config/targets
# /DEPLOYMENT_NAME/cmd_tlm/commands/ directory that contains configuration data for each
# command.
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

from utils.cosmos.writers import AbstractCosmosWriter

from utils.cosmos.templates import Command

class CommandWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This class generates the command definition files in
    cosmos_directory/COSMOS/config/targets/deployment_name.upper()/cmd_tlm/commands/
    """
    
    def __init__(self, topology, deployment_name, cosmos_directory):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        """
        super(CommandWriter, self).__init__(topology, deployment_name, cosmos_directory)
        self.repeated_names = {}
    
        # Initialize writer-unique file destination location
        self.cosmos_directory = cosmos_directory
        self.destination = cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/commands/"
    
    def write(self):
        """
        Generates the file
        """
        print "Creating Command Files"
        command_templates = {}
        for cmd in self.parser.commands:
            n = cmd.get_cmd_name()
            if n in self.repeated_names.keys():
                # Fix other name pair
                if n in command_templates.keys():
                    command_templates.get(n).cmd_name = self.repeated_names.get(n).get_comp_name() + "_" + n
                    command_templates.update({self.repeated_names.get(n).get_comp_name() + "_" + 
                                        n: command_templates.get(n)})
                    command_templates = self.removekey(command_templates, n)
                n = cmd.get_comp_name() + "_" + n
            self.repeated_names.update({n: cmd})

            # Initialize and fill Cheetah Template
            c = Command.Command()

            c.date = cmd.get_date()
            c.user = cmd.get_user()
            c.source = cmd.get_source()
            c.component_string = cmd.get_component_string()
            c.cmd_name = n
            c.endianness = cmd.get_endianness()
            c.cmd_desc = cmd.get_cmd_desc()
            c.opcode = cmd.get_opcode()
            c.target_caps = self.deployment_name.upper()
            c.target_lower = self.deployment_name.lower()
            c.cmd_items = cmd.get_cmd_items_cosmos()
            c.mnemonic = cmd.get_mnemonic()
            c.priority = cmd.get_priority()
            c.sync = cmd.get_sync()
            c.full = cmd.get_full()

            command_templates.update({n: c})

        # Write files
        for name, c in command_templates.iteritems():
            c.cmd_name = name
            fl = open(self.destination + name.lower() + ".txt", "w")
            print "Command " + name + " Created"
            c.cmd_name = name.upper()
            msg = c.__str__()
                    
            fl.writelines(msg)
            fl.close()

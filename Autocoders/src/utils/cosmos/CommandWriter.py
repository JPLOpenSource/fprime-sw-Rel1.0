
import os
import sys
import time
import datetime
import logging

from utils.cosmos import CosmosWriterAbs

from utils.cosmos.templates import Command
from zmq.utils.jsonapi import priority

PRINT = logging.getLogger('output')

class CommandWriter(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, topology, deployment_name, build_root):
        super(CommandWriter, self).__init__(topology, deployment_name, build_root)
        self.repeated_names = {}
    
        # Initialize writer-unique file destination location
        self.build_root = build_root
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/commands/"
    
    def write(self):
        print "Creating Command Files"
        command_templates = {}
        for cmd in self.parser.commands:
            n = cmd.get_cmd_name()
#             if n in self.repeated_names.keys():
#                 # Fix other name pair
#                 if n in event_templates.keys():
#                     event_templates.get(n).channel_name = self.repeated_names.get(n).get_comp_name() + "_" + n
#                     event_templates.update({self.repeated_names.get(n).get_comp_name() + "_" + 
#                                         n: event_templates.get(n)})
#                     event_templates = self.removekey(event_templates, n)
#                 n = evr.get_comp_name() + "_" + n
            self.repeated_names.update({n: cmd})

            # Initialize Cheetah Template
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
            c.cmd_args = cmd.get_cmd_args_cosmos()
            c.mnemonic = cmd.get_mnemonic()
            c.priority = cmd.get_priority()
            c.sync = cmd.get_sync()
            c.full = cmd.get_full()

            command_templates.update({n: c})

        # Write files
        for name, c in command_templates.iteritems():
            c.cmd_name = name
            fl = open(self.destination + name.lower() + ".txt", "w")
            print "Command " + name + " Created at: " + name.lower() + ".txt"
            c.cmd_name = name.upper()
            msg = c.__str__()
                    
            fl.writelines(msg)
            fl.close()

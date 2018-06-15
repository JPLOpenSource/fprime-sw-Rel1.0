
import os
import sys
import time
import datetime
import logging
import re

from utils.cosmos.writers import CosmosWriterAbs

from utils.cosmos.templates import Channel_Partial
from utils.cosmos.templates import Command_Partial
from utils.cosmos.templates import Event_Partial
from utils.cosmos.templates import Data_Viewer_Partial

class PartialWriter(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root):
        super(PartialWriter, self).__init__(parser, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destinations = {
            build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/channels/_" + deployment_name.lower() + "_tlm_chn_hdr.txt": Channel_Partial.Channel_Partial(),
            build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/commands/_" + deployment_name.lower() + "_cmds_hdr.txt": Command_Partial.Command_Partial(),
            build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/events/_" + deployment_name.lower() + "_tlm_evr_hdr.txt": Event_Partial.Event_Partial(),
            build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/tools/data_viewer/_user_dataviewers.txt": Data_Viewer_Partial.Data_Viewer_Partial()
            }
        
                    
    def write(self):
        # Open file

        for destination in self.destinations.keys():
            if not os.path.exists(destination):
                fl = open(destination, "w")
                
                tmpl = self.destinations[destination]
                
                msg = tmpl.__str__()
                
                fl.writelines(msg)
                fl.close()
                
                print destination + " Created"
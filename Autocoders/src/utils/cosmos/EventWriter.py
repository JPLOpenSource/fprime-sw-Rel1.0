
import os
import sys
import time
import datetime
import logging

from utils.cosmos import CosmosWriterAbs

PRINT = logging.getLogger('output')

class EventWriter(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, topology, deployment_name, build_root):
        super(EventWriter, self).__init__(topology, deployment_name, build_root)
    
        # Initialize writer-unique file destination location
        self.build_root = build_root
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/events/"
    
    def write(self):
        pass

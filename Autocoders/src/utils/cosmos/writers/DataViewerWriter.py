
import os
import sys
import time
import datetime
import logging

from utils.cosmos.writers import CosmosWriterAbs

from utils.cosmos.templates import Data_Viewer

class DataViewerWriter(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root):
        super(DataViewerWriter, self).__init__(parser, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/tools/data_viewer/"
        
                    
    def write(self):
        event_list= []
        for evr in self.parser.events:
            n = evr.get_evr_name()
            if n in self.repeated_names.keys():
                # Fix other name pair
                if n in event_list:
                    event_list.remove(n)
                    event_list.append(self.repeated_names.get(n).get_comp_name() + "_" + n)
                n = evr.get_comp_name() + "_" + n
            self.repeated_names.update({n: evr})
            event_list.append(n)
        event_list = sorted(event_list)
        
        # Open file
        fl = open(self.destination + "data_viewer.txt", "w")
        print "Data Viewer Created"
        
        dv = Data_Viewer.Data_Viewer()
        
        dv.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        dv.user = os.environ['USER']
        dv.target_upper = self.deployment_name.upper()
        dv.target_name = self.deployment_name.upper()
        dv.evr_names = event_list
                    
        msg = dv.__str__()
                    
        fl.writelines(msg)
        fl.close()

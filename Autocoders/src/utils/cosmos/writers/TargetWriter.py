
import os
import sys
import time
import datetime
import logging
import re

from utils.cosmos.writers import CosmosWriterAbs

from utils.cosmos.templates import Target

class TargetWriter(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root):
        super(TargetWriter, self).__init__(parser, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/"
        
                    
    def write(self):
#         # Open file
        fl = open(self.destination + "target.txt", "w")
        print "target.txt Created"
         
        t = Target.Target()
         
        t.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        t.user = os.environ['USER']
                     
        msg = t.__str__()
                     
        fl.writelines(msg)
        fl.close()

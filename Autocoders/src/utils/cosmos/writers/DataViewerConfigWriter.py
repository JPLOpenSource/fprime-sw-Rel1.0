
import os
import sys
import time
import datetime
import logging
import re

from utils.cosmos.writers import ConfigWriterAbs

from utils.cosmos.templates import Data_Viewer_Config

class DataViewerConfigWriter(ConfigWriterAbs.ConfigWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root, old_definition=None):
        super(DataViewerConfigWriter, self).__init__(parser, deployment_name, build_root, old_definition)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/tools/data_viewer/"
        
                    
    def write(self):
        user_definitions = []
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("TARGET_COMPONENT " + self.deployment_name.upper())
        
        names = []
        if os.path.isfile(self.destination + 'data_viewer.txt'):
            fl = open(self.destination + "data_viewer.txt", "r")
            
            lines = re.findall(".*TARGET_COMPONENT.*", fl.read())
            bad_lines = []
            for line in lines:
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
        
#         # Open file
        fl = open(self.destination + "data_viewer.txt", "w")
         
        dv = Data_Viewer_Config.Data_Viewer_Config()
         
        dv.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        dv.user = os.environ['USER']
        dv.names = names
                     
        msg = dv.__str__()
                     
        fl.writelines(msg)
        fl.close()

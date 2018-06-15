
import os
import sys
import time
import datetime
import logging
import re

from utils.cosmos.writers import ConfigWriterAbs

from utils.cosmos.templates import Tlm_Viewer_Config

class TlmViewerConfigWriter(ConfigWriterAbs.ConfigWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root, old_definition=None):
        super(TlmViewerConfigWriter, self).__init__(parser, deployment_name, build_root, old_definition)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/tools/tlm_viewer/"
        
                    
    def write(self):
        user_definitions = []
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("AUTO_TARGET " + self.deployment_name.upper())
        
        names = []
        if os.path.isfile(self.destination + 'tlm_viewer.txt'):
            fl = open(self.destination + "tlm_viewer.txt", "r")
            
            lines = re.findall(".*AUTO_TARGET.*", fl.read())
            bad_lines = []
            for line in lines:
                line = line.strip()
                if line[0] == '#' or not line[:11] == 'AUTO_TARGET' or " ".join(line.strip().split(" ")[0:2]) in user_definitions:
                    bad_lines.append(line)
                    
            for line in bad_lines:
                lines.remove(line)
                    
            for line in lines:
                line = line.split(" ")
                if not self.old_definition or not line[1] == self.old_definition:
                    names.append(line[1])
                            
            fl.close()
            print "Tlm Viewer Tool Config Altered"
        else:
            print "Tlm Viewer Tool Config Created"
                
        for line in user_definitions:
            names.append(line.split(" ")[1])
        
#         # Open file
        fl = open(self.destination + "tlm_viewer.txt", "w")
         
        tv = Tlm_Viewer_Config.Tlm_Viewer_Config()
         
        tv.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        tv.user = os.environ['USER']
        tv.names = names
                     
        msg = tv.__str__()
                     
        fl.writelines(msg)
        fl.close()

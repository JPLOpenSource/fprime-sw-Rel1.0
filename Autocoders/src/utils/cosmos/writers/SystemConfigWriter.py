
import os
import sys
import time
import datetime
import logging
import re

from utils.cosmos.writers import ConfigWriterAbs

from utils.cosmos.templates import System

class SystemConfigWriter(ConfigWriterAbs.ConfigWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root, old_definition=None):
        super(SystemConfigWriter, self).__init__(parser, deployment_name, build_root, old_definition)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/system/"
        
                    
    def write(self):
        user_definitions = ["DECLARE_TARGET SYSTEM"]
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("DECLARE_TARGET " + self.deployment_name.upper())        
            
        names = []
        if os.path.isfile(self.destination + 'system.txt'):
            fl = open(self.destination + "system.txt", "r")
            
            lines = re.findall(".*DECLARE_TARGET.*", fl.read())
            
            bad_lines = []
            for line in lines:
                line = line.strip()
                if line[0] == '#' or not line[:14] == 'DECLARE_TARGET' or " ".join(line.strip().split(" ")[0:2]) in user_definitions:
                    bad_lines.append(line)
                    
            for line in bad_lines:
                lines.remove(line)
                    
            for line in lines:
                line = line.split(" ")
                if not self.old_definition or not line[1] == self.old_definition:
                    names.append(line[1])
                
            fl.close()
            print "System.txt Altered"
        else:
            print "System.txt Created"
            
        for line in user_definitions:
            names.append(line.split(" ")[1])
        
#         # Open file
        fl = open(self.destination + "system.txt", "w")
         
        s = System.System()
         
        s.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        s.user = os.environ['USER']
        s.names = names
                     
        msg = s.__str__()
                     
        fl.writelines(msg)
        fl.close()


import os
import sys
import time
import datetime
import logging
import re

from utils.cosmos.writers import ConfigWriterAbs

from utils.cosmos.templates import Server_Config

class ServerConfigWriter(ConfigWriterAbs.ConfigWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root, old_definition=None):
        super(ServerConfigWriter, self).__init__(parser, deployment_name, build_root, old_definition)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/tools/cmd_tlm_server/"
        
                    
    def write(self):
        user_definitions = []
        if self.deployment_name and not self.deployment_name == "":
            user_definitions.append("INTERFACE_TARGET " + self.deployment_name.upper())
        
        names = []
        if os.path.isfile(self.destination + 'cmd_tlm_server.txt'):
            fl = open(self.destination + "cmd_tlm_server.txt", "r")
            
            lines = re.findall(".*INTERFACE_TARGET.*", fl.read())
            bad_lines = []
            for line in lines:
                print "LINE EXISTS: " + line
                line = line.strip()
                if line[0] == '#' or not line[:16] == 'INTERFACE_TARGET' or " ".join(line.strip().split(" ")[0:2]) in user_definitions:
                    print "LINE IS BAD: " + line + " " + line[:16]
                    bad_lines.append(line)
                    
            for line in bad_lines:
                lines.remove(line)
                    
            for line in lines:
                line = line.split(" ")
                if not self.old_definition or not line[1] == self.old_definition:
                    names.append(line[1])
                            
            fl.close()
            print "Cmd Tlm Server Config Altered"
        else:
            print "Cmd Tlm Server Config Created"
                
        for line in user_definitions:
            names.append(line.split(" ")[1])
        
#         # Open file
        fl = open(self.destination + "cmd_tlm_server.txt", "w")
         
        sc = Server_Config.Server_Config()
         
        sc.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        sc.user = os.environ['USER']
        sc.names = names
                     
        msg = sc.__str__()
                     
        fl.writelines(msg)
        fl.close()

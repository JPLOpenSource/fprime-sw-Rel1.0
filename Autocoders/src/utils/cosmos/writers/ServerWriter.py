
import os
import sys
import time
import datetime
import logging

from utils.cosmos.writers import CosmosWriterAbs

from utils.cosmos.templates import Cosmos_Server

class ServerWriter(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root):
        super(ServerWriter, self).__init__(parser, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/"
        
                    
    def write(self):
        # Open file
        fl = open(self.destination + "cmd_tlm_server.txt", "w")
        print "Server Interface File Created"
        
        cs = Cosmos_Server.Cosmos_Server()
        
        cs.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        cs.user = os.environ['USER']
        cs.target_name = self.deployment_name.upper()
        cs.write_port = 5000
        cs.read_port = 5000
        cs.read_timeout = 10
        cs.write_timeout = 10
        cs.protocol_name_w = "RefProtocol"
        cs.protocol_name_r = "RefProtocol"
        cs.len_bit_offset_w = 32
        cs.len_bit_offset_r = 72
        cs.len_bit_size_w = 32
        cs.len_bit_size_r = 32
        cs.len_val_offset_w = 8
        cs.len_val_offset_r = 13
        cs.bytes_per_count_w = 1
        cs.bytes_per_count_r = 1 
        cs.endianness_w = "BIG_ENDIAN"
        cs.endianness_r = "BIG_ENDIAN"
        cs.discard_leading_w = 0
        cs.discard_leading_r = 0
        cs.sync_w = "5A5A5A5A"
        cs.sync_r = "413541352047554920"
        cs.has_max_length_w = "nil"
        cs.has_max_length_r = "nil"
        cs.fill_ls_w = "true"
        cs.fill_ls_r = "true"
                    
        msg = cs.__str__()
                    
        fl.writelines(msg)
        fl.close()

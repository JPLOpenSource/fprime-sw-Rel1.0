
import os
import sys
import time
import datetime
import logging

from utils.cosmos import CosmosWriter

from utils.cosmos.templates import Channel_Screen

class ChannelScreenWriter(CosmosWriter.CosmosWriter):
    
    def __init__(self, topology, deployment_name, build_root):
        super(ChannelScreenWriter, self).__init__(topology, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/screens/"
        
                    
    def write(self):
        instances = self.topology.get_instances()
        channel_list = []
        for inst in instances:
            comp_name = inst.get_name()
            comp_type = inst.get_type()
            base_id = inst.get_base_id()
            if '0x' in base_id:
                base_id = int(base_id, 16)
            else:
                base_id = int(base_id)
                comp_parser = inst.get_comp_xml()

            if "get_channels" in dir(comp_parser):
                channels = comp_parser.get_channels()
            
                for ch in channels:
                    n = ch.get_name()
                    if n in self.repeated_names.keys():
                        # Fix other name pair
                        if n in channel_list:
                            channel_list.remove(n)
                            channel_list.append(self.repeated_names.get(n)[1].get_name() + "_" + n)
                        n = comp_name + "_" + n
                    self.repeated_names.update({n: (ch, inst)})
                    channel_list.append(n)
        channel_list = sorted(channel_list)
        
        # Open file
        fl = open(self.destination + "channels.txt", "w")
        print "Channel Screen Created"
        
        c = Channel_Screen.Channel_Screen()
        
        c.target_name = self.deployment_name.upper()
        c.channels = channel_list
                    
        msg = c.__str__()
                    
        fl.writelines(msg)
        fl.close()

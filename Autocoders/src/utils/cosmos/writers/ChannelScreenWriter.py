
import os
import sys
import time
import datetime
import logging

from utils.cosmos.writers import CosmosWriterAbs

from utils.cosmos.templates import Channel_Screen

class ChannelScreenWriter(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root):
        super(ChannelScreenWriter, self).__init__(parser, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/screens/"
        
                    
    def write(self):
        channel_list= []
        for ch in self.parser.channels:
            n = ch.get_ch_name()
            if n in self.repeated_names.keys():
                # Fix other name pair
                if n in channel_list:
                    channel_list.remove(n)
                    channel_list.append(self.repeated_names.get(n).get_comp_name() + "_" + n)
                n = ch.get_comp_name() + "_" + n
            self.repeated_names.update({n: ch})
            channel_list.append(n)
        channel_list = sorted(channel_list)
        
        # Open file
        fl = open(self.destination + "channels.txt", "w")
        print "Channel Screen Created"
        
        c = Channel_Screen.Channel_Screen()
        
        c.date = datetime.datetime.now().strftime("%A, %d, %B, %Y")
        c.user = os.environ['USER']
        c.target_name = self.deployment_name.upper()
        c.channels = channel_list
                    
        msg = c.__str__()
                    
        fl.writelines(msg)
        fl.close()

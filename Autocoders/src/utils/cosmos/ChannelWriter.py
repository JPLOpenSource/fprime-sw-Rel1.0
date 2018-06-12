
import os
import sys
import time
import datetime
import logging

from utils.cosmos import CosmosWriterAbs

from utils.cosmos.templates import Channel

class ChannelWriter(CosmosWriterAbs.CosmosWriterAbs):

    def __init__(self, parser, deployment_name, build_root):
        super(ChannelWriter, self).__init__(parser, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/channels/"
        
    def removekey(self, d, key):
        r = dict(d)
        del r[key]
        return r
    
    def write(self):
        print "Creating Channel Files"
        channel_templates = {}
        for ch in self.parser.channels:
            n = ch.get_ch_name()
            if n in self.repeated_names.keys():
                # Fix other name pair
                if n in channel_templates.keys():
                    channel_templates.get(n).channel_name = self.repeated_names.get(n).get_comp_name() + "_" + n
                    channel_templates.update({self.repeated_names.get(n).get_comp_name() + "_" + 
                                        n: channel_templates.get(n)})
                    channel_templates = self.removekey(channel_templates, n)
                n = ch.get_comp_name() + "_" + n
            self.repeated_names.update({n: ch})

            # Initialize Cheetah Template
            c = Channel.Channel()

            c.date = ch.get_date()
            c.user = ch.get_user()
            c.source = ch.get_source()
            c.component_string = ch.get_component_string()
            c.ch_name = ch.get_ch_name()
            c.endianness = ch.get_endianness()
            c.ch_desc = ch.get_ch_desc()
            c.id = ch.get_id()
            c.target_caps = self.deployment_name.upper()
            c.target_lower = self.deployment_name.lower()

            c.value_bits = ch.get_value_bits()
            c.value_type = ch.get_value_type()
    
            c.format_string = ch.get_format_string()
            c.types = ch.get_types()

            channel_templates.update({n: c})

        # Write files
        for name, c in channel_templates.iteritems():
            fl = open(self.destination + name.lower() + ".txt", "w")
            print "Channel " + c.ch_name + " Created"
            c.ch = c.ch_name.upper()
            msg = c.__str__()
                    
            fl.writelines(msg)
            fl.close()
                    

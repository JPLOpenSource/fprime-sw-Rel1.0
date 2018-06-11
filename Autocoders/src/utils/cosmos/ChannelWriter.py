
import os
import sys
import time
import datetime
import logging

from utils.cosmos import CosmosWriter

from utils.cosmos.templates import Channel

class ChannelWriter(CosmosWriter.CosmosWriter):

    def __init__(self, topology, deployment_name, build_root):
        super(ChannelWriter, self).__init__(topology, deployment_name, build_root)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/channels/"
        
    def removekey(self, d, key):
        r = dict(d)
        del r[key]
        return r
    
    def write(self):
        instances = self.topology.get_instances()
        channel_templates = {}
        for inst in instances:
            comp_name = inst.get_name()
            comp_type = inst.get_type()
            base_id = inst.get_base_id()
            if '0x' in base_id:
                base_id = int(base_id, 16)
            else:
                base_id = int(base_id)
                comp_parser = inst.get_comp_xml()

            #
            # Write out each row of channel tlm data here...
            #
            if "get_channels" in dir(comp_parser):
                channels = comp_parser.get_channels()
                
                for ch in channels:
                    
                    ch_id = ch.get_ids()[0]
                    if '0x' in ch_id:
                        ch_id = int(ch_id, 16)
                    else:
                        ch_id = int(ch_id)
                    ch_id += base_id
                    n     = ch.get_name()
                    if n in self.repeated_names.keys():
                        # Fix other name pair
                        if n in channel_templates.keys():
                            channel_templates.get(n).channel_name = self.repeated_names.get(n)[1].get_name() + "_" + n
                            channel_templates.update({self.repeated_names.get(n)[1].get_name() + "_" + 
                                                n: channel_templates.get(n)})
                            channel_templates = self.removekey(channel_templates, n)
                        n = comp_name + "_" + n
                    self.repeated_names.update({n: (ch, inst)})
                    t     = ch.get_type()
                    enum_name = "None"
                    if type(t) is type(tuple()):
                        enum = t
                        enum_name = t[0][1]
                        t = t[0][0]
                    ch_comment = ch.get_comment()

                    # Initialize Cheetah Template
                    c = Channel.Channel()
                    
                    d = datetime.datetime.now()
                    c.date = d.strftime("%A, %d %B %Y")
                    c.user = os.environ['USER']
                    c.source = comp_parser.get_xml_filename()
                    c.component_string = comp_type + "::" + comp_name
                    c.target_caps = self.deployment_name.upper()
                    c.channel_name = n
                    c.endianness = "BIG_ENDIAN"
                    c.chn_desc = ch_comment
                    c.target_lower = self.deployment_name.lower()
                    c.id = ch_id
                    
                    cosmos_type = self.type_hash[t]
                    
                    c.value_bits = cosmos_type[0]
                    c.value_type = (cosmos_type[1] if not (cosmos_type[1] == "ENUM") else cosmos_type[2])
                    
                    # Handle units
                    format_string = "EMPTY"
                    if ch.get_format_string():
                        format_string = ch.get_format_string()
                    c.format_string = format_string
                    
                    # Handle enum type
                    channel_enum_types = "EMPTY"
                    count = 0
                    if t == 'ENUM':
                        channel_enum_types = []
                        for item in enum[1]:
                            if item[1] == None:
                                channel_enum_types.append((item[0], count))
                            else:
                                channel_enum_types.append((item[0], count))
                            count = count + 1

                    c.types = channel_enum_types
                    channel_templates.update({n: c})
                    
        # Write files
        for name, c in channel_templates.iteritems():
            fl = open(self.destination + c.channel_name.lower() + ".txt", "w")
            print "Channel " + c.channel_name + " Created"
            c.channel_name = c.channel_name.upper()
            msg = c.__str__()
                    
            fl.writelines(msg)
            fl.close()
                    
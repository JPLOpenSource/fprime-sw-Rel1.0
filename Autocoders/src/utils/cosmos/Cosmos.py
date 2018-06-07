
import os
import sys
import time
import datetime

from utils.cosmos.templates import Channel

class Cosmos:
    
    def __init__(self, topology, deployment, cosmos_directory):
        self.topology = topology
        self.deployment = deployment
        self.cosmos_directory = cosmos_directory
        self.type_hash = {}
        self.init_cosmos_hashes()
    
    def init_cosmos_hashes(self):
        self.type_hash["F32"] = (32, "FLOAT")
        self.type_hash["F64"] = (64, "FLOAT")
        self.type_hash["U8"] = (8, "UINT")
        self.type_hash["U16"] = (16, "UINT")
        self.type_hash["U32"] = (32, "UINT")
        self.type_hash["U64"] = (64, "UINT")
        self.type_hash["I8"] = (8, "INT")
        self.type_hash["I16"] = (16, "INT")
        self.type_hash["I32"] = (32, "INT")
        self.type_hash["I64"] = (64, "INT")
        self.type_hash["bool"] = (16, "BOOLEAN", "UINT")
        self.type_hash["string"] = (0, "STRING")
        self.type_hash["ENUM"] = (32, "ENUM", "UINT")
    
    def create_events(self):
        instances = self.topology.get_instances()
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
                    t     = ch.get_type()
                    enum_name = "None"
                    if type(t) is type(tuple()):
                        enum = t
                        enum_name = t[0][1]
                        t = t[0][0]
                    ch_comment = ch.get_comment()
                    #
                    # Write out the channel enum record here...
                    #
                    if t == 'ENUM':
                        num = 0
                        for item in enum[1]:
                            if item[1] == None:
                                pass
                            else:
                                num = int(item[1])
                            num += 1

                    # Initialize Cheetah Template
                    c = Channel.Channel()
                    
                    d = datetime.datetime.now()
                    c.date = d.strftime("%A, %d %B %Y")
                    c.user = os.environ['USER']
                    c.source = comp_parser.get_xml_filename()
                    c.component_string = comp_type + "::" + comp_name
                    c.target_caps = self.deployment.upper()
                    c.channel_name = n
                    c.endianness = "BIG_ENDIAN"
                    c.chn_desc = ch_comment
                    c.target_lower = self.deployment.lower()
                    c.id = ch_id
                    
                    cosmos_type = self.type_hash[t]
                    
                    c.value_bits = cosmos_type[0]
                    c.value_type = cosmos_type[1]
                    
                    # Open file
                    fl = open(self.cosmos_directory + "/targets/REF/cmd_tlm/channels/tst_" + n.lower() + ".txt", "w")
                    
                    msg = c.__str__()
                    fl.writelines(msg.replace("< %=", "<%="))
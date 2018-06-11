
import os
import sys
import time
import datetime
import logging

from utils.cosmos import CosmosWriter

class EventWriter(CosmosWriter.CosmosWriter):
    
    def __init__(self, topology, deployment_name, build_root):
        super(EventWriter, self).__init__(topology, deployment_name, build_root)
    
        # Initialize writer-unique file destination location
        self.build_root = build_root
        self.destination = build_root + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/events/"
    
    def write(self):
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
            # Write out each row of event data here...
            #
            if "get_events" in dir(comp_parser):
                evrs = comp_parser.get_events()
                for evr in evrs:
                    evr_id =evr.get_ids()[0]
                    if '0x' in evr_id:
                        evr_id = int(evr_id, 16)
                    else:
                        evr_id = int(evr_id)
                    evr_id += base_id
                    n = evr.get_name()
                    print n
                    s = evr.get_severity()
                    f = evr.get_format_string()
                    #
                    # Write out the evr args records here...
                    #
                    num = 0
                    args = evr.get_args()
                    for arg in args:
                        n = arg.get_name()
                        t = arg.get_type()
                        c = arg.get_comment()
                        enum_name = "None"
                        if type(t) is type(tuple()):
                            enum = t
                            enum_name = t[0][1]
                            t = t[0][0]
                        num += 1
                        #
                        # Write out the evr enum records here...
                        #
                        if t == 'ENUM':
                            num = 0
                            for item in enum[1]:
                                if item[1] == None:
                                    pass
                                else:
                                    num = int(item[1])
                                num += 1

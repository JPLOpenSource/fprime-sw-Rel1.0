
from utils.cosmos import CosmosCommand
from utils.cosmos import CosmosChannel
from utils.cosmos import CosmosEvent

class CosmosTopParser():
    
    def __init__(self):
        self.channels = []
        self.events = []
        self.commands = []
                
    def parse_topology(self, topology, overwrite = True):
        if overwrite:
            self.channels = []
            self.events = []
            self.commands = []
        
        for inst in topology.get_instances():
            comp_name = inst.get_name()
            comp_type = inst.get_type()
            base_id = inst.get_base_id()
            if '0x' in base_id:
                base_id = int(base_id, 16)
            else:
                base_id = int(base_id)
            comp_parser = inst.get_comp_xml()
            #
            # Write out each row of command data here...
            #
#             if 'get_commands' in dir(comp_parser):
#                 cmds = comp_parser.get_commands()
#                 for cmd in cmds:
#                     opcode = cmd.get_opcodes()[0]
#                     if '0x' in opcode:
#                         opcode = int(opcode, 16)
#                     else:
#                         opcode = int(opcode)
#                     opcode += base_id
#                     n = cmd.get_mnemonic()
#                     c = cmd.get_comment()
#                     cosmos_cmd = CosmosCommand.CosmosCommand(comp_name, comp_type, n, opcode, c)
#                     #
#                     # Write out command args csv here....
#                     #
#                     args = cmd.get_args()
#                     num = 0
#                     for arg in args:
#                         n = arg.get_name()
#                         t = arg.get_type()
#                         c = arg.get_comment()
#                         enum_name = "None"
#                         if type(t) is type(tuple()):
#                             enum = t
#                             enum_name = t[0][1]
#                             t = t[0][0]
#                         num += 1
#                         #
#                         # Write out command enum csv here...
#                         #
#                         if t == 'ENUM':
#                             num2 = 0
#                             for item in enum[1]:
#                                 if item[1] == None:
#                                     pass
#                                 else:
#                                     num2 = int(item[1])
#                                 num2 += 1
#                         cosmos_cmd.add_arg(n, t, c, enum_name)
#                     self.commands.append(cosmos_cmd)       
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
                    comment = evr.get_comment()
                    s = evr.get_severity()
                    f = evr.get_format_string()
                    source = comp_parser.get_xml_filename()
                    cosmos_evr = CosmosEvent.CosmosEvent(comp_name, comp_type, source, evr_id, n, s, f, comment)
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
                        #cosmos_evr.add_arg(n, t, c, enum_name)
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
                    enum = None
                    if type(t) is type(tuple()):
                        enum = t
                        enum_name = t[0][1]
                        t = t[0][0]
                    c = ch.get_comment()
                    source = comp_parser.get_xml_filename()
                    cosmos_ch = CosmosChannel.CosmosChannel(comp_name, comp_type, source, ch_id, n, c)
                    cosmos_ch.set_arg(t, enum_name, enum, ch.get_format_string())
                    self.channels.append(cosmos_ch)
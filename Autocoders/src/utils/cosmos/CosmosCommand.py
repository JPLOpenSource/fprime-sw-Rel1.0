
from utils.cosmos import CosmosObjectAbs

class CosmosCommand(CosmosObjectAbs.CosmosObjectAbs):
    
    class CommandItem:
        def __init__(self, name, desc, bits, type, types, min_val, max_val, default):
            self.name = name.upper()
            self.desc = desc
            self.bits = bits
            self.type = type
            self.types = types
            self.min_val = min_val
            self.max_val = max_val
            self.default = default
            if type == 'STRING':
                self.default = '"' + self.default + '"'
            self.neg_offset = False
            self.bit_offset = 0
            
        def convert_to_tuple(self):
            return (self.name, self.desc, self.types, self.neg_offset, self.bit_offset, self.bits, self.type, self.min_val, self.max_val, self.default)
    
        def add_neg_offset_fields(self, bit_offset):
            self.bit_offset = bit_offset
            self.neg_offset = True
    
    def __init__(self, comp_name, comp_type, source, name, opcode, comment, mnemonic, priority, sync, full):
        super(CosmosCommand, self).__init__(comp_name, comp_type, source)
        self.opcode = opcode
        self.cmd_name = name
        self.cmd_desc = comment
        self.mnemonic = mnemonic
        self.priority = priority
        self.sync = sync
        self.full = full
        self.cmd_args = []

    def convert_items_to_cheetah_list(self, list):
        temp = []
        
        for i in list:
            temp.append(i.convert_to_tuple())
        
        return temp
        
    def add_arg(self, name, type, comment, bits, string_max, enum_name, enum, cmd_type):
        if type == 'string':
            len_item = self.CommandItem(name + "_length", "Length of String Arg", 16, "UINT", [], self.min_hash["U16"], self.max_hash["U16"], self.default_hash["U16"])
            self.cmd_args.append(len_item)
        
        cosmos_type = self.type_hash[type]
        value_type = (cosmos_type[1] if not (cosmos_type[1] == "ENUM" or cosmos_type[1] == "BOOLEAN") else cosmos_type[2])
        
        # Handle enum
        cmd_enum_types = []
        count = 0
        if not enum == None:
            num = 0
            for item in enum[1]:
                if item[1] == None:
                    cmd_enum_types.append((item[0], num))
                else:
                    cmd_enum_types.append((item[0], int(item[1])))
                num += 1
        types = cmd_enum_types
        
        min_val = self.min_hash[type]
        max_val = self.max_hash[type]
        default = self.default_hash[type]
        
        if cmd_type == 'NEG_OFFSET':
            item = self.CommandItem(name, comment, bits, value_type, types, min_val, max_val, default)
            item.add_neg_offset_fields(0)
        else:
            item = self.CommandItem(name, comment, bits, value_type, types, min_val, max_val, default)
        self.cmd_args.append(item)
        
    def update_neg_offset(self):
        reverse = False
        for arg in self.cmd_args:
            if arg.type == 'STRING':
                reverse = True
                break
        
        count = 0
        if reverse:
            for item in reversed(self.cmd_args):
                if item.type == 'STRING':
                    break
                count += item.bits
                item.bit_offset = count * -1
                
    def get_cmd_args(self):
        return self.cmd_args
    def get_cmd_args_cosmos(self):
        return self.convert_items_to_cheetah_list(self.cmd_args)
    def get_opcode(self):
        return self.opcode
    def get_cmd_name(self):
        return self.cmd_name
    def get_cmd_desc(self):
        return self.cmd_desc
    def get_mnemonic(self):
        return self.mnemonic
    def get_priority(self):
        return self.priority
    def get_sync(self):
        return self.sync
    def get_full(self):
        return self.full

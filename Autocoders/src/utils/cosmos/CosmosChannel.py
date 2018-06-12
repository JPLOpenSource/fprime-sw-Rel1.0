
from utils.cosmos import CosmosObjectAbs

class CosmosChannel(CosmosObjectAbs.CosmosObjectAbs):
    
    def __init__(self, comp_name, comp_type, source, ch_id, name, comment):
        super(CosmosChannel, self).__init__(comp_name, comp_type, source)
        self.id = ch_id
        self.ch_name = name
        self.ch_desc = comment
        self.value_bits = 0
        self.value_type = "ERROR: Value item type not set"
        self.format_string = "ERROR: Value item not set"
        self.types = []
    
    def set_arg(self, type, enum_name, enum, format_string):
        cosmos_type = self.type_hash[type]
        self.value_bits = cosmos_type[0]
        self.value_type = (cosmos_type[1] if not (cosmos_type[1] == "ENUM") else cosmos_type[2])
        # print enum_name
        
        # Handle units
        if format_string == None:
            format_string = ""
        self.format_string = format_string
        
        # Handle enum
        channel_enum_types = []
        count = 0
        if not enum == None:
            num = 0
            for item in enum[1]:
                if item[1] == None:
                    channel_enum_types.append((item[0], num))
                else:
                    channel_enum_types.append((item[0], int(item[1])))
                num += 1
        self.types = channel_enum_types

    def get_id(self):
        return self.id
    def get_ch_name(self):
        return self.ch_name
    def get_ch_desc(self):
        return self.ch_desc
    def get_value_bits(self):
        return self.value_bits
    def get_value_type(self):
        return self.value_type
    def get_format_string(self):
        return self.format_string
    def get_types(self):
        return self.types
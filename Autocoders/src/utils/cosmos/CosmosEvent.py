
from utils.cosmos import CosmosObjectAbs

class CosmosEvent(CosmosObjectAbs.CosmosObjectAbs):
    
    class EventItem:
        def __init__(self, name, desc, bits, type, types, is_block = False):
            self.name = name.upper()
            self.desc = desc
            self.bits = bits
            self.type = type
            self.types = types
            self.block = is_block
            self.neg_offset = False
            self.derived = False
            self.bit_offset = 0
            self.template_string = ""
            
        def convert_to_tuple(self):
            return (self.block, self.derived, self.name, self.desc, self.template_string, self.types, self.neg_offset, self.bit_offset, self.bits, self.type)
    
        def add_neg_offset_fields(self, bit_offset):
            self.bit_offset = bit_offset
            self.neg_offset = True
            self.block = False
            self.derived = False

        def add_derived_fields(self, template_string):
            self.template_string = template_string
            self.derived = True
            self.block = False
            self.neg_offset = False
    
    def __init__(self, comp_name, comp_type, source, evr_id, name, severity, format_string, comment):
        super(CosmosEvent, self).__init__(comp_name, comp_type, source)
        self.id = evr_id
        self.evr_name = name
        self.evr_desc = comment
        self.severity = severity
        self.format_string = format_string
        self.evr_items = []
        self.names = []
        self.non_len_names = []
        
    def add_block(self):
        item = self.EventItem("name", "desc", 0, "type", [], True)
        self.evr_items.append(item)
        
    def convert_items_to_cheetah_list(self, list):
        temp = []
        
        for i in list:
            temp.append(i.convert_to_tuple())
        
        return temp
        
    def add_item(self, name, desc, bits, type, enum_name, enum, evr_type, bit_offset, template_string):
        if type == 'string':
            if evr_type == 'DERIVED':
                len_item = self.EventItem(name + "_length", "Length of String Arg", 16, "UINT", [])
                len_item.add_derived_fields(template_string)
                self.evr_items.append(len_item)
            else:
                len_item = self.EventItem(name + "_length", "Length of String Arg", 16, "UINT", [])
                self.evr_items.append(len_item)
        
        cosmos_type = self.type_hash[type]
        value_type = (cosmos_type[1] if not (cosmos_type[1] == "ENUM" or cosmos_type[1] == "BOOLEAN") else cosmos_type[2])
        
        # Handle enum
        event_enum_types = []
        count = 0
        if not enum == None:
            num = 0
            for item in enum[1]:
                if item[1] == None:
                    event_enum_types.append((item[0], num))
                else:
                    event_enum_types.append((item[0], int(item[1])))
                num += 1
        types = event_enum_types
        
        if evr_type == 'NEG_OFFSET':
            item = self.EventItem(name, desc, bits, value_type, types)
            item.add_neg_offset_fields(bit_offset)
        elif evr_type == 'DERIVED':
            item = self.EventItem(name, desc, bits, value_type, types)
            item.add_derived_fields(template_string)
        else:
            item = self.EventItem(name, desc, bits, value_type, types)
        self.non_len_names.append(name)
        self.names.append(name)
        self.evr_items.append(item)
        
    def update_neg_offset(self):
        reverse = False
        for item in self.evr_items:
            if item.type == 'STRING' and not item.block:
                reverse = True
                break
        
        count = 0
        if reverse:
            for item in reversed(self.evr_items):
                if item.type == 'STRING':
                    break
                count += item.bits
                item.bit_offset = count * -1
                
    def update_template_strings(self):
        # THIS AMOUNT IS HARDCODED, PLEASE FIX
        total_pre_item_bits = 256
        aggregate = str(total_pre_item_bits) + " START"
        for item in self.evr_items:
            if not item.block:
                item.template_string = aggregate + " " + str(item.bits) + " " + item.type
                aggregate = item.template_string
                
    def get_evr_items(self):
        return self.evr_items
    def get_evr_items_cosmos(self):
        return self.convert_items_to_cheetah_list(self.evr_items)
    def get_names(self):
        return self.names
    def get_nonlen_names(self):
        return self.non_len_names
    def get_id(self):
        return self.id
    def get_evr_name(self):
        return self.evr_name
    def get_evr_desc(self):
        return self.evr_desc
    def get_severity(self):
        return self.severity
    def get_format_string(self):
        return self.format_string

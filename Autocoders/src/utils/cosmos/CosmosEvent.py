
from utils.cosmos import CosmosObjectAbs

class CosmosEvent(CosmosObjectAbs.CosmosObjectAbs):
    
    class EventItem:
        def __init__(self, name, desc, bits, type, types, format_string, is_block = False):
            self.name = name
            self.desc = desc
            self.bits = bits
            self.type = type
            self.types = types
            self.format_string
            self.block = is_block
            self.neg_offset = False
            self.derived = False
            
        def add_neg_offset_fields(self, bit_offset):
            self.bit_offset = bit_offset
            self.neg_offset = True
            self.block = False
            self.derived = False
            
        def add_derived_fields(self, template_string):
            self.template_string = template_string
            self.derived = True
            self.block = False
            self.neg_offset = True
            
    
    def __init__(self, comp_name, comp_type, source, evr_id, name, severity, format_string, comment):
        super(CosmosEvent, self).__init__(comp_name, comp_type, source)
        self.id = evr_id
        self.evr_name = name
        self.evr_desc = comment
        self.severity = severity
        self.format_string = format_string
        self.item_type = 'NORMAL'
        self.neg_offset = False
        self.neg_offset = False
        self.derived = False
        self.last_item = 'NONE'
        self.items = []
        
    def add_item(self, name, desc, bits, type, enum_name, enum, format_string, evr_type, bit_offset, template_string):
        # Handle units
        if format_string == None:
            format_string = ""
        
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
        types = channel_enum_types
        
        item = 'NONE'
        if evr_type == 'BLOCK':
            item = EventItem(name, desc, bits, type, types, format_string, True)
        elif evr_type == 'NEGOFFSET':
            item = EventItem(name, desc, bits, type, types, format_string)
            item.add_neg_offset_fields(bit_offset)
        elif evr_type == 'DERIVED':
            item = EventItem(name, desc, bits, type, types, format_string)
            item.add_derived_fields(template_string)
        else:
            item = EventItem(name, desc, bits, type, types, format_string)
        self.last_item = item
        self.items.append(item)
        
    def get_items(self):
        return items
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
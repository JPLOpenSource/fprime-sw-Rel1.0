
from utils.cosmos import CosmosObjectAbs

class CosmosCommand(CosmosObjectAbs.CosmosObjectAbs):
    
    def __init__(self, comp_name, comp_type, name, opcode, comment):
        super(CosmosCommand, self).__init__(comp_name, comp_type)
        self.name = name
        self.opcode = opcode
        self.comment = comment
        print comp_name, comp_type, name, opcode, comment
        
    def add_arg(self, name, type, comment, enum_name):
        print name, type, comment, enum_name
        
    def get_name(self):
        return self.name
    def get_opcode(self):
        return self.opcode
    def get_comment(self):
        return self.comment
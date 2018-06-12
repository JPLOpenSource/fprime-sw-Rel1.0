
import os
import sys
import time
import datetime

class CosmosObjectAbs(object):
    
    def __init__(self, comp_name, comp_type, source):
        self.comp_name = comp_name
        self.component_string = comp_name + "::" + comp_type
        d = datetime.datetime.now()
        self.date = d.strftime("%A, %d, %B, %Y")
        self.user = os.environ['USER']
        self.endianness = "BIG_ENDIAN" # HARDCODED FOR FPRIME
        self.source = source
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
        
    def get_date(self):
        return self.date
    def get_user(self):
        return self.user
    def get_source(self):
        return self.source
    def get_endianness(self):
        return self.endianness
    def get_component_string(self):
        return self.component_string
    def get_comp_name(self):
        return self.comp_name
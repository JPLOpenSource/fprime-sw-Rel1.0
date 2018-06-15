
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
        self.min_hash = {}
        self.max_hash = {}
        self.default_hash = {}
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
        
        self.min_hash["F32"] = -10000.0
        self.min_hash["F64"] = -100000.0
        self.min_hash["U8"] = 0
        self.min_hash["U16"] = 0
        self.min_hash["U32"] = 0
        self.min_hash["U64"] = 0
        self.min_hash["I8"] = -128
        self.min_hash["I16"] = -1000 #-32768
        self.min_hash["I32"] = -10000 #-2147483648
        self.min_hash["I64"] = -10000#-9223372036854775808
        self.min_hash["bool"] = 0
        self.min_hash["string"] = ""
        self.min_hash["ENUM"] = self.min_hash["U32"]
        
        self.max_hash["F32"] = 10000.0
        self.max_hash["F64"] = 100000.0
        self.max_hash["U8"] = 255
        self.max_hash["U16"] = 1000  #65535
        self.max_hash["U32"] = 10000 #4294967295
        self.max_hash["U64"] = 10000#18446744073709551615
        self.max_hash["I8"] = 127
        self.max_hash["I16"] = 32767
        self.max_hash["I32"] = 10000 #2147483647
        self.max_hash["I64"] = 10000 #9223372036854775807
        self.max_hash["bool"] = 1
        self.max_hash["string"] = "" # Dont use this, should be set elsewhere to value from topology
        self.max_hash["ENUM"] = self.max_hash["U32"]
        
        self.default_hash["F32"] = 0.0
        self.default_hash["F64"] = 0.0
        self.default_hash["U8"] = 0
        self.default_hash["U16"] = 0
        self.default_hash["U32"] = 0
        self.default_hash["U64"] = 0
        self.default_hash["I8"] = 0
        self.default_hash["I16"] = 0
        self.default_hash["I32"] = 0
        self.default_hash["I64"] = 0
        self.default_hash["bool"] = False
        self.default_hash["string"] = "String" # Dont use this, should be set elsewhere to value from topology
        self.default_hash["ENUM"] = 0
        
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
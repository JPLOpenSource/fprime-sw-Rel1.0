
class CosmosWriter(object):
    
    def __init__(self, topology, deployment_name, cosmos_directory):
        self.topology = topology
        self.deployment_name = deployment_name
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
    
    def write(self):
        raise '# CosmosWriter.write() - Implementation Error: you must supply your own concrete implementation.'
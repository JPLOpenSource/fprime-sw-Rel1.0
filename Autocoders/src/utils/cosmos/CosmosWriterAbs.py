
class CosmosWriterAbs(object):
    
    def __init__(self, parser, deployment_name, cosmos_directory):
        self.parser = parser
        self.deployment_name = deployment_name
        self.cosmos_directory = cosmos_directory
        
    def removekey(self, d, key):
        r = dict(d)
        del r[key]
        return r
    
    def write(self):
        raise '# CosmosWriter.write() - Implementation Error: you must supply your own concrete implementation.'
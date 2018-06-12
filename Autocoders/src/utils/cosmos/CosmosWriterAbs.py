
class CosmosWriterAbs(object):
    
    def __init__(self, parser, deployment_name, cosmos_directory):
        self.parser = parser
        self.deployment_name = deployment_name
        self.cosmos_directory = cosmos_directory
    
    def write(self):
        raise '# CosmosWriter.write() - Implementation Error: you must supply your own concrete implementation.'

from utils.cosmos.writers import CosmosWriterAbs

class ConfigWriterAbs(CosmosWriterAbs.CosmosWriterAbs):
    
    def __init__(self, parser, deployment_name, build_root, old_definition):
        super(ConfigWriterAbs, self).__init__(parser, deployment_name, build_root)
        self.old_definition = old_definition

    def write(self):
        pass

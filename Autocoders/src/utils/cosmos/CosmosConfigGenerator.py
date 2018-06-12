import logging

# Global logger init. below.
PRINT = logging.getLogger('output')

class CosmosConfigGenerator:
    
    def __init__(self):
        self.writers = []

    def append_writer(self, cosmos_writer):
        self.writers.append(cosmos_writer)
    
    def generate_cosmos_files(self):
        if self.writers:
            for writer in self.writers:
                writer.write()
        else:
            PRINT.info("Must add file writers before generating files")
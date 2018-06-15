import logging
import os

# Global logger init. below.
PRINT = logging.getLogger('output')

class CosmosGenerator:
    
    def __init__(self):
        self.writers = []
        
    def make_directory(self, directory):
        if not os.path.isdir(directory):
            os.makedirs(directory)
            print "Created " + directory
        else:
            print "Directory " + directory + " already exists"
        
    def create_filesystem(self, deployment, build_root):
        print "Creating Directory System"
        base_directory = build_root + "/COSMOS/config/"
        
        self.make_directory(base_directory + "system/")
        self.make_directory(base_directory + "tools/cmd_tlm_server/")
        self.make_directory(base_directory + "tools/tlm_viewer/")
        self.make_directory(base_directory + "tools/data_viewer/")
        self.make_directory(base_directory + "targets/" + deployment.upper())
        self.make_directory(base_directory + "targets/" + deployment.upper() + "/screens/")
        self.make_directory(base_directory + "targets/" + deployment.upper() + "/tools/")
        self.make_directory(base_directory + "targets/" + deployment.upper() + "/tools/data_viewer/")
        self.make_directory(base_directory + "targets/" + deployment.upper() + "/cmd_tlm/")
        self.make_directory(base_directory + "targets/" + deployment.upper() + "/cmd_tlm/channels")
        self.make_directory(base_directory + "targets/" + deployment.upper() + "/cmd_tlm/commands")
        self.make_directory(base_directory + "targets/" + deployment.upper() + "/cmd_tlm/events")

    def append_writer(self, cosmos_writer):
        self.writers.append(cosmos_writer)
    
    def generate_cosmos_files(self):
        if self.writers:
            for writer in self.writers:
                writer.write()
        else:
            PRINT.info("Must add file writers before generating files")
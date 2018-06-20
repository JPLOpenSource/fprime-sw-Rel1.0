#!/bin/env python
#===============================================================================
# NAME: CosmosGenerator.py
#
# DESCRIPTION: This class takes in a variable amount of CosmosWriterAbs instances
# and calls each of their write() methods within its generate_cosmos_files()
# method in order to autocode the Cosmos config text files.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

import logging
import os
import shutil

PRINT = logging.getLogger('output')

# Cosmos file writer class
from utils.cosmos.writers import ChannelWriter
from utils.cosmos.writers import CommandWriter
from utils.cosmos.writers import ConfigSystemWriter
from utils.cosmos.writers import ServerWriter
from utils.cosmos.writers import ChannelScreenWriter
from utils.cosmos.writers import DataViewerWriter
from utils.cosmos.writers import EventWriter
from utils.cosmos.writers import ConfigDataViewerWriter
from utils.cosmos.writers import ConfigTlmViewerWriter
from utils.cosmos.writers import ConfigServerWriter
from utils.cosmos.writers import TargetWriter
from utils.cosmos.writers import PartialWriter
from utils.cosmos.writers import RubyWriter

# Global logger init. below.
PRINT = logging.getLogger('output')

class CosmosGenerator:
    """
    This class contains methods that are capable of creating all the files and
    directories that a deployment needs to be added to COSMOS.
    """
    
    def __init__(self):
        """
        Init
        """
        self.channels = []
        self.events = []
        self.commands = []
        
    def make_directory(self, directory):
        """
        Creates a directory
        @param directory: The directory to create
        """
        if not os.path.isdir(directory):
            os.makedirs(directory)
            print "Created " + directory
        else:
            print "Directory " + directory + " already exists"
        
    def create_filesystem(self, target, root_dir):
        """
        Creates the target's /config directory and its subdirectories
        @param target: The name of the target to create
        @param root_dir: /config location
        """
        print "Creating Directory System"
        base_directory = root_dir + "/config/"
        
        self.make_directory(base_directory + "system/")
        self.make_directory(base_directory + "tools/cmd_tlm_server/")
        self.make_directory(base_directory + "tools/tlm_viewer/")
        self.make_directory(base_directory + "tools/data_viewer/")
        self.make_directory(base_directory + "targets/" + target.upper())
        self.make_directory(base_directory + "targets/" + target.upper() + "/screens/")
        self.make_directory(base_directory + "targets/" + target.upper() + "/tools/")
        self.make_directory(base_directory + "targets/" + target.upper() + "/tools/data_viewer/")
        self.make_directory(base_directory + "targets/" + target.upper() + "/cmd_tlm/")
        self.make_directory(base_directory + "targets/" + target.upper() + "/cmd_tlm/channels")
        self.make_directory(base_directory + "targets/" + target.upper() + "/cmd_tlm/commands")
        self.make_directory(base_directory + "targets/" + target.upper() + "/cmd_tlm/events")
        
    def remove_target(self, cosmos_path, target):
        """
        Deletes a target by removing its /config directory and all other
        instances where it is mentioned in config files
        @param cosmos_path: Path to COSMOS directory
        @param target: Target to remove (name in caps)
        """
        # SYSTEM is required by COSMOS for it to run properly
        if target == "SYSTEM":
            print "ERROR: DO NOT REMOVE COSMOS SYSTEM FOLDER"  
        elif not os.path.isdir(cosmos_path + "/config/targets/" + target):
            print "ERROR: DEPLOYMENT " + target + " DOES NOT EXIST"
        else:
            shutil.rmtree(cosmos_path + "/config/targets/" + target)
            print "REMOVED " + cosmos_path + "/config/targets/" + target + "/"
        
            # Remove reference to target from files shared by all other targets
            ConfigSystemWriter.ConfigSystemWriter(None, "", cosmos_path, target).write()
            ConfigServerWriter.ConfigServerWriter(None, "", cosmos_path, target).write()
            ConfigDataViewerWriter.ConfigDataViewerWriter(None, "", cosmos_path, target).write()
            ConfigTlmViewerWriter.ConfigTlmViewerWriter(None, "", cosmos_path, target).write()
            print "REMOVED ALL REFERENCES TO " + target
    
    def generate_cosmos_files(self, target, cosmos_path):        
        """
        Generate all COSMOS config files
        @param target: Name of target to write files to
        @param cosmos_path: Path to COSMOS directory
        """
        writers = []
        
        # Package command and telemetry data to be passed to writers
        cmd_tlm_data = self.pack_cmd_tlm_data()
        
        # Comment out writer to remove it from file generation
        writers.append(PartialWriter.PartialWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(ConfigSystemWriter.ConfigSystemWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(ConfigServerWriter.ConfigServerWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(ConfigDataViewerWriter.ConfigDataViewerWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(ConfigTlmViewerWriter.ConfigTlmViewerWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(ServerWriter.ServerWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(TargetWriter.TargetWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(ChannelWriter.ChannelWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(EventWriter.EventWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(CommandWriter.CommandWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(ChannelScreenWriter.ChannelScreenWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(DataViewerWriter.DataViewerWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(DataViewerWriter.DataViewerWriter(cmd_tlm_data, target, cosmos_path))
        writers.append(RubyWriter.RubyWriter(cmd_tlm_data, target, cosmos_path))
        
        for writer in writers:
            writer.write()
            
    def pack_cmd_tlm_data(self):
        """
        Packs all command and telemetry data into a tuple so that it can be
        sent to writers in alphabetical order
        @return: (channels, commands, events)
        """
        return (self.channels, self.commands, self.events)
    
    def load_commands(self, commands, overwrite = True):
        """
        Load all commands into generator's list
        @param commands: Command to be written
        @param overwrite: Whether to overwrite previous contents of list (optional)
        """
        if overwrite:
            self.commands = []
        for command in commands:
            self.commands.append(command)
            
    def load_events(self, events, overwrite = True):
        """
        Load all events into generator's list
        @param events: Events to be written
        @param overwrite: Whether to overwrite previous contents of list (optional)
        """
        if overwrite:
            self.events = []
        for event in events:
            self.events.append(event)
            
    def load_channels(self, channels, overwrite = True):
        """
        Load all channels into generator's list
        @param channels: Channels to be written
        @param overwrite: Whether to overwrite previous contents of list (optional)
        """
        if overwrite:
            self.channels = []
        for channel in channels:
            self.channels.append(channel)
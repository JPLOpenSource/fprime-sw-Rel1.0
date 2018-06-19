#!/bin/env python
#===============================================================================
# NAME: cosmosgen.py
#
# DESCRIPTION: A tool for autocoding topology XML files into cosmos targets in 
# COSMOS directory.
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

import os
import sys
import shutil
import time
import glob
import logging
import exceptions

from optparse import OptionParser
from models import ModelParser
from utils import ConfigManager

from utils import Logger

# Parsers to read the XML
from parsers import XmlParser
from parsers import XmlTopologyParser

# Cosmos file writer class
from utils.cosmos import CosmosGenerator
from utils.cosmos import CosmosTopParser
from utils.cosmos.writers import CosmosWriter
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

# Configuration manager object.
CONFIG = ConfigManager.ConfigManager.getInstance()

# Flag to indicate verbose mode.
VERBOSE = False

# Global logger init. below.
PRINT = logging.getLogger('output')
DEBUG = logging.getLogger('debug')

# Build Root environmental variable if one exists.
BUILD_ROOT = None

# Deployment name from topology XML only
DEPLOYMENT = None

# COSMOS config file location
COSMOS = None

# Version label for now
class Version:
    id      = "0.1"
    comment = "Initial prototype"
VERSION = Version()

def pinit():
    """
    Initialize the option parser and return it.
    """

    usage = "usage: %prog [options] [xml_topology_filename]"
    vers = "%prog " + VERSION.id + " " + VERSION.comment
    program_longdesc = '''
This script reads F' topology XML and produces .txt files that configure a COSMOS target.
These can be used to send commands and receive telemetry within the COSMOS system.
'''
    program_license = "Copyright 2018 user_name (California Institute of Technology)                                            \
                ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged."

    parser = OptionParser(usage, version=vers, epilog=program_longdesc,description=program_license)
    
    # Add parser options
    parser.add_option("-l", "--logger", dest="logger", default="QUIET",
        help="Set the logging level <DEBUG | INFO | QUIET> (def: 'QUIET').")
    parser.add_option("-r", "--rm_target", dest="target_rm",
                      help="Target to be removed", action="store", default=None)
    
    parser.add_option("-v", "--verbose", dest="verbose_flag",
                      help="Enable verbose mode showing more runtime detail (def: False)",
                      action="store_true", default=False)
    
    return parser
    
    
def main():
    """
    Main program.
    """
    global VERBOSE # prevent local creation of variable
    global BUILD_ROOT # environmental variable if set
    global DEPLOYMENT # deployment set in topology xml only and used to install new instance dicts

    CONFIG = ConfigManager.ConfigManager.getInstance()
    Parser = pinit()
    (opt, args) = Parser.parse_args()
    VERBOSE = opt.verbose_flag
    
        # Get the current working directory so that we can return to it when
    # the program completes. We always want to return to the place where
    # we started.
    
    starting_directory = os.getcwd()
    
    
    # Check for BUILD_ROOT env. variable
    if ('BUILD_ROOT' in os.environ.keys()) == False:
        PRINT.info("ERROR: Build root not set to root build path...")
        sys.exit(-1)
    else:
        BUILD_ROOT = os.environ['BUILD_ROOT']
        ModelParser.BUILD_ROOT = BUILD_ROOT
        PRINT.info("BUILD_ROOT set to %s in environment" % BUILD_ROOT)
    print starting_directory, BUILD_ROOT        
    # Remove a target from filesystem
    if opt.target_rm:
        target = opt.target_rm.upper()
        
        # Required by COSMOS for it to run properly
        if target == "SYSTEM":
            print "ERROR: DO NOT REMOVE COSMOS SYSTEM FOLDER"
            sys.exit(-1)
            
        if not os.path.isdir(BUILD_ROOT + "/COSMOS/config/targets/" + target):
            print "ERROR: DEPLOYMENT " + target + " DOES NOT EXIST"
            sys.exit(-1)
        
        shutil.rmtree(BUILD_ROOT + "/COSMOS/config/targets/" + target)
        print "REMOVED " + BUILD_ROOT + "/COSMOS/config/targets/" + target + "/"
        
        # Write targetless info ("" in params) to each of the files that we don't want to entirely remove
        # as they may affect other targets we aren't currently removing
        ConfigSystemWriter.ConfigSystemWriter(None, "", BUILD_ROOT, target).write()
        ConfigServerWriter.ConfigServerWriter(None, "", BUILD_ROOT, target).write()
        ConfigDataViewerWriter.ConfigDataViewerWriter(None, "", BUILD_ROOT, target).write()
        ConfigTlmViewerWriter.ConfigTlmViewerWriter(None, "", BUILD_ROOT, target).write()
        print "REMOVED ALL REFERENCES TO " + target
        sys.exit(-1)

    #
    #  Parse the input Topology XML filename
    #
    if len(args) == 0:
        PRINT.info("Usage: %s [options] xml_filename" % sys.argv[0])
        return
    else:
        xml_filenames = args[0:]
    
    #
    # Create XML Parser and write COSMOS files for Topology
    #
    for xml_filename in xml_filenames:
        
        xml_type = XmlParser.XmlParser(xml_filename)()

        if xml_type == "assembly" or xml_type == "deployment":
            DEBUG.info("Detected ISF Topology XML Files...")
            the_parsed_topology_xml = XmlTopologyParser.XmlTopologyParser(xml_filename)

            # Name of COSMOS target to be created
            DEPLOYMENT = the_parsed_topology_xml.get_deployment()
            PRINT.info("Found assembly or deployment named: %s\n" % DEPLOYMENT)
            
            #
            # Create COSMOS application file system here by passing XML parser data to cosmos config file generator
            #
            
            cosmos_parser = CosmosTopParser.CosmosTopParser()
            
            # Parse the topology file
            cosmos_parser.parse_topology(the_parsed_topology_xml)
    
            cosmos_gen = CosmosGenerator.CosmosGenerator()
            
            # Create the config/targets directories for the Deployment if they don't already exist
            cosmos_gen.create_filesystem(DEPLOYMENT, BUILD_ROOT)
             
            # Add the writers for the corresponding files that should be written
            cosmos_gen.append_writer(PartialWriter.PartialWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(ConfigSystemWriter.ConfigSystemWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(ConfigServerWriter.ConfigServerWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(ConfigDataViewerWriter.ConfigDataViewerWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(ConfigTlmViewerWriter.ConfigTlmViewerWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(ServerWriter.ServerWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(TargetWriter.TargetWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(ChannelWriter.ChannelWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(EventWriter.EventWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(CommandWriter.CommandWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(ChannelScreenWriter.ChannelScreenWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
            cosmos_gen.append_writer(DataViewerWriter.DataViewerWriter(cosmos_parser, DEPLOYMENT, BUILD_ROOT))
             
            # Generate all files here
            cosmos_gen.generate_cosmos_files()
            
        else:
            PRINT.info("File not a Topology XML file")
            sys.exit(-1)
            
    # Always return to directory where we started.
    os.chdir(starting_directory)

if __name__ == '__main__':
    main()

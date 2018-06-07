'''
NAME: cosmosgen.py

DESCRIPTION: This script reads topology XML to produce config files for
             a cosmos application.
'''

import os
import sys
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
from utils.cosmos.Cosmos import Cosmos

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
                      help="Target to be removed", default=None)
    
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
    #
    #  Parse the input Component XML file and create internal meta-model
    #
    if len(args) == 0:
        PRINT.info("Usage: %s [options] xml_filename" % sys.argv[0])
        return
    else:
        xml_filenames = args[0:]

    # Check for BUILD_ROOT env. variable
    if ('BUILD_ROOT' in os.environ.keys()) == False:
        PRINT.info("ERROR: Build root not set to root build path...")
        sys.exit(-1)
    else:
        BUILD_ROOT = os.environ['BUILD_ROOT']
        ModelParser.BUILD_ROOT = BUILD_ROOT
        PRINT.info("BUILD_ROOT set to %s in environment" % BUILD_ROOT)
    #
    # Parse XML
    #
    for xml_filename in xml_filenames:       
        
        xml_type = XmlParser.XmlParser(xml_filename)()

        if xml_type == "assembly" or xml_type == "deployment":
            DEBUG.info("Detected ISF Topology XML Files...")
            the_parsed_topology_xml = XmlTopologyParser.XmlTopologyParser(xml_filename)
            
            for inst in the_parsed_topology_xml.get_instances():
                comp_name = inst.get_name()
                comp_type = inst.get_type()
                base_id = inst.get_base_id()
                if '0x' in base_id:
                    base_id = int(base_id, 16)
                else:
                    base_id = int(base_id)
                comp_parser = inst.get_comp_xml()
            DEPLOYMENT = the_parsed_topology_xml.get_deployment()
            PRINT.info("Found assembly or deployment named: %s\n" % DEPLOYMENT)
            COSMOS = BUILD_ROOT + "/COSMOS/config"
            
            #
            # Create COSMOS application file system here by passing parsed topology to cosmos file generator
            #
            cosmos = Cosmos(the_parsed_topology_xml, DEPLOYMENT, COSMOS)
            
            # Generate all event files here
            cosmos.create_events()
            
        else:
            PRINT.info("File not a Topology XML file")
            sys.exit(-1)
            
    # Always return to directory where we started.
    os.chdir(starting_directory)

if __name__ == '__main__':
    main()

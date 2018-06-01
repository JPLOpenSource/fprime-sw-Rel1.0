#!/usr/bin/env python
'''
NAME: sysDictionaryGen.py

DESCRIPTION: This script reads topology XML to produce command, EVR,
             Channel telemetry summary tables.
'''

import os
import sys
import time
import glob
import logging
import exceptions
import csv

from optparse import OptionParser

from utils import Logger
from utils import ConfigManager


# Parsers to read the XML
from models import ModelParser
from parsers import XmlParser
from parsers import XmlComponentParser
from parsers import XmlPortsParser
from parsers import XmlSerializeParser
from parsers import XmlTopologyParser
from _ast import Num

# Flag to indicate verbose mode.
VERBOSE = False

# Global logger init. below.
PRINT = logging.getLogger('output')
DEBUG = logging.getLogger('debug')

# Configuration manager object.
CONFIG = ConfigManager.ConfigManager.getInstance()

# Build a default log file name
SYS_TIME = time.gmtime()

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

    current_dir = os.getcwd()

    usage = "usage: %prog [options] [xml_filename]"
    vers = "%prog " + VERSION.id + " " + VERSION.comment
    program_longdesc = '''
This script reads F' topology XML and produces summary *.csv spreadsheet files.
These spreadsheets contain all command, evr, and channel telemetry descriptions.
'''
    program_license = "Copyright 2018 user_name (California Institute of Technology)                                            \
                ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged."

    parser = OptionParser(usage, version=vers, epilog=program_longdesc,description=program_license)
    
    parser.add_option("-p", "--path", dest="work_path", type="string",
        help="Switch to new working directory (def: %s)." % current_dir,
        action="store", default=current_dir)

    #parser.add_option("-v", "--verbose", dest="verbose_flag",
    #    help="Enable verbose mode showing more runtime detail (def: False)",
    #    action="store_true", default=False)
    
    parser.add_option("-l", "--logger", dest="logger", default="QUIET",
        help="Set the logging level <DEBUG | INFO | QUIET> (def: 'QUIET').")

    parser.add_option("-L", "--logger-output-file", dest="logger_output",
        default=None, help="Set the logger output file. (def: isfgen.log).")
    
    return parser

def isSimpleType(type):
    """
    Returns True if this is type of F[32|64],U[8|16|32|64],I[8|16|32|64],string, or ENUM,
    otherwise return False
    @param: type is the name of the type of argument
    """
    if (("F32" == type) or
        ("F64" == type) or
        ("U8"   == type) or
        ("U16"  == type) or 
        ("U32"  == type) or 
        ("U64"  == type) or 
        ("I8"   == type) or 
        ("I16"  == type) or 
        ("I32"  == type) or 
        ("I64"  == type) or
        ("bool" == type) or
        ("string" == type) or
        ("ENUM" == type)):
        return True
    else:
        return False


def enumFindAndParse(enum_name):
    """
    Returns a list of tuple's of (identifier, value, comment) if enum of enum_name is found,
    otherwise returns None object.
    """
    enum_list = []
    #
    # Iterate over component collections
    #
    os.chdir(BUILD_ROOT)
    #
    # Only search Svc for now!
    #
    for collection_dir in glob.glob('Svc'):
        if os.path.isdir(collection_dir):
            bdir = BUILD_ROOT + os.sep + collection_dir
            os.chdir(bdir)
            for component_dir in glob.glob('*'):
                if os.path.isdir(component_dir):
                    dir = bdir + os.sep + component_dir
                    os.chdir(dir)
                    enum_files = glob.glob("*EnumAi.txt")
                    if len(enum_files) > 0:
                        for efile in enum_files:
                            if os.path.isfile(efile):
                                #print efile, enum_name
                                if enum_name == efile.split('EnumAi.txt')[0]:
                                    lines = open(efile, 'r').readlines()[5:]
                                    lines = filter(lambda x: x!='\n', lines)
                                    for l in range(0,len(lines),3):
                                        l1 = lines[l].strip('\n')
                                        l2 = lines[l+1].strip('\n')
                                        l3 = lines[l+2].strip('\n')
                                        enum_list.append((l1,l2,l3))
                                    return enum_list
                    os.chdir('..')
            os.chdir(BUILD_ROOT)
        return enum_list
    
    
def main():
    """
    Main program.
    """
    global VERBOSE # prevent local creation of variable
    global BUILD_ROOT # environmental variable if set
    global GEN_TEST_CODE # indicate if test code should be generated
    global DEPLOYMENT # deployment set in topology xml only and used to install new instance dicts

    CONFIG = ConfigManager.ConfigManager.getInstance()
    Parser = pinit()
    (opt, args) = Parser.parse_args()
    #VERBOSE = opt.verbose_flag

    # Check that the specified working directory exists. Remember, the
    # default working directory is the current working directory which
    # always exists. We are basically only checking for when the user
    # specifies an alternate working directory.

    if os.path.exists(opt.work_path) == False:
        Parser.error('Specified path does not exist (%s)!' % opt.work_path)

    #
    log_level = opt.logger
    log_fd = opt.logger_output

    # Configure the logging.
    log_level_dict = dict()

    log_level_dict['QUIET']    = None
    log_level_dict['DEBUG']    = logging.DEBUG
    log_level_dict['INFO']     = logging.INFO
    log_level_dict['WARNING']  = logging.WARN
    log_level_dict['ERROR']    = logging.ERROR
    log_level_dict['CRITICAL'] = logging.CRITICAL

    if log_level_dict[log_level] == None:
        stdout_enable = False
    else:
        stdout_enable = True

    log_fd = opt.logger_output
    # For now no log file

    Logger.connectDebugLogger(log_level_dict[log_level], log_fd, stdout_enable)
    Logger.connectOutputLogger(log_fd)
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
        PRINT.info("ERROR: The -b command option requires that BUILD_ROOT environmental variable be set to root build path...")
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

        if xml_type == "component":
            DEBUG.info("Detected ISF Component XML Files...")
            the_parsed_component_xml = XmlComponentParser.XmlComponentParser(xml_filename)
            
        elif xml_type == "interface":
            DEBUG.info("Detected ISF Port XML Files...")
            the_parsed_port_xml = XmlPortsParser.XmlPortsParser(xml_filename)

        elif xml_type == "serializable":
            DEBUG.info("Detected ISF Serializable XML Files...")
            the_serial_xml = XmlSerializeParser.XmlSerializeParser(xml_filename)

        elif xml_type == "assembly" or xml_type == "deployment":
            DEBUG.info("Detected ISF Topology XML Files...")
            the_parsed_topology_xml = XmlTopologyParser.XmlTopologyParser(xml_filename)
            DEPLOYMENT = the_parsed_topology_xml.get_deployment()
            PRINT.info("Found assembly or deployment named: %s\n" % DEPLOYMENT)
            COSMOS = BUILD_ROOT + "/COSMOS/config"
            #
            # Create COSMOS application file system here
            #
            if not os.path.exists(COSMOS + "/targets/" + DEPLOYMENT.upper()):
                os.makedirs(COSMOS + "/targets/" + DEPLOYMENT.upper())
                PRINT.info("Created Directory: %s", COSMOS + "/targets/" + DEPLOYMENT.upper())
            else:
                PRINT.info("Directory %s already exists", COSMOS + "/targets/" + DEPLOYMENT.upper())
            #
            # Open CSV files here...
            #
            sys_fd = open(COSMOS + "/system/system.txt","w")
            PRINT.info("Opened: %s", COSMOS + "/system/system.txt")
            #
            tar_fd = open(COSMOS + "/targets/" + DEPLOYMENT.upper() + "/target.txt","w")
            PRINT.info("Opened: %s",COSMOS + "/targets/" + DEPLOYMENT.upper() + "/target.txt")
#            #
#            cmd_fd_enums = open(DEPLOYMENT + "_CommandsEnums.csv","w")
#            cmd_writer_enums = csv.writer(cmd_fd_enums)
#            PRINT.info("Opened: %s", DEPLOYMENT + "_CommandsEnums.csv")
#            #
#            evr_fd = open(DEPLOYMENT + "_EventMsgs.csv","w")
#            evr_writer = csv.writer(evr_fd)
#            PRINT.info("Opened: %s", DEPLOYMENT + "_EventMsgs.csv")
#            #
#            evr_fd_args = open(DEPLOYMENT + "_EventsArgs.csv","w")
#            evr_writer_args = csv.writer(evr_fd_args)
#            PRINT.info("Opened: %s", DEPLOYMENT + "_EventsArgs.csv")
#            #
#            evr_fd_enums = open(DEPLOYMENT + "_EventsEnums.csv","w")
#            evr_writer_enums = csv.writer(evr_fd_enums)
#            PRINT.info("Opened: %s", DEPLOYMENT + "_EventsEnums.csv")
#            #
#            ch_fd  = open(DEPLOYMENT + "_Channels.csv", "w")
#            ch_writer = csv.writer(ch_fd)
#            PRINT.info("Opened: %s", DEPLOYMENT + "_Channels.csv")
#            #
#            ch_fd_enums = open(DEPLOYMENT + "_ChannelsEnums.csv","w")
#            ch_writer_enums = csv.writer(ch_fd_enums)
#            PRINT.info("Opened: %s", DEPLOYMENT + "_ChannelsEnums.csv")
            #
            # Write headers
            #
#            cmd_writer.writerow(["COMPONENT NAME", "COMPONENT TYPE", "OPCODE", "MNEMONIC", "COMMENT"])
#            cmd_writer_args.writerow(["COMPONENT NAME", "COMPONENT TYPE", "OPCODE", "ARG NUMBER", "ARG NAME", "ARG TYPE", "COMMENT", "ENUM NAME"])
#            cmd_writer_enums.writerow(["COMPONENT NAME", "COMPONENT TYPE", "OPCODE", "ENUM_NAME", "INDETIFIER", "VALUE", "COMMENT"])
#            evr_writer.writerow(["COMPONENT NAME", "COMPONENT TYPE", "EVR ID", "NAME", "SERVERITY", "FORMAT"])
#            evr_writer_args.writerow(["COMPONENT NAME", "COMPONENT TYPE", "EVR ID", "ARG NUMBER", "ARG NAME", "ARG TYPE", "COMMENT", "ENUM NAME"])
#            evr_writer_enums.writerow(["COMPONENT NAME", "COMPONENT TYPE", "EVR_ID", "ENUM_NAME", "INDETIFIER", "VALUE", "COMMENT"])
#            ch_writer.writerow(["COMPONENT NAME", "COMPONENT TYPE", "CHANNEL ID", "NAME", "TYPE", "COMMENT", "ENUM NAME"])
#            ch_writer_enums.writerow(["COMPONENT NAME", "COMPONENT TYPE", "CH_ID", "ENUM_NAME", "INDETIFIER", "VALUE", "COMMENT"])
#            PRINT.info("Completed writing headings row.")
#            #
#            # Parse instances here...
#            #
#            for inst in the_parsed_topology_xml.get_instances():
#                # print inst.get_name(), inst.get_type()
#                comp_name = inst.get_name()
#                comp_type = inst.get_type()
#                base_id = inst.get_base_id()
#                if '0x' in base_id:
#                    base_id = int(base_id, 16)
#                else:
#                    base_id = int(base_id)
#                comp_parser = inst.get_comp_xml()
#                #
#                # Write out each row of command data here...
#                #
#                if 'get_commands' in dir(comp_parser):
#                    cmds = comp_parser.get_commands()
#                    for cmd in cmds:
#                        opcode = cmd.get_opcodes()[0]
#                        if '0x' in opcode:
#                            opcode = int(opcode, 16)
#                        else:
#                            opcode = int(opcode)
#                        opcode += base_id
#                        n = cmd.get_mnemonic()
#                        c = cmd.get_comment()
#                        cmd_writer.writerow([comp_name, comp_type, opcode, n, c])
#                        # print "\t", cmd.get_mnemonic(), opcode + base_id
#                        #
#                        # Write out command args csv here....
#                        #
#                        args = cmd.get_args()
#                        num = 0
#                        for arg in args:
#                            n = arg.get_name()
#                            t = arg.get_type()
#                            c = arg.get_comment()
#                            enum_name = "None"
#                            if type(t) is type(tuple()):
#                                enum = t
#                                enum_name = t[0][1]
#                                t = t[0][0]
#                                # print "\t\t", arg.get_name(), arg.get_type()
#                            cmd_writer_args.writerow([comp_name,comp_type,opcode,num,n, t, c, enum_name])
#                            num += 1
#                            #
#                            # Write out command enum csv here...
#                            #
#                            if t == 'ENUM':
#                                num2 = 0
#                                for item in enum[1]:
#                                    if item[1] == None:
#                                        pass
#                                    else:
#                                        num2 = int(item[1])
#                                    cmd_writer_enums.writerow([comp_name, comp_type, opcode, enum_name, item[0], num2, item[2]])
#                                    num2 += 1
#                #
#                # Write out each row of event data here...
#                #
#                if "get_events" in dir(comp_parser):
#                    evrs = comp_parser.get_events()
#                    for evr in evrs:
#                        evr_id =evr.get_ids()[0]
#                        if '0x' in evr_id:
#                            evr_id = int(evr_id, 16)
#                        else:
#                            evr_id = int(evr_id)
#                        evr_id += base_id
#                        n = evr.get_name()
#                        s = evr.get_severity()
#                        f = evr.get_format_string()
#                        evr_writer.writerow([comp_name, comp_type, evr_id, n, s, f])
#                            # print "\t\t", evr.get_name(), evr_id + base_id
#                        #
#                        # Write out the evr args records here...
#                        #
#                        num = 0
#                        args = evr.get_args()
#                        for arg in args:
#                            n = arg.get_name()
#                            t = arg.get_type()
#                            c = arg.get_comment()
#                            enum_name = "None"
#                            if type(t) is type(tuple()):
#                                enum = t
#                                enum_name = t[0][1]
#                                t = t[0][0]
#                            evr_writer_args.writerow([comp_name,comp_type,evr_id,num,n,t,c,enum_name])
#                            num += 1
#                            #
#                            # Write out the evr enum records here...
#                            #
#                            if t == 'ENUM':
#                                num = 0
#                                for item in enum[1]:
#                                    if item[1] == None:
#                                        pass
#                                    else:
#                                        num = int(item[1])
#                                    evr_writer_enums.writerow([comp_name, comp_type, evr_id, enum_name, item[0], num, item[2]])
#                                    num += 1
#                            #
#                            # Write out any evr's with enum generated from text hacked files...
#                            # Assume if type is names it is an enum
#                            #
#                            if isSimpleType(t) == False:
#                                #print evr_id, n, t, isSimpleType(t)
#                                enum_name = t
#                                items = enumFindAndParse(t)
#                                if items != None:
#                                    for item in items:
#                                        evr_writer_enums.writerow([comp_name, comp_type, evr_id, enum_name, item[0], item[1], item[2]])
#                #
#                # Write out each row of channel tlm data here...
#                #
#                if "get_channels" in dir(comp_parser):
#                    channels = comp_parser.get_channels()
#                    for ch in channels:
#                        ch_id = ch.get_ids()[0]
#                        if '0x' in ch_id:
#                            ch_id = int(ch_id, 16)
#                        else:
#                            ch_id = int(ch_id)
#                        ch_id += base_id
#                        n     = ch.get_name()
#                        t     = ch.get_type()
#                        enum_name = "None"
#                        if type(t) is type(tuple()):
#                            enum = t
#                            enum_name = t[0][1]
#                            t = t[0][0]
#                        c     = ch.get_comment()
#                        ch_writer.writerow([comp_name, comp_type, ch_id, n, t, c, enum_name])
#                        #
#                        # Write out the channel enum csv record here...
#                        #
#                        if t == 'ENUM':
#                            num = 0
#                            for item in enum[1]:
#                                if item[1] == None:
#                                    pass
#                                else:
#                                    num = int(item[1])
#                                ch_writer_enums.writerow([comp_name, comp_type, ch_id, enum_name, item[0], num, item[2]])
#                                num += 1
#                        #
#                        # Write out any channel with enum generated from text hacked files...
#                        # Assume if type is names it is an enum
#                        #
#                        if isSimpleType(t) == False:
#                            #print ch_id, n, t, isSimpleType(t)
#                            enum_name = t
#                            items = enumFindAndParse(t)
#                            if items != None:
#                                for item in items:
#                                    ch_writer_enums.writerow([comp_name, comp_type, ch_id, enum_name, item[0], item[1], item[2]])
#
#            cmd_fd.close()
#            cmd_fd_args.close()
#            cmd_fd_enums.close()
#            evr_fd.close()
#            evr_fd_args.close()
#            evr_fd_enums.close()
#            ch_fd.close()
#            ch_fd_enums.close()
#            PRINT.info("CSV Files closed!")
#        else:
#            PRINT.info("Invalid ISF XML found...this format not supported")



if __name__ == '__main__':
    main()

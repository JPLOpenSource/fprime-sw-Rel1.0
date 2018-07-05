'''
NAME: OpenmctJSONDictonaryGen.py

DESCRIPTION: Reads topology XML to produce command, EVR, and channel JSON
             dictionaries to be read in by the openmct-telemetry-server as
             configuration files

AUTHOR: Aaron Doubek-Kraft aarondou@jpl.nasa.gov
'''

import os
import logging
import json

from optparse import OptionParser

from models import ModelParser
from parsers import XmlTopologyParser
from utils import Logger

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
        This script reads F' topology XML and produces summary JSON documents.
        These documents contain all command, evr, and channel telemetry descriptions.
        '''
    program_license = "Copyright 2018 user_name (California Institute of Technology)                                            \
                ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged."

    parser = OptionParser(usage, version=vers, epilog=program_longdesc,description=program_license)

    parser.add_option("-p", "--path", dest="work_path", type="string",
        help="Switch to new working directory (def: %s)." % current_dir,
        action="store", default=current_dir)

    parser.add_option("-l", "--logger", dest="logger", default="QUIET",
        help="Set the logging level <DEBUG | INFO | QUIET> (def: 'QUIET').")

    parser.add_option("-L", "--logger-output-file", dest="logger_output",
        default=None, help="Set the logger output file. (def: isfgen.log).")

    return parser

def main():

    parser = pinit()
    (opts, args) = parser.parse_args()
    xmlFilename = args[0]
    outFilename = "/".join([opts.work_path, "dictionary.json"])

    # Log to stdout
    Logger.connectOutputLogger(opts.logger_output)

    # Global logger init. below.
    PRINT = logging.getLogger('output')
    DEBUG = logging.getLogger('debug')

    #
    #  Parse the input Component XML file and create internal meta-model
    #
    if len(args) == 0:
        PRINT.info("Usage: %s [options] xml_filename" % sys.argv[0])
        return
    else:
        xmlFilename = args[0]

    # Check for BUILD_ROOT env. variable
    if ('BUILD_ROOT' in os.environ.keys()) == False:
        PRINT.info("ERROR: The -b command option requires that BUILD_ROOT environmental variable be set to root build path...")
        sys.exit(-1)
    else:
        BUILD_ROOT = os.environ['BUILD_ROOT']
        ModelParser.BUILD_ROOT = BUILD_ROOT
        PRINT.info("BUILD_ROOT set to %s in environment" % BUILD_ROOT)

    parsedTopology = XmlTopologyParser.XmlTopologyParser(xmlFilename)
    deployment = parsedTopology.get_deployment().lower()

    dictionary = {}
    dictionary[deployment] = {
        "events": {},
        "channels": {},
        "commands": {}
    }

    events = dictionary[deployment]["events"]
    channels = dictionary[deployment]["channels"]
    commands = dictionary[deployment]["commands"]

    limitLabels = ["low_red", "low_orange", "low_yellow", "high_yellow", "high_orange", "high_red"]
    unitLabels = ["label", "gain", "offset"]

    for inst in parsedTopology.get_instances():
        comp_name = inst.get_name()
        comp_type = inst.get_type()
        comp_namespace = inst.get_namespace()
        component = "::".join([comp_namespace, comp_type])
        base_id = inst.get_base_id()
        if '0x' in base_id:
            base_id = int(base_id, 16)
        else:
            base_id = int(base_id)
        comp_parser = inst.get_comp_xml()
        comp_dir = dir(comp_parser)

        if "get_commands" in comp_dir:
            for command in comp_parser.get_commands():
                opcode = command.get_opcodes()[0]
                opcode = int(opcode, 16) if ('0x' in opcode) else int(opcode)
                opcode += base_id

                name = "_".join([comp_name, command.get_mnemonic()])

                arguments = []
                for arg in command.get_args():
                    arguments.append({
                        "description": arg.get_comment(),
                        "name": arg.get_name(),
                        "type": arg.get_type(),
                    })

                metadata = {
                    "id": opcode,
                    "name": name,
                    "description": command.get_comment(),
                    "component": component,
                    "arguments" : arguments
                }

                commands[opcode] = metadata

        if "get_events" in comp_dir:
            for event in comp_parser.get_events():
                ev_id = event.get_ids()[0]
                ev_id = int(ev_id, 16) if ('0x' in ev_id) else int(ev_id)
                ev_id += base_id

                arguments = []
                for arg in event.get_args():
                    arguments.append(arg.get_type())

                metadata = {
                    "id": ev_id,
                    "description":  event.get_comment(),
                    "name": event.get_name(),
                    "component": component,
                    "format_string": event.get_format_string(),
                    "severity": event.get_severity(),
                    "telem_type": "event",
                    "arguments": arguments
                }

                events[ev_id] = metadata

        if "get_channels" in comp_dir:
            for channel in comp_parser.get_channels():
                ch_id = channel.get_ids()[0]
                ch_id = int(ch_id, 16) if ('0x' in ch_id) else int(ch_id)
                ch_id += base_id

                name = "_".join([comp_name, channel.get_name()])

                units = []
                for unit in channel.get_units():
                    units.append(dict(zip(unitLabels, unit)))

                type = channel.get_type()
                type_name = ''
                if isinstance(type, str):
                    type_name = type
                else:
                    type_name = 'Enum'
                    enum_dict = {}
                    for (i, enum) in enumerate(type[1]):
                        enum_dict[str(i)] = enum[0]


                metadata = {
                    "id": ch_id,
                    "name": name,
                    "description": channel.get_comment(),
                    "telem_type": "channel",
                    "component": component,
                    "format_string": channel.get_format_string(),
                    "limits" : dict(zip(limitLabels, channel.get_limits())),
                    "type": type_name,
                    "units": units
                }

                if (type_name == "Enum"):
                    metadata["enum_dict"] = enum_dict
                    metadata["format_string"] = "%s"

                channels[ch_id] = metadata

    # Add events channel
    channels["-1"] = {
        "id": "-1",
        "name": "Events",
        "telem_type": "channel",
        "component": None,
        "description": "Events are shown here",
        "type": "string",
        "format_string": None
    }

    # Stringify JSON -- indent option makes it readable, can be removed if file
    # size is an issue
    jsonStr = json.dumps(dictionary, indent=4)

    # Create output directory if it doesn't exist
    directory = os.path.dirname(outFilename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write JSON to file
    outFile = open(outFilename, 'w')
    outFile.write(jsonStr)
    PRINT.info("JSON output written to %s" % outFilename)
    outFile.close()

if __name__ == '__main__':
    main()

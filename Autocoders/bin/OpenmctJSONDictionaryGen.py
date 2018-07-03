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

parser = OptionParser("Usage: %prog [xml_filename]")
(opts, args) = parser.parse_args()
xmlFilename = args[0]
outFilename = "dictionary.json"

# Log to stdout
Logger.connectOutputLogger(None)

# Global logger init. below.
PRINT = logging.getLogger('output')
DEBUG = logging.getLogger('debug')

# Set build root
BUILD_ROOT = os.environ['BUILD_ROOT']
ModelParser.BUILD_ROOT = BUILD_ROOT
PRINT.info("BUILD_ROOT set to %s in environment" % BUILD_ROOT)

parsedTopology = XmlTopologyParser.XmlTopologyParser(xmlFilename)
deployment = parsedTopology.get_deployment().lower()

print(deployment)

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
                arguments.append({
                    "description": arg.get_comment(),
                    "name": arg.get_name(),
                    "type": arg.get_type(),
                })

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

            metadata = {
                "id": ch_id,
                "name": name,
                "description": channel.get_comment(),
                "telem_type": "channel",
                "component": component,
                "format_string": channel.get_format_string(),
                "limits" : dict(zip(limitLabels, channel.get_limits())),
                "type": channel.get_type(),
                "units": units
            }

            channels[ch_id] = metadata

outFile = open(outFilename, 'w')
jsonStr = json.dumps(dictionary, indent=4)
outFile.write(jsonStr)
PRINT.info("JSON output written to %s" % outFilename)
outFile.close()

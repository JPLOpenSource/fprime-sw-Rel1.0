'''
NAME: OpenmctJSONDictonaryGen.py

DESCRIPTION: Reads topology XML to produce command, EVR, and channel JSON
             dictionaries to be read in by the openmct-telemetry-server as
             configuration files

AUTHOR: Aaron Doubek-Kraft aarondou@jpl.nasa.gov
'''

import os

from optparse import OptionParser

from parsers import XmlTopologyParser

parser = OptionParser("Usage: %prog [xml_filename]")
args = parser.parse_args()
print(args)

parsedTopology = XmlTopologyParser.XmlTopologyParser(xmlFilename)
deployment = parsedTopology.get_deployment()

print(deployment)

for inst in parsedTopology.get_instances():
    print inst.get_name()

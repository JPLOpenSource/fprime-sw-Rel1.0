#!/bin/env python
#===============================================================================
# NAME: ChannelWriter.py
#
# DESCRIPTION: This writer generates the channel files in the COSMOS/config/targets
# /DEPLOYMENT_NAME/cmd_tlm/channels/ directory that contains configuration data 
# for each channel.
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
import time
import datetime
import logging

from utils.cosmos.writers import AbstractCosmosWriter

from utils.cosmos.templates import Channel

class ChannelWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This class generates the channel definition files in
    cosmos_directory/COSMOS/config/targets/deployment_name.upper()/cmd_tlm/channels/
    """

    def __init__(self, parser, deployment_name, cosmos_directory):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        """
        super(ChannelWriter, self).__init__(parser, deployment_name, cosmos_directory)
        self.repeated_names = {}
        
        # Initialize writer-unique file destination location
        self.destination = cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/channels/"
    
    def write(self):
        """
        Generates the file
        """
        print "Creating Channel Files"
        channel_templates = {}
        for ch in self.parser.channels:
            n = ch.get_ch_name()
            if n in self.repeated_names.keys():
                # Fix other name pair
                if n in channel_templates.keys():
                    channel_templates.get(n).channel_name = self.repeated_names.get(n).get_comp_name() + "_" + n
                    channel_templates.update({self.repeated_names.get(n).get_comp_name() + "_" + 
                                        n: channel_templates.get(n)})
                    channel_templates = self.removekey(channel_templates, n)
                n = ch.get_comp_name() + "_" + n
            self.repeated_names.update({n: ch})

            # Initialize and fill Cheetah Template
            c = Channel.Channel()

            c.date = ch.get_date()
            c.user = ch.get_user()
            c.source = ch.get_source()
            c.component_string = ch.get_component_string()
            c.ch_name = n
            c.endianness = ch.get_endianness()
            c.ch_desc = ch.get_ch_desc()
            c.id = ch.get_id()
            c.target_caps = self.deployment_name.upper()
            c.target_lower = self.deployment_name.lower()

            c.value_bits = ch.get_value_bits()
            c.value_type = ch.get_value_type()
    
            c.format_string = ch.get_format_string()
            c.types = ch.get_types()

            channel_templates.update({n: c})

        # Write files
        for name, c in channel_templates.iteritems():
            c.ch_name = name
            fl = open(self.destination + name.lower() + ".txt", "w")
            print "Channel " + name + " Created"
            c.ch_name = name.upper()
            msg = c.__str__()
                    
            fl.writelines(msg)
            fl.close()
                    
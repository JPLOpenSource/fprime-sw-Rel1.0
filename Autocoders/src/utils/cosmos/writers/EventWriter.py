#!/bin/env python
#===============================================================================
# NAME: EventWriter.py
#
# DESCRIPTION: This writer generates the event files in the COSMOS/config/targets
# /DEPLOYMENT_NAME/cmd_tlm/events/ directory that contains configuration data 
# for each event.
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

from utils.cosmos.templates import Event

class EventWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This class generates the event definiton files in
    cosmos_directory/COSMOS/config/targets/deployment_name.upper()/cmd_tlm/events/
    """
    
    def __init__(self, topology, deployment_name, cosmos_directory):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        """
        super(EventWriter, self).__init__(topology, deployment_name, cosmos_directory)
        self.repeated_names = {}
    
        # Initialize writer-unique file destination location
        self.cosmos_directory = cosmos_directory
        self.destination = cosmos_directory + "/COSMOS/config/targets/" + deployment_name.upper() + "/cmd_tlm/events/"
    
    def write(self):
        """
        Generates the file
        """
        print "Creating Event Files"
        event_templates = {}
        for evr in self.parser.events:
            n = evr.get_evr_name()
            if n in self.repeated_names.keys():
                # Fix other name pair
                if n in event_templates.keys():
                    event_templates.get(n).channel_name = self.repeated_names.get(n).get_comp_name() + "_" + n
                    event_templates.update({self.repeated_names.get(n).get_comp_name() + "_" + 
                                        n: event_templates.get(n)})
                    event_templates = self.removekey(event_templates, n)
                n = evr.get_comp_name() + "_" + n
            self.repeated_names.update({n: evr})

            # Initialize and fill Cheetah Template
            e = Event.Event()

            e.date = evr.get_date()
            e.user = evr.get_user()
            e.source = evr.get_source()
            e.component_string = evr.get_component_string()
            e.evr_name = n
            e.endianness = evr.get_endianness()
            e.evr_desc = evr.get_evr_desc()
            e.id = evr.get_id()
            e.target_caps = self.deployment_name.upper()
            e.target_lower = self.deployment_name.lower()
            e.evr_items = evr.get_evr_items_cosmos()
            e.names = evr.get_names()
            e.nonlen_names = evr.get_nonlen_names()
    
            e.format_string = evr.get_format_string()
            e.severity = evr.get_severity()

            event_templates.update({n: e})

        # Write files
        for name, e in event_templates.iteritems():
            e.evr_name = name
            fl = open(self.destination + name.lower() + ".txt", "w")
            print "Event " + name + " Created"
            e.evr_name = name.upper()
            msg = e.__str__()
                    
            fl.writelines(msg)
            fl.close()
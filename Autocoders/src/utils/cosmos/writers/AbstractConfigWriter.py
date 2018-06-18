#!/bin/env python
#===============================================================================
# NAME: AbstractConfigWriter.py
#
# DESCRIPTION: This is the abstract class inherited by only the writers who generate
# the files that reside outside of the COSMOS/config/targets/DEPLOYMENT_NAME/
# as they require the ability to append rather than just creating / deleting.
# These classes all begin with the prefix "Config"
#
# AUTHOR: Jordan Ishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED: June 6, 2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from utils.cosmos.writers import AbstractCosmosWriter

class AbstractConfigWriter(AbstractCosmosWriter.AbstractCosmosWriter):
    """
    This abstract class defines the commonality between all files outside
    of the COSMOS/config/targets/TARGET_NAME/ directories as they must be
    able to append / remove target definitions as opposed to just rewriting
    the entire file.
    """
    
    def __init__(self, parser, deployment_name, cosmos_directory, old_definition):
        """
        @param parser: CosmosTopParser instance with channels, events, and commands
        @param deployment_name: name of the COSMOS target
        @param cosmos_directory: Directory of COSMOS
        @param old_definition: COSMOS target name that you want to remove
        """
        super(AbstractConfigWriter, self).__init__(parser, deployment_name, cosmos_directory)
        self.old_definition = old_definition

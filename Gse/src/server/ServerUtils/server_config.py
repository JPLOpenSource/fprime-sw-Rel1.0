#===============================================================================
# NAME: ServerConfig.py
#
# DESCRIPTION: This is a simple configuration class patterned after the
#		one in the Keck observation sequencer GUI and the Tahoe
#       CalVal pipeline.  The configuration class has changed since
#       previous ones.  This new one uses the ConfigParser module
#       included with Python 2.4 to extend configuration out to
#       reading windows like .ini files.  If none exist then this
#       uses hardwired values set in a dictionary called prop to
#       default initiallization.
#
# AUTHOR: Leonard J. Reder
#
# EMAIL:  reder@jpl.nasa.gov
#
# DATE CREATED  : 6 June 2017 
#
# Copyright 2017, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

import os
import sys
import glob
import ConfigParser


class ServerConfig(ConfigParser.SafeConfigParser):
    """
    This class provides a single entrypoint for all configurable properties,
    namely the self.Prop dictionary.
    """

    __instance = None
    __prop     = None

    def __init__(self):
        """
	    Constructor.
	    """
        ConfigParser.SafeConfigParser.__init__(self)
        ConfigParser.ConfigParser.__init__(self)
        ConfigParser.RawConfigParser.__init__(self)
        self.__prop   = dict()
        self._setProps()

        # Constants
        self.FLIGHT_TYPE = "flight"
        self.GROUND_TYPE = "ground"
        self.PUB_TYPE    = "publish"
        self.SUB_TYPE    = "subscription"
        self.SUB_OPTION  = "subscribe"
        self.USUB_OPTION = "unsubscribe"
        
        self.REG_CMD     = "reg"
        self.SUB_CMD     = "sub"
        self.USUB_CMD    = "usub"
        self.LIST_CMD    = "list"

        self.ROUTING_TABLE_CMD_ADDRESS = "ipc:///tmp/pipe.rt_cmd"
        self.ROUTING_TABLE_CMD_REPLY_ADDRESS = "ipc:///tmp/pipe.rt_cmd_reply"


        config_file_name = 'server.ini'
        files = list()

        # And in current directory
        files.append(os.getcwd() + os.sep + config_file_name)

        self.read(files)


    def getInstance():
        """
        Return instance of singleton.
        """
        if(ServerConfig.__instance is None):
            ServerConfig.__instance = ServerConfig()
        return ServerConfig.__instance

    #define static method
    getInstance = staticmethod(getInstance)


    def _setProps(self):
        """
	Used only by constructor to set all ConfigParser defaults. Establishes
        a dictionary of sections and then a dictionary of keyword, value
        association for each section.
	@params None
        """


        ################################################################
        # Default file paths here.
        ################################################################
        

        # Log file save path
        # Default: Current Directory

        try:
            build_root = os.environ['BUILD_ROOT']
        except KeyError, e:
            print "Server Config: BUILD_ROOT not found."
            build_root = ''

        server_filepath = os.path.join(build_root, 'Gse/src/server')
        log_filepath = os.path.join("logs", "server_logs")
        self.__prop['filepaths'] = dict()
        self.__prop['filepaths']['server_filepath'] = server_filepath 
        self.__prop['filepaths']['server_log_filepath'] = os.path.join(\
                                                  server_filepath, log_filepath)
        self.__prop['filepaths']['server_log_internal_filepath'] = os.path.join(\
                                        self.__prop['filepaths']['server_log_filepath'], 'internals')
        self.__prop['filepaths']['throughput_analysis_filepath'] = os.path.join(\
                                                    server_filepath, "logs/throughput")

        self.__prop['settings'] = dict()
        self.__prop['settings']['server_socket_hwm'] = 10000
                                                    

        # This sets the defaults within a section. 
        self._setSectionDefaults('filepaths')
        self._setSectionDefaults('settings')   

    def _setSectionDefaults(self, section):
        """
        For a section set up the default values.
        """
        self.add_section(section)
        for (key,value) in self.__prop[section].items():
            self.set(section, key, "%s" % value)


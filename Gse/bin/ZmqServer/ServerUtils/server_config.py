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
        self.__prop['filepaths'] = dict()

        # Log file save path
        # Default: Current Directory

        server_filepath = os.getcwd()
        log_filepath = os.path.join("logs", "server_logs")
        self.__prop['filepaths']['server_filepath'] = server_filepath 
        self.__prop['filepaths']['server_log_filepath'] = os.path.join(\
                                                  server_filepath, log_filepath)
                                                    




        # This sets the defaults within a section. 
        self._setSectionDefaults('filepaths')
               

    def _setSectionDefaults(self, section):
        """
        For a section set up the default values.
        """
        self.add_section(section)
        for (key,value) in self.__prop[section].items():
            self.set(section, key, "%s" % value)


if __name__ == '__main__':
    #
    # Quick test of configure defaults.
    #
    config = ConfigManager().getInstance()
    print
    print 'IPC section defaults:'
    for (key, value) in config.items('ipc'):
        print "%s = %s" % (key, value)
    print
    print 'Get some of the ipc values:'
    print 'h_pub_suffix = %s' % config.get('ipc','h_pub_suffix')
    print 'h_msg_suffix = %s' % config.get('ipc','h_msg_suffix')
    print 'c_int_suffix = %s' % config.get('ipc','c_int_suffix')
    print 'c_dispatch_suffix = %s' % config.get('ipc','c_dispatch_suffix')
    print 'c_cmd_dispatch_suffix = %s' % config.get('ipc', 'c_cmd_dispatch_suffix')

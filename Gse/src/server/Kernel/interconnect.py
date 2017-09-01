import os
import zmq
import types
import random
import binascii

# Global server config class
from server.ServerUtils.server_config import ServerConfig
SERVER_CONFIG = ServerConfig.getInstance()


###################################################################
## Helper functions for connecting sockets                       ##
###################################################################

def GetRandomPort():
    return random.randrange(50000,60000)

import zmq

from logging import DEBUG, INFO, ERROR 

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import SetGlobalLoggingLevel, GetLogger
from server.ServerUtils.server_config import ServerConfig

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class Adapter(object):
    """
    General adapter class.
    """

    def __init__(self, protocol, client_type, server_cmd_port):
        self.__name = "{}_adapter".format(protocol)

        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(self.__name,log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        self.__logger.debug("Logger Active")

        # Adapter Information 
        self.__client_type = client_type
        self.__protocol = protocol
        
        # ZMQ Socket Handles and Information
        self.__server_pub_port = None
        self.__server_sub_port = None

        self.__context = zmq.Context()

        self.__client_connections = {} # Save connections by client ID 
    
        self.__command_socket = self.__context.socket(zmq.ROUTER) 
        self.__command_socket.connect("tcp://localhost:{}".format(server_cmd_port))

        # Create Reactor 
        self.__loop = IOLoop.instance()

        # Wrap sockets in ZMQStreams for IOLoop handlers
        self.__command_socket = ZMQStream(self.__command_socket)

        # Register handlers
        self.__command_socket.on_recv(self.__HandleCommand)

    def Start(self):
        try:
            self.__logger.debug("Reactor Starting")
            self.__RegisterToServer()

            self.__loop.start()

        except KeyboardInterrupt:
            pass # Fall through to quit
        
        self.Quit()

    def Quit(self):
        self.__logger.info("Stopping adapter")

        self.__command_socket.close()
        self.__context.term()

    def __HandleCommand(self, msg): 

        if msg[0] == "":
            pass

        # Setup pub/sub ports
        self.__server_pub_port = struct.unpack("<I", msg[1])[0]
        self.__server_sub_port = struct.unpack("<I", msg[2])[0]
        self.__logger.debug("Pubishing to : {} Subscribed to: {}".format(self.__server_sub_port,\
                                                                        self.__server_pub_port))


    def __RegisterToServer(self):
        self.__logger.debug("Registering to server")

        server_cmd_socket = SERVER_CONFIG.SRV_CMD_ID 

        reg_cmd = SERVER_CONFIG.REG_CMD + self.__client_type + self.__protocol
        self.__command_socket.send_multipart([server_cmd_socket.encode(), reg_cmd.encode()])
        







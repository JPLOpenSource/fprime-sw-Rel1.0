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

        # Create one socket for sending, one socket for receiving commands(and responses)
        # Two are needed because command_socket_recv is wrapped by a ZMQStream
        #self.__command_socket_send = self.__context.socket(zmq.ROUTER)
        #self.__command_socket_send.setsockopt(zmq.IDENTITY, self.__name)
        #self.__command_socket_send.connect("tcp://localhost:{}".format(server_cmd_port))

        self.__command_socket_recv = self.__context.socket(zmq.ROUTER) 
        self.__command_socket_recv.setsockopt(zmq.IDENTITY, self.__name)
        self.__command_socket_recv.connect("tcp://localhost:{}".format(server_cmd_port))

        # Create Reactor 
        self.__loop = IOLoop.instance()

        # Wrap sockets in ZMQStreams for IOLoop handlers
        #self.__command_socket_recv = ZMQStream(self.__command_socket_recv)

        # Register handlers
        #self.__command_socket_recv.on_recv(self.__HandleCommand)

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

        self.__command_socket_recv.close()
        #self.__command_socket_send.close()
        self.__context.term()

    def __HandleCommand(self, msg): 
        self.__logger.debug("Received Command {}".format(msg))

        if msg[0] == "":
            pass

        # Setup pub/sub ports
        self.__server_pub_port = struct.unpack("<I", msg[1])[0]
        self.__server_sub_port = struct.unpack("<I", msg[2])[0]
        self.__logger.debug("Pubishing to : {} Subscribed to: {}".format(self.__server_sub_port,\
                                                                        self.__server_pub_port))


    def __RegisterToServer(self):
        self.__logger.debug("Registering to server")
       
        reg_cmd = [SERVER_CONFIG.SRV_CMD_ID, SERVER_CONFIG.REG_CMD, self.__client_type, self.__protocol]
        self.__logger.debug(reg_cmd)
        
        self.__command_socket_recv.send_multipart([SERVER_CONFIG.SRV_CMD_ID])
        



if __name__ == "__main__":
    a = Adapter("ps", "flight", 5555)
    a.Start()



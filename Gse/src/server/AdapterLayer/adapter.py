import zmq
import struct

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

        self.__command_socket = self.__context.socket(zmq.DEALER) 
        self.__command_socket.setsockopt(zmq.IDENTITY, self.__name)
        self.__command_socket.connect("tcp://localhost:{}".format(server_cmd_port))

        # Create Reactor 
        self.__loop = IOLoop.instance()

        # Wrap sockets in ZMQStreams for IOLoop handlers
        self.__command_socket = ZMQStream(self.__command_socket)

        # Register handlers
        self.__command_socket.on_recv(self.__HandleCommand)

        self.__registered = False

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
        self.__logger.debug("Received Command {}".format(msg))


        if self.__registered is False: # Anticipate registration response

            # Setup pub/sub ports
            self.__server_pub_port = struct.unpack("<I", msg[1])[0]
            self.__server_sub_port = struct.unpack("<I", msg[2])[0]
            self.__logger.debug("Pubishing to : {} Subscribed to: {}".format(self.__server_sub_port,\
                                                                            self.__server_pub_port))
        else: # Process commands normally
            return_id   = msg[0]
            cmd         = msg[1] 

            if cmd == SERVER_CONFIG.REG_CMD:
                client_name = msg[2] 
                thread = AdapterThread(client_name)



    def __RegisterToServer(self):
        self.__logger.debug("Registering to server")
       
        reg_cmd = [SERVER_CONFIG.REG_CMD, self.__client_type, self.__protocol]
        self.__logger.debug(reg_cmd)
        
        self.__command_socket.send_multipart(reg_cmd)
        



if __name__ == "__main__":
    a = Adapter("ps", "flight", 5555)
    a.Start()



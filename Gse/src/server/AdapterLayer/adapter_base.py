import zmq
from abc import ABCMeta, abstractmethod
import struct

from logging import DEBUG, INFO, ERROR
import threading 
from multiprocessing import Process

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from server.Kernel.interconnect import BindToRandomTcpEndpoint
from utils.logging_util import SetGlobalLoggingLevel, GetLogger
from server.ServerUtils.server_config import ServerConfig

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class AdapterBase(object):
    """
    General adapter class.
    """
    __metaclass__ = ABCMeta
    def __init__(self, protocol, client_name,  to_server_pub_port,\
                                               from_server_sub_port,\
                                               to_client_pub_port,\
                                               from_client_sub_port):

        self.__client_name = client_name
        self.__name = "{}_{}_adapter".format(client_name, protocol)

        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(self.__name,log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        self.__logger.debug("Logger Active")
        self.__logger.debug("to_server_pub_port: {}".format(to_server_pub_port))
        self.__logger.debug("from_server_sub_port: {}".format(from_server_sub_port))
        self.__logger.debug("to_client_pub_port: {}".format(to_client_pub_port))
        self.__logger.debug("from_client_sub_port: {}".format(from_client_sub_port))

        # Adapter Information 
        self.__protocol = protocol
        
        # Zmq Context
        self.__context = zmq.Context()

        # Book Keeping 
        self.__client_connections = {} # Save connections by client ID 

        # Create threads
        self.__from_client_decode_thread = threading.Thread(target=self.__FromClientDecodeThread,\
                                                            args=(self.__name,\
                                                                  self.__context,\
                                                                  from_client_sub_port,\
                                                                  to_server_pub_port))
                        

        self.__to_client_encode_thread = threading.Thread(target=self.__ToClientEncodeThread,\
                                                          args=(self.__name,\
                                                                self.__context,\
                                                                to_client_pub_port,\
                                                                from_server_sub_port))
                                                          

    def Start(self):
        self.__logger.info("Starting adapter")
        self.__from_client_decode_thread.start()
        self.__to_client_encode_thread.start()

    def Quit(self):
        self.__logger.info("Stopping adapter")

        self.__context.term()

    def __FromClientDecodeThread(self, adapter_name, context, from_client_sub_port, to_server_pub_port):
        name = "{}_decode_thread".format(adapter_name)
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        logger = GetLogger(name,log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        logger.debug("Logger Active")


        from_client_sub_socket = context.socket(zmq.ROUTER)
        from_client_sub_socket.bind("tcp://*:{}".format(from_client_sub_port))

        to_server_pub_socket   = context.socket(zmq.DEALER)
        to_server_pub_socket.setsockopt(zmq.IDENTITY, self.__client_name)
        to_server_pub_socket.connect("tcp://localhost:{}".format(to_server_pub_port))


        try:
            while(True):
                # Receive encoded packet
                msg_bundle = from_client_sub_socket.recv_multipart()    
                logger.debug("Received: {}".format(msg_bundle))
                encoded_packet = msg_bundle[1]      # Ignore ID
                                                    # As our sub socket identity is
                                                    # The same as the client

                packet = self.Decode(encoded_packet)
                to_server_pub_socket.send(packet)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                from_client_sub_socket.close()
                to_server_pub_socket.close()
            else:
                raise

    def __ToClientEncodeThread(self, adapter_name, context, to_client_pub_port, from_server_sub_port):
        name = "{}_encode_thread".format(adapter_name)
                        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        logger = GetLogger(name,log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        logger.debug("Logger Active")

        from_server_sub_socket = context.socket(zmq.ROUTER)
        from_server_sub_socket.setsockopt(zmq.IDENTITY, self.__client_name)
        from_server_sub_socket.connect("tcp://localhost:{}".format(from_server_sub_port))

        to_client_pub_socket = context.socket(zmq.DEALER)
        to_client_pub_socket.bind("tcp://*:{}".format(to_client_pub_port)) 

        try:
            while(True):
                msg_bundle = from_server_sub_socket.recv_multipart()
                logger.debug("Received: {}".format(msg_bundle))
                packet      = msg_bundle[1]
                encoded_packet = self.Encode(packet)
                #logger.debug("Sending: {}".format([encoded_packet]))
                to_client_pub_socket.send(encoded_packet)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                to_client_pub_socket.close()
                to_server_sub_socket.close()
            else:
                raise
                 
    @abstractmethod
    def Decode(self, encoded_packet):
        """
        Abstact decode method.
        Returns a pure FPrime packet.
        """
        raise NotImplementedError

    @abstractmethod
    def Encode(self, packet):
        """
        Abstract encode method.
        Returns an encoded FPrime packet.
        """
        raise NotImplementedError
        
if __name__ == "__main__":
    a = Adapter("ps", "flight", 5555)
    a.Start()



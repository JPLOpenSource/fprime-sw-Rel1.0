#===============================================================================
# NAME: adapter_base.py
#
# DESCRIPTION: AdapterBase provides an abstract interface for all ZmqServer plugins.
#
# AUTHOR: David Kooi
#
# EMAIL: david.kooi@nasa.jpl.gov
#        dkooi@ucsc.edu
#
#
# Copyright 2017, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================


import zmq
from abc import ABCMeta, abstractmethod
import struct

from logging import DEBUG, INFO, ERROR
import threading 
from multiprocessing import Process

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import SetGlobalLoggingLevel, GetLogger
from server.ServerUtils.server_config import ServerConfig

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class AdapterBase(object):
    """
    General adapter class.
    @params protocol: Name of the protocol
    @params client_name: Name of the corosponding client.
    @params to_server_pub_port: What server port to publish packets to server.
    @params from_server_sub_port: What port to receive packets from server.
    @params to_client_pub_port: What port to publish packets to client.
    @params from_client_sub_port: What port to receive packets from client.
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
        """
        Startup the threads.
        """

        self.__logger.info("Starting adapter")
        self.__from_client_decode_thread.start()
        self.__to_client_encode_thread.start()

    def Quit(self):
        """
        Quit the threads by terminating the context.
        """
        self.__logger.info("Stopping adapter")

        self.__context.term()

    def __FromClientDecodeThread(self, adapter_name, context, from_client_sub_port, to_server_pub_port):
        """
        Receive encoded packets from the client and decode them.
        """
        name = "{}_decode_thread".format(adapter_name)
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        logger = GetLogger(name,log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        logger.debug("Logger Active")

        # Create the sockets
        from_client_sub_socket = context.socket(zmq.ROUTER) # Subscribe to packets from client
        from_client_sub_socket.bind("tcp://*:{}".format(from_client_sub_port))

        to_server_pub_socket   = context.socket(zmq.DEALER) # Publish packets to server
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

                packet = self.Decode(encoded_packet) # Call the implemented decode method
                to_server_pub_socket.send(packet)

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                from_client_sub_socket.close()
                to_server_pub_socket.close()
            else:
                raise

    def __ToClientEncodeThread(self, adapter_name, context, to_client_pub_port, from_server_sub_port):
        """
        Receive packets from the server and encode them.
        """
        name = "{}_encode_thread".format(adapter_name)
                        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        logger = GetLogger(name,log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        logger.debug("Logger Active")

        # Create sockets
        from_server_sub_socket = context.socket(zmq.ROUTER) # Subscribe to packets from the server
        from_server_sub_socket.setsockopt(zmq.IDENTITY, self.__client_name)
        from_server_sub_socket.connect("tcp://localhost:{}".format(from_server_sub_port))

        to_client_pub_socket = context.socket(zmq.DEALER) # Publish packet to client
        to_client_pub_socket.bind("tcp://*:{}".format(to_client_pub_port)) 

        try:
            while(True):
            
                msg_bundle = from_server_sub_socket.recv_multipart()
                logger.debug("Received: {}".format(msg_bundle))
                packet      = msg_bundle[1] # The first frame contains the senders identifier. We don't need this.
                encoded_packet = self.Encode(packet) # Call the implemented encode function
                logger.debug("Sending: {}".format([encoded_packet]))
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
        


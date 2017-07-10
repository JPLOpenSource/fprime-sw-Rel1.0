import os
import zmq
import threading
import logging

from utils.logging_util import GetLogger
from server_utils.ServerConfig import ServerConfig

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance() 

class  GeneralSubscriptionThread(threading.Thread):
    """
    Defines the required setup for a client subscription thread. 
    I.e: 
        Create a zmq.SUB port to receive 
        Create a zmq.PUB port to send

    @params name: Name of the thread
    @params runnable: The main function of the thread
    @params InitializeKernelPorts: Callback function to set the port numbers of
                                   the publish and subscribe ports
    """
    def __init__(self, name, runnable, context, InitializeKernelPorts):
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, log_path)
        self.__logger.debug("Logger Active") 

        # Setup socket to receive all target messages
        sub_socket = context.socket(zmq.ROUTER)
        try:
            sub_port = sub_socket.bind_to_random_port("tcp://*")
        except zmq.ZMQError as e: 
            self.__logger.error("Unable to bind sub port.")  
            raise e
        self.__logger.debug("Subcription port: {}".format(sub_port))

        # Setup socket to publish to clients
        pub_socket = context.socket(zmq.DEALER)
        try:
            pub_port = pub_socket.bind_to_random_port("tcp://*")
        except zmq.ZMQBindError as e:
            self.__logger.error("Unable to bind pub port.")
            raise e
        self.__logger.debug("Publish port: {}".format(pub_port))

        # Callback the server of the allocated ports
        InitializeKernelPorts(sub_port, pub_port)

        # Initialze class base
        threading.Thread.__init__(self, target=runnable, args=(sub_socket,\
                                  pub_socket, self.__logger))

def FlightSubRunnable(sub_socket, pub_socket, logger):
    """
    Flight client subscription thread. Receives all events, telemetry, and files
    from connected flight clients. After routing, publishes to ground clients. 

    @param sub_socket: Flight client zmq subscription socket 
    @param pub_socket: Ground client zmq publishing socket
    @param logger: This thread's logger
    """

    logger.debug("Entering FlightSubRunnable")

    while True:
        try:
            msg = sub_socket.recv_multipart() 
            logger.debug("Packet Received: {}".format(msg))

            pub_socket.send_multipart(msg)
            logger.debug("Sent packet to sub")
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break
            else:
                raise




    logger.info("Exiting FlightSubRunnable")
    sub_socket.close()
    pub_socket.close()

def GroundSubRunnable(sub_socket, pub_socket, logger):
    """
    Ground client subscription thread. Receives all commands and files
    from connected ground clients.

    @param sub_socket: Ground client zmq subscription socket 
    @param pub_socket: Flight client zmq publishing socket
    @param logger: This thread's logger
    """
    logger.debug("Entering GroundSubRunnable")

    while True:
        try:
            msg = sub_socket.recv_multipart() 
            logger.debug("Packet Received: {}".format(msg))

            pub_socket.send_multipart(msg)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break
            else:
                raise

    logger.info("Exiting GroundSubRunnable")
    sub_socket.close()
    pub_socket.close()


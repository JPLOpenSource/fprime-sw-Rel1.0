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
    def __init__(self, name, runnable, context, InitializeKernelPorts,\
                 SERVER_RUNNING):
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

        # Setup socket to publish to clients
        pub_socket = context.socket(zmq.DEALER)
        try:
            pub_port = pub_socket.bind_to_random_port("tcp://*")
        except zmq.ZMQBindError as e:
            self.__logger.error("Unable to bind pub port.")
            raise e

        InitializeKernelPorts(sub_port, pub_port)

        threading.Thread.__init__(self, target=runnable, args=(sub_socket,\
                                  pub_socket, self.__logger, SERVER_RUNNING))

def FlightSubRunnable(sub_socket, pub_socket, logger, SERVER_RUNNING):
    logger.debug("Entering FlightSubRunnable")

    while SERVER_RUNNING.is_set():
        pass

    logger.info("Exiting FlightSubRunnable")

def GroundSubRunnable(sub_socket, pub_socket, logger, SERVER_RUNNING):
    while SERVER_RUNNING.is_set():
        pass

    logger.info("Exiting GroundSubRunnable")

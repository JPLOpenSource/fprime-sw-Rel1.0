import os
import zmq
import time
import threading
import logging

from itertools import cycle
from logging import DEBUG, INFO
from utils.logging_util import GetLogger
from utils.throughput_analyzer import ThroughputAnalyzer

from server.ServerUtils.server_config import ServerConfig
from RoutingCore.routing_table import RoutingTable 

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance() 

class  GeneralServerIOThread(threading.Thread):
    """
    Defines the required setup for a general server IO thread. 

    @params client_type: "Flight" or "Ground". Case insensitive.
    @params pubsub_type: "Publisher" or "Subscriber. Case insensitive.
    @params InputPortBinder: Function to configure ServerIOThread to use tcp or inproc
    @params OutputPortBinder: Function to configure ServerIOThread to use tcp or inproc
    @params runnable: The main function of the thread
    @params SetEndpoints: Callback function to set the port numbers of
                                   the publish and subscribe ports
    """
    def __init__(self, client_type, pubsub_type, context,\
                                       BindInputEndpoint,\
                                       BindOutputEndpoint,\
                                       SetEndpoints):
        
        # Setup Logger
        name = "{}_{}_IOThread".format(client_type, pubsub_type) 
        self.__name = name
        log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        # Setup socket to receive all target messages
        self.__input_socket = context.socket(zmq.ROUTER)
        try:
            input_endpoint = BindInputEndpoint(self.__input_socket) 
        except zmq.ZMQError as e: 
            self.__logger.error("Unable to bind input endpoint.")  
            raise e
        self.__logger.debug("Input endpoint: {}".format(input_endpoint))

        # Setup socket to publish to clients
        self.__output_socket = context.socket(zmq.ROUTER)
        self.__output_socket.setsockopt(zmq.ROUTER_HANDOVER, 1) # Needed to handle reconnections

        try:
            output_endpoint = BindOutputEndpoint(self.__output_socket) 
        except zmq.ZMQBindError as e:
            self.__logger.error("Unable to bind output endpoint.")
            raise e
        self.__logger.debug("Output endpoint: {}".format(output_endpoint))

        # Callback the server of the allocated endpoints
        SetEndpoints(input_endpoint, output_endpoint)
 
        # Initialze class base
        threading.Thread.__init__(self, target=self.__ServerIORunnable)  
                                 

    def __ServerIORunnable(self):
        """
        Defines the ServerIO thread.  
        """
        self.__logger.debug("Entering Runnable")

        analyzer = ThroughputAnalyzer(self.__name + "_analyzer")
        analyzer.StartAverage()
        while True:
            try:
                
                

                msg = self.__input_socket.recv_multipart() 
                self.__logger.debug("Packet Received: {}".format(msg))

                analyzer.StartInstance()
                self.__output_socket.send_multipart(msg, zmq.NOBLOCK)  
                
                analyzer.SaveInstance()
                analyzer.Increment(1)
                

            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break
                elif e.errno == zmq.EAGAIN:
                    continue
                else:
                    raise

        self.__logger.debug("Exiting Runnable")

        analyzer.SetAverageThroughput()
        analyzer.PrintReports()

        self.__input_socket.close()
        self.__output_socket.close()


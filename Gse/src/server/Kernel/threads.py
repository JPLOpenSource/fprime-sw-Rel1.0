import os
import zmq
import time
import signal
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

    @params client_name: Name of the client which this thread represents.
    @params pubsub_type: "Publisher" or "Subscriber. Case insensitive.
    @params InputPortBinder: Function to configure ServerIOThread to use tcp or inproc
    @params OutputPortBinder: Function to configure ServerIOThread to use tcp or inproc
    @params runnable: The main function of the thread
    @params SetEndpoints: Callback function to set the port numbers of
                                   the publish and subscribe ports
    """
    def __init__(self, client_name, pubsub_type, Interconnect):

        self.__client_name = client_name
        self.__pubsub_type = pubsub_type
        context = zmq.Context.instance()

        # Setup Logger
        name = "{}_{}_IOThread".format(client_name, pubsub_type) 
        self.__name = name
        log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
        

        # Initialze class base
        threading.Thread.__init__(self, target=self.__ServerIORunnable, args=(Interconnect,context))  

        
    def __ServerIORunnable(self, Interconnect, context):
        """
        Defines the ServerIO thread.  
        """
        self.__logger.debug("Entering Runnable")
        self.__logger.debug("ZMQ Context: {}".format(context.underlying))

        # Setup socket to receive
        input_socket = Interconnect.GetInputSocket(context)
        input_socket.setsockopt(zmq.LINGER, 0)
        input_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm')))
        # If ROUTER, set options to allow for reconnections
        if(input_socket.type == zmq.ROUTER):        
            input_socket.setsockopt(zmq.ROUTER_HANDOVER, 1)

        # Attempt bind
        try:
            input_endpoint = Interconnect.BindInputEndpoint(input_socket) 
        except zmq.ZMQError as e: 
            self.__logger.error("Unable to bind input endpoint.")  
            raise e
        self.__logger.debug("Input endpoint: {}".format(input_endpoint))
        self.__logger.debug(input_socket)

        # Setup socket to publish
        output_socket = Interconnect.GetOutputSocket(context)
        output_socket.setsockopt(zmq.LINGER, 0)
        output_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm')))
        # If ROUTER, set options to allow for reconnections
        if(output_socket.type == zmq.ROUTER):        
            output_socket.setsockopt(zmq.ROUTER_HANDOVER, 1)

        # Attempt bind
        try:
            output_endpoint = Interconnect.BindOutputEndpoint(output_socket) 
        except zmq.ZMQBindError as e:
            self.__logger.error("Unable to bind output endpoint.")
            raise e
        self.__logger.debug("Output endpoint: {}".format(output_endpoint))
        self.__logger.debug(output_socket)


        # Set routing commands
        cmd_socket = Interconnect.GetCmdSocket(context)
        cmd_reply_socket = Interconnect.GetCmdReplySocket(context)
        self.__CheckRoutingCommand = Interconnect.GetCheckRoutingCommandFunc()

        # Set the created endpoints
        Interconnect.SetEndpoints(input_endpoint, output_endpoint)


        #analyzer = ThroughputAnalyzer(self.__name + "_analyzer")
        #analyzer.StartAverage()
        
        while True:
            try:
                #analyzer.StartInstance()
                msg = input_socket.recv_multipart(flags=zmq.NOBLOCK) 
                self.__logger.debug("Packet Received: {}".format(msg))

                output_socket.send_multipart(msg, zmq.NOBLOCK)  
                
                #analyzer.SaveInstance()
                #analyzer.Increment(1)

                # Check for incoming routing table command messages
                self.__CheckRoutingCommand(self.__logger, self.__client_name, cmd_socket, cmd_reply_socket)                    

            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    self.__logger.debug("ETERM")
                    break
                elif e.errno == zmq.EAGAIN:
                    continue
                else:
                    raise

        #analyzer.SetAverageThroughput()
        #analyzer.PrintReports()

        input_socket.close()
        output_socket.close()
        if(cmd_socket):
            cmd_socket.close()
        if(cmd_reply_socket):
            cmd_reply_socket.close()
        self.__logger.debug("Exiting Runnable")



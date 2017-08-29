import os
import zmq
import time
import signal
import threading
import logging
from itertools import cycle
from logging import DEBUG, INFO

from utils.logging_util import GetLogger

from utils import throughput_analyzer

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.RoutingCore.routing_table import RoutingTable 

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance() 

class  GeneralServerIOThread(threading.Thread):
    """
    Defines the required setup for a general server IO thread.
    Specific logic is provided by Interconnect.

    @params client_name: Name of the client which this thread represents.
    @params pubsub_type: "Publisher" or "Subscriber. Case insensitive.
    @params Interconnect: Specified internal logic of the IO thread.
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


        # Set routing commands
        cmd_socket = Interconnect.GetCmdSocket(context)
        cmd_reply_socket = Interconnect.GetCmdReplySocket(context)
        CheckRoutingCommand = Interconnect.GetCheckRoutingCommandFunc()

        # Set output_socket details
        SendOutput = Interconnect.GetOutputSocketFunc()

        # Set the created endpoints
        Interconnect.SetEndpoints(input_endpoint, output_endpoint)

        poller = zmq.Poller()
        poller.register(input_socket, zmq.POLLIN)
        poller.register(cmd_socket, zmq.POLLIN)


        test_point = throughput_analyzer.GetTestPoint(self.__name + "_test_point")
        test_point.StartAverage()

        # Wrap while in a try statement so we can catch the ETERM error
        # that occurs when ClientProcess terminates the zmq context
        try:
            while True:
                socks = dict(poller.poll())

                if(input_socket in socks):

                    test_point.StartInstance()

                    msg = input_socket.recv_multipart() 
                    self.__logger.debug("Packet Received: {}".format(msg))
                    SendOutput(self.__logger, msg, output_socket)

                    test_point.Increment(1)
                    test_point.SaveInstance()

                    
                elif(cmd_socket in socks):
                    # Check for incoming routing table command messages
                    CheckRoutingCommand(self.__logger, self.__client_name, input_socket, cmd_socket, cmd_reply_socket)                    



        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__logger.debug("ETERM")
                pass # Continue to exit
            else:
                raise

        test_point.SetAverageThroughput()
        test_point.PrintReports()

        # Close sockets
        input_socket.close()
        output_socket.close()
        if(cmd_socket):
            cmd_socket.close()
        if(cmd_reply_socket):
            cmd_reply_socket.close()
        self.__logger.debug("Exiting Runnable")



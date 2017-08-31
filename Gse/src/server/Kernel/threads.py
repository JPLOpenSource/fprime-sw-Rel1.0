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





class GeneralSubscriberThread(threading.Thread):

    def __init__(self, context, server_sub_port, pub_address):

        self.__sub_socket = context.socket(zmq.ROUTER)
        self.__sub_socket.setsockopt(zmq.LINGER, 0)
        self.__sub_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm')))
        self.__sub_socket.setsockopt(zmq.ROUTER_HANDOVER, 1) # Needed for client reconnect
        self.__sub_socket.bind("tcp://*:{}".format(server_sub_port))

        self.__pub_socket = context.socket(zmq.PUB)
        self.__pub_socket.setsockopt(zmq.LINGER, 0)        
        self.__pub_socket.bind(pub_address)
        
        threading.Thread.__init__(self, target=self.__SubscribeRunnable)

    def __SubscribeRunnable(self):
        try:
            while(True):
                msg = self.__sub_socket.recv_multipart(copy=False)
                self.__pub_socket.send_multipart(msg, copy=False)
        except zmq.ZMQError as e:
            if(e.errno == zmq.ETERM):
                pass
            else:
                raise  

        # Exit
        self.__sub_socket.close()
        self.__pub_socket.close()


class GeneralPublisherThread(threading.Thread):
    def __init__(self, context, client_name, pub_address, server_pub_port)

        self.__client_name = client_name

        self.__sub_socket = context.socket(zmq.SUB)
        self.__sub_socket.setsockopt(zmq.LINGER, 0)
        self.__sub_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm')))
        self.__sub_socket.setsockopt(zmq.ROUTER_HANDOVER, 1) # Needed for client reconnect
        self.__sub_socket.connect(pub_address)
        
        self.__pub_socket = context.socket(zmq.DEALER)
        self.__pub_socket.setsockopt(zmq.LINGER, 0)        
        self.__pub_socket.bind("tcp://*:{}".format(server_pub_port))

        self.__cmd_socket = context.socket(zmq.SUB)
        self.__cmd_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.__cmd_socket.connect(SERVER_CONFIG.ROUTING_TABLE_CMD_ADDRESS)

        self.__cmd_reply_socket = context.socket(zmq.DEALER)
        self.__cmd_reply_socket.connect(SERVER_CONFIG.ROUTING_TABLE_CMD_REPLY_ADDRESS)


        threading.Thread.__init__(self, target=self.__PublishRunnable)

    def __PublishRunnable(self):

        poller = zmq.Poller()
        poller.register(self.__sub_socket, zmq.POLLIN)
        poller.register(self.__cmd_socket, zmq.POLLIN)

        socks = dict(poller.poll())

        if(self.__sub_socket in socks):
            msg = self.__sub_socket.recv_multipart(copy=False)
            self.__pub_socket.send_multipart(msg, copy=False)

        if(self.__cmd_socket in socks):
            cmd_list = cmd_socket.recv_multipart()

            recipient   = cmd_list[0]
            option      = cmd_list[1]
            pub_client  = cmd_list[2] # The publishing client whom to
                                      # subscribe or unsubscribe to.

            if(cmd_list[0] == self.__client_name):
                logger.debug("Command received: {}".format(cmd_list))
                if(option == 'subscribe'):
                    sub_socket.setsockopt(zmq.SUBSCRIBE, pub_client)
                elif(option == 'unsubscribe'):
                    sub_socket.setsockopt(zmq.UNSUBSCRIBE, pub_client) 

            # Ack routing table
            cmd_reply_socket.send(b"{}_pubsub Received".format(client_name))







class  GeneralServerIOThread(threading.Thread):
    """
    Defines the required setup for a general server IO thread.
    Specific logic is provided by Interconnect.

    @params client_name: Name of the client which this thread represents.
    @params pubself.__subtype: "Publisher" or "Subscriber. Case insensitive.
    @params Interconnect: Specified internal logic of the IO thread.
    """
    def __init__(self, client_name, pubself.__subtype, Interconnect):

        self.__client_name = client_name
        self.__pubself.__subtype = pubself.__subtype
        context = zmq.Context.instance()

        # Setup Logger
        name = "{}_{}_IOThread".format(client_name, pubself.__subtype) 
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
        self.__subsocket = Interconnect.GetInputSocket(context)
        self.__subsocket.setsockopt(zmq.LINGER, 0)
        self.__subsocket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm')))
        # If ROUTER, set options to allow for reconnections
        if(self.__subsocket.type == zmq.ROUTER):        
            self.__subsocket.setsockopt(zmq.ROUTER_HANDOVER, 1)

        # Attempt bind
        try:
            self.__subendpoint = Interconnect.BindInputEndpoint(self.__subsocket) 
        except zmq.ZMQError as e: 
            self.__logger.error("Unable to bind input endpoint.")  
            raise e
        self.__logger.debug("Input endpoint: {}".format(self.__subendpoint))

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
        Interconnect.SetEndpoints(self.__subendpoint, output_endpoint)

        poller = zmq.Poller()
        poller.register(self.__subsocket, zmq.POLLIN)
        poller.register(cmd_socket, zmq.POLLIN)


        test_point = throughput_analyzer.GetTestPoint(self.__name + "_test_point")
        test_point.StartAverage()

        # Wrap while in a try statement so we can catch the ETERM error
        # that occurs when ClientProcess terminates the zmq context
        try:
            while True:
                socks = dict(poller.poll())

                if(self.__subsocket in socks):

                    test_point.StartInstance()

                    msg = self.__subsocket.recv_multipart(copy=False) 
                    self.__logger.debug("Packet Received: {}".format(msg))
                    SendOutput(self.__logger, msg, output_socket)

                    test_point.Increment(1)
                    test_point.SaveInstance()

                    
                elif(cmd_socket in socks):
                    # Check for incoming routing table command messages
                    CheckRoutingCommand(self.__logger, self.__client_name, self.__subsocket, cmd_socket, cmd_reply_socket)                    



        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__logger.debug("ETERM")
                pass # Continue to exit
            else:
                raise

        test_point.SetAverageThroughput()
        test_point.PrintReports()

        # Close sockets
        self.__subsocket.close()
        output_socket.close()
        if(cmd_socket):
            cmd_socket.close()
        if(cmd_reply_socket):
            cmd_reply_socket.close()
        self.__logger.debug("Exiting Runnable")



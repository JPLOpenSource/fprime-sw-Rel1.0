import os
import sys
import time
import zmq
import logging
import datetime
import threading

from logging import DEBUG, INFO

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import GetLogger
from ServerUtils.server_config import ServerConfig

from threads import GeneralServerIOThread 
from interconnect import SubscriberThreadEndpoints, PublisherThreadEndpoints

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class ZmqKernel(object):

    def __init__(self, command_port):
        self.__context = zmq.Context()

        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger("zmq_kernel",log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        self.__logger.debug("Logger Active")

        # Setup routing table
        self.__routing_table = {}

        # Set endpoints for Flight subscriber and publisher threads
        self.__flight_sub_thread_endpoints = SubscriberThreadEndpoints()
        self.__flight_pub_thread_endpoints = PublisherThreadEndpoints()

        # Set endpoints for Ground subscriber and publisher threads
        self.__ground_sub_thread_endpoints = SubscriberThreadEndpoints()
        self.__ground_pub_thread_endpoints = PublisherThreadEndpoints()

        # Setup flight subcriber and publisher threads
        client_type   = "Flight"
        pubsub_type   = "Subscribe"
        SetEndpoints  = self.__flight_sub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__flight_sub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__flight_sub_thread_endpoints.GetOutputBinder()

        self.__flight_sub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints) 

        client_type   = "Flight"
        pubsub_type   = "Publish"
        SetEndpoints  = self.__flight_pub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__flight_pub_thread_endpoints.GetInputBinder()
        BindOutput     = self.__flight_pub_thread_endpoints.GetOutputBinder()

          
        self.__flight_pub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints)

        # Setup ground subscriber and publisher threads
        client_type   = "Ground"
        pubsub_type   = "Subscribe"
        SetEndpoints  = self.__ground_sub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__ground_sub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__ground_sub_thread_endpoints.GetOutputBinder()

        self.__ground_sub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints)

        client_type   = "Ground"
        pubsub_type   = "Publish"
        SetEndpoints  = self.__ground_pub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__ground_pub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__ground_pub_thread_endpoints.GetOutputBinder()

        self.__ground_pub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints)
                                 
        # Setup command/status socket
        self.__command_socket = self.__context.socket(zmq.ROUTER)
        try:
            self.__command_socket.bind("tcp://*:{}".format(command_port))
        except ZMQError as e:
            if e.errno == zmq.EADDRINUSE:
                logger.error("Unable to bind command socket to port {}"\
                             .format(command_port))
                raise e

        # Create Reactor 
        self.__loop = IOLoop.instance()
        
        # Wrap sockets in ZMQStreams for IOLoop handlers
        self.__command_socket = ZMQStream(self.__command_socket)

        # Register handlers
        self.__command_socket.on_recv(self.__HandleCommand)

    def GetContext(self):
        """
        Return zmq context.
        """
        return self.__context
    
    def Start(self):
        """
        Start main event loop of the zmq kernel
        """
        try:
            self.__logger.debug("Kernel reactor starting.")
            
            self.__flight_sub_thread.start()
            self.__flight_pub_thread.start()

            self.__ground_sub_thread.start()
            self.__ground_pub_thread.start()

            self.__loop.start()
        except KeyboardInterrupt:
            self.Quit()  
          
    def Quit(self):
        """
        Shut down server
        """
        self.__logger.info("Initiating server shutdown") 

        # Must close all sockets before context terminate
        self.__command_socket.close()

        self.__context.term()

    def __HandleCommand(self, msg):
        """
        Receives a new command message and dispatches the message to the
        proper command handler.
        """
        self.__logger.debug("Command Received: {}".format(msg))
        
        return_id = msg[0]
        cmd       = msg[1] 

        if cmd == 'REG':
            status, server_pub_port, server_sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(return_id, status, server_pub_port, server_sub_port)


    def __HandleRegistration(self, msg):
        """
        Receives a client registration message.
        Returns a tuple containing the registration status, pub, and sub ports 
        """
        name        = msg[2]
        client_type = msg[3]
        proto       = msg[4]
        self.__logger.info("Registering {name} as {client_type} client "
                            "using {proto} protocol."\
                       .format(name=name, client_type=client_type.lower(),\
                               proto=proto))
     
        #TODO: Generate meaningful registration status
        status = 1

        try:
            self.__AddToRoutingTable(name, client_type)
         
            server_pub_port          = self.__GetServerPubPort(client_type) 
            server_sub_port          = self.__GetServerSubPort(client_type) 
        except TypeError:
            status = -1
            server_pub_port = -1
            server_sub_port = -1

        return (status, server_pub_port, server_sub_port)


    def __RegistrationResponse(self, return_id, status, server_pub_port,\
                                                        server_sub_port):
        """
        Send response to the registering client 
        """

        msg = [
               bytes(return_id),\
               bytes(status),\
               bytes(server_pub_port),\
               bytes(server_sub_port)
              ]

        self.__command_socket.send_multipart(msg)

    def __GetServerPubPort(self, client_type):
        """
        Return the publish port based on client_type 
        """
        if   client_type.lower() == "flight":
            return self.__flight_pub_thread_endpoints.GetOutputPort()
        elif client_type.lower() == "ground":
            return self.__ground_pub_thread_endpoints.GetOutputPort()
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))

            raise TypeError
            
    def __GetServerSubPort(self, client_type):
        """
        Based on client_type return the subscription port.
        """
        if   client_type.lower() == "flight":
            return self.__flight_sub_thread_endpoints.GetInputPort()
        elif client_type.lower() == "ground":
            return self.__ground_sub_thread_endpoints.GetInputPort()
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))

            raise TypeError 
            

    def __AddToRoutingTable(self, name, client_type):
        """
        Based on it's type, add client to the routing table. 
        """
        pass
        


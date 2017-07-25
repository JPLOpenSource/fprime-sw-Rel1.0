import os
import sys
import time
import zmq
import logging
import datetime
import thread
import struct
import threading
import traceback
import multiprocessing

from logging import DEBUG, INFO, ERROR 

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import SetGlobalLoggingLevel, GetLogger
from ServerUtils.server_config import ServerConfig

from threads import GeneralServerIOThread 
from interconnect import SubscriberThreadEndpoints, PublisherThreadEndpoints
from RoutingCore.core import RoutingCore

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class ZmqKernel(object):

    def __init__(self, command_port, timeout=None):
        """
        @params command_port: tcp port on which to receive registration and commands
        @params timeout: Quit server after timeout. For unittesting purposes
        """

        self.__context = zmq.Context()

        # Setup Logger
        SetGlobalLoggingLevel(logLevel=INFO, fileLevel=DEBUG, globalLevel=False)
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger("zmq_kernel",log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        self.__logger.debug("Logger Active")

        # Create RoutingCore
        self.__RoutingCore = RoutingCore(self.__context)

        # Set endpoints for Flight subscriber and publisher threads
        self.__flight_sub_thread_endpoints = SubscriberThreadEndpoints()
        self.__flight_pub_thread_endpoints = PublisherThreadEndpoints()

        # Set endpoints for Ground subscriber and publisher threads
        self.__ground_sub_thread_endpoints = SubscriberThreadEndpoints()
        self.__ground_pub_thread_endpoints = PublisherThreadEndpoints()

        # Setup flight subcriber and publisher threads
        client_type   = SERVER_CONFIG.FLIGHT_TYPE
        pubsub_type   = SERVER_CONFIG.SUB_TYPE
        SetEndpoints  = self.__flight_sub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__flight_sub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__flight_sub_thread_endpoints.GetOutputBinder()

        self.__flight_sub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints) 

        client_type   = SERVER_CONFIG.FLIGHT_TYPE
        pubsub_type   = SERVER_CONFIG.PUB_TYPE
        SetEndpoints  = self.__flight_pub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__flight_pub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__flight_pub_thread_endpoints.GetOutputBinder()
 
        self.__flight_pub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints)

        # Setup ground subscriber and publisher threads
        client_type   = SERVER_CONFIG.GROUND_TYPE
        pubsub_type   = SERVER_CONFIG.SUB_TYPE
        SetEndpoints  = self.__ground_sub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__ground_sub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__ground_sub_thread_endpoints.GetOutputBinder()

        self.__ground_sub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints)

        client_type   = SERVER_CONFIG.GROUND_TYPE
        pubsub_type   = SERVER_CONFIG.PUB_TYPE
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

        # Set timeout for unit testing
        if(timeout):
            self.__loop.call_later(timeout, self.__loop.stop)
        
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
            pass # Fall through to quit

        self.Quit()  
          
    def Quit(self):
        """
        Shut down server
        """
        self.__logger.info("Initiating server shutdown") 
    
        self.__RoutingCore.Quit()

        # Must close all sockets before context terminate
        self.__command_socket.close()
        self.__context.term() 
  

    def __HandleCommand(self, msg):
        """
        Receives a new command message and dispatches the message to the
        proper command handler.
        """
        self.__logger.debug("Command Received: {}".format(msg))

        client_name = msg[0]
        cmd         = msg[1].lower()

        if   cmd == SERVER_CONFIG.REG_CMD: 
            status, server_pub_port, server_sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(client_name, status, server_pub_port, server_sub_port)

        elif cmd == SERVER_CONFIG.SUB_CMD: 
            option = SERVER_CONFIG.SUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)
            self.__RoutingCoreConfigurationResponse(client_name, status)

        elif cmd == SERVER_CONFIG.USUB_CMD:
            option = SERVER_CONFIG.USUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)
            self.__RoutingCoreConfigurationResponse(client_name, status)

    def __RoutingCoreConfigurationResponse(self, return_id, status):
        pass#self.__command_socket.send_multipart([return_id, status])

    def __HandleRoutingCoreConfiguration(self, msg, option):
        client_name         = msg[2]
        client_type         = msg[3]
        subscriptions       = msg[4:]


        if(client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE):
            
            if(subscriptions == ['']): # Empty message in zmq means subscribe to all
                self.__RoutingCore.routing_table.ConfigureAllGroundPublishers(option, client_name)
            else:
                self.__RoutingCore.routing_table.ConfigureGroundPublishers(option,\
                                                                   client_name,\
                                                                  subscriptions)
        elif(client_type.lower() == SERVER_CONFIG.GROUND_TYPE):
            if(subscriptions == ['']): # Subscribe to all
                self.__RoutingCore.routing_table.ConfigureAllFlightPublishers(option, client_name)
            else:
                self.__RoutingCore.routing_table.ConfigureFlightPublishers(option,\
                                                                client_name,\
                                                                subscriptions)
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            return -1


        return 1


    def __HandleRegistration(self, msg):
        """
        Receives a client registration message.
        Returns a tuple containing the registration status, pub, and sub ports 
        """
        client_name = msg[0]
        client_type = msg[2]
        proto       = msg[3]
        self.__logger.info("Registering {client_name} as {client_type} client "
                            "using {proto} protocol."\
                       .format(client_name=client_name, client_type=client_type.lower(),\
                               proto=proto))
     
        #TODO: Generate meaningful registration status
        status = 1

        try:
            self.__AddClientToRoutingCore(client_name, client_type)
         
            server_pub_port = self.__GetServerPubPort(client_type) 
            server_sub_port = self.__GetServerSubPort(client_type) 
        except TypeError:
            traceback.print_exc()
            self.__logger.error("Client type: {} not recognized.".format(client_type))

            status = -1
            server_pub_port = -1
            server_sub_port = -1

        return (status, server_pub_port, server_sub_port)


    def __RegistrationResponse(self, return_name, status, server_pub_port,\
                                                        server_sub_port):
        """
        Send response to the registering client 
        """

        msg = [
               bytes(return_name),\
               struct.pack("<I", status),\
               struct.pack("<I", server_pub_port),\
               struct.pack("<I", server_sub_port)
              ]

        self.__logger.debug("Registartion Status  :{}".format(bytes(status)))
        self.__logger.debug("Registration Response: {}".format(msg))
        self.__command_socket.send_multipart(msg)

    def __GetServerPubPort(self, client_type):
        """
        Return the publish port based on client_type 
        """
        if   client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:
            return self.__flight_pub_thread_endpoints.GetOutputPort()
        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:
            return self.__ground_pub_thread_endpoints.GetOutputPort()
        else:
            raise TypeError
            
    def __GetServerSubPort(self, client_type):
        """
        Based on client_type return the subscription port.
        """
        if   client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:
            return self.__flight_sub_thread_endpoints.GetInputPort()
        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:
            return self.__ground_sub_thread_endpoints.GetInputPort()
        else:
            raise TypeError 
            

    def __AddClientToRoutingCore(self, client_name, client_type):
        """
        Based on it's type, add client to the routing table and create
        a PubSubPair. 
        """
        if client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:

            serverIO_subscriber_output_address = self.__flight_sub_thread_endpoints.GetOutputAddress()
            serverIO_publisher_input_address = self.__flight_pub_thread_endpoints.GetInputAddress()

            # Add to routing table
            self.__RoutingCore.routing_table.AddFlightClient(client_name)

        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:
            serverIO_subscriber_output_address = self.__ground_sub_thread_endpoints.GetOutputAddress()
            serverIO_publisher_input_address = self.__ground_pub_thread_endpoints.GetInputAddress()

            # Add to routing table
            self.__RoutingCore.routing_table.AddGroundClient(client_name)

        else:
            raise TypeError

        # Create PubSub pair for client
        self.__RoutingCore.CreatePubSubPair(client_name, client_type,\
                                            serverIO_subscriber_output_address,\
                                            serverIO_publisher_input_address)


        



import os
import sys
import time
import zmq
import logging
import datetime
import thread
import struct
import pickle
import signal
import threading
import traceback
import multiprocessing

from logging import DEBUG, INFO, ERROR 

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import SetGlobalLoggingLevel, GetLogger
from server.ServerUtils.server_config import ServerConfig
from server.AdapterLayer import adapter_utility
from server.AdapterLayer.adapter_process import AdapterProcess

from server.Kernel.threads import GeneralServerIOThread 
from server.Kernel import interconnect
from server.Kernel.interconnect import SubscriberThreadEndpoints, PublisherThreadEndpoints
from server.Kernel.RoutingCore.core import RoutingCore

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class ZmqKernel(object):

    def __init__(self, command_port, console_lvl=INFO, file_lvl=INFO, timeout=None):
        """
        @params command_port: tcp port on which to receive registration and commands
        @params timeout: Quit server after timeout. For unittesting purposes
        """
        self.__context = zmq.Context()

        # Setup Logger
        SetGlobalLoggingLevel(consoleLevel=console_lvl, fileLevel=file_lvl, globalLevel=True)
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
        self.__command_socket.setsockopt(zmq.IDENTITY, SERVER_CONFIG.SRV_CMD_ID)
        try:
            self.__command_socket.bind("tcp://*:{}".format(command_port))
        except zmq.ZMQError as e:
            if e.errno == zmq.EADDRINUSE:
                self.__logger.error("Unable to bind command socket to port {}"\
                             .format(command_port))
                raise e

        # Setup adapter and adapter booking

        self.__reference_adapter_dict    = adapter_utility.LoadAdapters()
        self.__adapter_process_dict      = dict()


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
            self.__logger.debug("Reactor starting.")
            
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
        
        self.__TerminateAdapters()
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

        return_id = msg[0]
        cmd       = msg[1].lower()

        # Register
        if   cmd == SERVER_CONFIG.REG_CMD: 
            status, server_pub_port, server_sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(return_id, status, server_pub_port, server_sub_port)

        # Subscribe
        elif cmd == SERVER_CONFIG.SUB_CMD: 
            option = SERVER_CONFIG.SUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)
            self.__RoutingCoreConfigurationResponse(return_id, status)

        # Unsubscribe
        elif cmd == SERVER_CONFIG.USUB_CMD:
            option = SERVER_CONFIG.USUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)
            self.__RoutingCoreConfigurationResponse(return_id, status)

        # List subscriptions
        elif cmd == SERVER_CONFIG.LIST_CMD:
            client_sub_dict = self.__HandleListSubscription()
            self.__ListSubscriptionResponse(return_id, client_sub_dict)

    def __HandleListSubscription(self):
        return self.__RoutingCore.routing_table.GetAllClientSubscription()

    def __ListSubscriptionResponse(self, return_id, client_sub_dict):

        self.__logger.debug("Sending ListSubscription Response")
        self.__command_socket.send_multipart([return_id, pickle.dumps(client_sub_dict)])

    def __RoutingCoreConfigurationResponse(self, return_id, status):
        #TODO Add Routing config response
        pass#self.__command_socket.send_multipart([return_id, status])

    def __HandleRoutingCoreConfiguration(self, msg, option):
        """
        Handle subscription or unsubscription.
        """

        client_name         = msg[2]
        client_type         = msg[3]
        subscriptions       = msg[4:]

        # Configure Flight Client subscriptions
        if(client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE):
            
            if(subscriptions == ['']): # Empty message in zmq means subscribe to all
                self.__RoutingCore.routing_table.ConfigureAllGroundPublishers(option, client_name)
            else:
                self.__RoutingCore.routing_table.ConfigureGroundPublishers(option,\
                                                                   client_name,\
                                                                  subscriptions)
        # Configure Ground Client subscriptions
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


        return 0


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

            # Get server IO ports
            server_pub_port = self.__GetServerPubPort(client_type) 
            server_sub_port = self.__GetServerSubPort(client_type) 
   
            if(proto.lower() in self.__reference_adapter_dict):
                # Return adapter ports for the client
                server_pub_port, server_sub_port = self.__CreateAdapter(client_type,\
                                                                        client_name,\
                                                                        proto.lower())
         
            elif proto.lower() == "zmq":
                # No adapter needed, use plain server ports
                server_pub_port = self.__GetServerPubPort(client_type) 
                server_sub_port = self.__GetServerSubPort(client_type) 
            else:
                raise TypeError

        except TypeError:
            traceback.print_exc()
            self.__logger.error("Registration Error. Either:")
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            self.__logger.error("Protocol type: {} not recognized".format(proto))

            status = -1
            server_pub_port = 0
            server_sub_port = 0

        return (status, server_pub_port, server_sub_port)

    def __CreateAdapter(self, client_type, client_name, proto):
        # Get ports for the adapter to connect to
        from_server_pub_port = self.__GetServerPubPort(client_type) # Server port publishing to adapter
        to_server_sub_port   = self.__GetServerSubPort(client_type)   # Server port subscribed to adapter
        
        from_client_sub_port = interconnect.GetRandomPort() # Adapter port subscribed to client
        to_client_pub_port   = interconnect.GetRandomPort() # Adapter port publishing to client

        # Get uninstantiated adapter object 
        Adapter = self.__reference_adapter_dict[proto] 
        # Then create an instance 
        adapter = Adapter(proto, client_name, to_server_sub_port, from_server_pub_port,\
                                              to_client_pub_port, from_client_sub_port)
        # Create a process
        process = AdapterProcess(adapter)
        # Save a reference to the process
        self.__adapter_process_dict[proto] = process
        # Now start
        process.start()

        return to_client_pub_port, from_client_sub_port

    def __TerminateAdapters(self):
        for proto in self.__adapter_process_dict:
            self.__adapter_process_dict[proto].terminate()

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

        self.__logger.debug("Registartion Status: {}".format(bytes(status)))
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


        

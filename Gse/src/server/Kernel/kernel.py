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

from utils import logging_util
from utils import throughput_analyzer

from utils.logging_util import GetLogger
from server.Kernel.client_process import ClientProcess

from RoutingCore.core import RoutingCore

# Global server config class
from server.ServerUtils.server_config import ServerConfig
SERVER_CONFIG = ServerConfig.getInstance()


class ZmqKernel(object):

    def __init__(self, command_port, console_lvl=INFO, file_lvl=INFO, tp_on=False,\
                                                                      timeout=None):
        """
        @params command_port: tcp port on which to receive registration and commands
        @params console_lvl: global logging level for console output
        @params file_lvl: global logging level for file output
        @params tp_on: True to log throughput at TestPoints. False to disable
        @params timeout: Quit server after timeout. For unittesting purposes
        """

        self.__context = zmq.Context()

        # Store references to each client process
        self.__client_process_dict = dict()

        # Setup global logging settings
        logging_util.SetGlobalLoggingLevel(consoleLevel=console_lvl, fileLevel=file_lvl,\
                                                                     globalLevel=True)
        # Setup global throughput_analyzer settings
        throughput_analyzer.GlobalToggle(tp_on)
        throughput_analyzer.InitializeFolders()

        # Create logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger("zmq_kernel",log_path, logLevel=DEBUG,\
                                               fileLevel=DEBUG)
        self.__logger.debug("Logger Active")
        self.__logger.debug("PID: {}".format(os.getpid()))

        # Create RoutingCore
        self.__RoutingCore = RoutingCore(self.__context)
                                 
        # Setup command/status socket
        self.__command_socket = self.__context.socket(zmq.ROUTER)
        try:
            self.__command_socket.bind("tcp://*:{}".format(command_port))
        except zmq.ZMQError as e:
            if e.errno == zmq.EADDRINUSE:
                self.__logger.error("Unable to bind command socket to port {}"\
                             .format(command_port))
                raise e

        # Setup ClientProcess kill socket
        # This socket is binds to each ClientProcess.
        # When the server shuts down a kill message is sent to
        # each ClientProcess.
        self.__kill_socket = self.__context.socket(zmq.PUB)
        self.__kill_socket.bind(SERVER_CONFIG.KILL_SOCKET_ADDRESS)

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

            self.__loop.start() 

        except KeyboardInterrupt:
            pass # Fall through to quit

        self.Quit()  
          
    def Quit(self):
        """
        Shut down server
        """
        self.__logger.info("Initiating server shutdown")

        # Send message to all ClientProcesses to exit
        self.__kill_socket.send(b"Exit")

        # Quit the RoutingCore
        self.__RoutingCore.Quit()

        # Must close all sockets before context will terminate
        self.__command_socket.close()
        self.__kill_socket.close()
        self.__context.term() 

  

    def __HandleCommand(self, msg):
        """
        Receives a new command message and dispatches the message to the
        proper command handler.
        """
        self.__logger.debug("Command Received: {}".format(msg))

        return_id = msg[0]
        cmd       = msg[1].lower()

        # Client Register
        if   cmd == SERVER_CONFIG.REG_CMD: 
            status, server_pub_port, server_sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(return_id, status, server_pub_port, server_sub_port)

        # Client subscribe
        elif cmd == SERVER_CONFIG.SUB_CMD: 
            option = SERVER_CONFIG.SUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)
            self.__RoutingCoreConfigurationResponse(return_id, status)

        # Client unsubscribe
        elif cmd == SERVER_CONFIG.USUB_CMD:
            option = SERVER_CONFIG.USUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)
            self.__RoutingCoreConfigurationResponse(return_id, status)

        # List subscriptions
        elif cmd == SERVER_CONFIG.LIST_CMD:
            client_sub_dict = self.__HandleListSubscription()
            self.__ListSubscriptionResponse(return_id, client_sub_dict)

    def __HandleListSubscription(self):
        """
        Gets a dictionary detailing the subscription configuration of 
        all flight and ground clients
        """
        subscription_dict = self.__RoutingCore.routing_table.GetAllClientSubscription()
        return subscription_dict

    def __ListSubscriptionResponse(self, return_id, client_sub_dict):
        """
        Send a serialized subscription dictionary to the client with ID return_id.
        """

        self.__logger.debug("Sending ListSubscription Response")
        self.__command_socket.send_multipart([return_id, pickle.dumps(client_sub_dict)])

    def __RoutingCoreConfigurationResponse(self, return_id, status):
        pass#self.__command_socket.send_multipart([return_id, status])

    def __HandleRoutingCoreConfiguration(self, msg, option):
        """
        Handle subscribe or unsubscribe operation.
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


        # Do not duplicate if the ClientProcess exists
        if client_name in self.__client_process_dict:

            # Return the ports of the created ClientProcess
            server_pub_port = self.__client_process_dict[client_name]['server_pub_port']
            server_sub_port = self.__client_process_dict[client_name]['server_sub_port']
            return (0, server_pub_port, server_sub_port)


        # Attempt to add the registering client ot the RoutingCore
        # If this succeeds the registration was successful.
        try:
            client_process = self.__RoutingCore.CreateClientProcess(client_name, client_type)
            # Create a new process and get it's allocated ports
            server_pub_port = client_process.GetPublisherThreadOutputPort()
            server_sub_port = client_process.GetSubscriberThreadInputPort()
            self.__logger.debug("output port: {}".format(server_pub_port))
            self.__logger.debug("input port: {}".format(server_sub_port))

            # Save a reference to the process and it's allocated ports
            self.__client_process_dict[client_name] = dict()
            self.__client_process_dict[client_name]['process'] = client_process
            self.__client_process_dict[client_name]['server_pub_port'] = server_pub_port
            self.__client_process_dict[client_name]['server_sub_port'] = server_sub_port
            
            # Start the publish and subscribe threads
            client_process.start()

            status = 1 # Successful registration

        except TypeError:
            traceback.print_exc()
            self.__logger.error("Client type: {} not recognized.".format(client_type))

            status = 0
            server_pub_port = 0
            server_sub_port = 0


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

        self.__logger.debug("Registration Status: {}".format(bytes(status)))
        self.__logger.debug("Registration Response: {}".format(msg))
        self.__command_socket.send_multipart(msg)


    def __AddClientToRoutingCore(self, client_name, client_type):
        """
        Based on it's type, add client to the routing table.
        """
        if client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:

            # Add to routing table
            self.__RoutingCore.routing_table.AddFlightClient(client_name)

        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:

            # Add to routing table
            self.__RoutingCore.routing_table.AddGroundClient(client_name)

        else:
            raise TypeError

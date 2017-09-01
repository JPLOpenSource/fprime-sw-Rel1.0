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

from server.AdapterLayer import adapter_utility
from server.Kernel import interconnect
from server.Kernel.threads import GeneralSubscriberThread, GeneralPublisherThread

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

        self.__main_context = zmq.Context()

        # Store references to each client process
        self.__routing_table = dict()
        self.__routing_table[SERVER_CONFIG.FLIGHT_TYPE] = dict()
        self.__routing_table[SERVER_CONFIG.GROUND_TYPE] = dict()
        self.__book_keeping = dict() # Use for storing port numbers

        # Setup adapter and adapter book keeping
        self.__reference_adapter_dict    = adapter_utility.LoadAdapters()
        self.__adapter_process_dict      = dict()

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


        # Create flight and ground subscriber threads
        self.__flight_side_context = zmq.Context(io_threads=1)
        self.__server_flight_sub_port = interconnect.GetRandomPort()
        self.__flight_subscribe_thread = GeneralSubscriberThread(self.__flight_side_context,\
                                                                 SERVER_CONFIG.FLIGHT_TYPE,\
                                                                 self.__server_flight_sub_port,\
                                                                 SERVER_CONFIG.FLIGHT_PUB_ADDRESS)

        self.__ground_side_context = zmq.Context(io_threads=1)
        self.__server_ground_sub_port = interconnect.GetRandomPort()
        self.__ground_subscribe_thread = GeneralSubscriberThread(self.__ground_side_context,\
                                                                 SERVER_CONFIG.GROUND_TYPE,\
                                                                 self.__server_ground_sub_port,
                                                                 SERVER_CONFIG.GROUND_PUB_ADDRESS)


        # Setup routing command socket
        self.__routing_command_socket     = self.__main_context.socket(zmq.PUB)
        self.__routing_command_socket.bind(SERVER_CONFIG.ROUTING_TABLE_CMD_ADDRESS)
        self.__logger.debug("Command socket: {}".format(SERVER_CONFIG.ROUTING_TABLE_CMD_ADDRESS))

        # Set routing command reply socket
        self.__routing_command_reply_socket = self.__main_context.socket(zmq.ROUTER)
        self.__routing_command_reply_socket.setsockopt(zmq.RCVTIMEO, 500) # Timeout after 500 ms
        self.__routing_command_reply_socket.bind(SERVER_CONFIG.ROUTING_TABLE_CMD_REPLY_ADDRESS)
        self.__logger.debug("Command reply socket: {}".format(SERVER_CONFIG.ROUTING_TABLE_CMD_REPLY_ADDRESS))


        # Setup command/status socket
        self.__command_socket = self.__main_context.socket(zmq.ROUTER)
        try:
            self.__command_socket.bind("tcp://*:{}".format(command_port))
        except zmq.ZMQError as e:
            if e.errno == zmq.EADDRINUSE:
                self.__logger.error("Unable to bind command socket to port {}"\
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

            self.__flight_subscribe_thread.start()
            self.__ground_subscribe_thread.start()
            self.__loop.start() 

        except KeyboardInterrupt:
            pass # Fall through to quit

        self.Quit()  
          
    def Quit(self):
        """
        Shut down server
        """
        self.__TerminateAdapters()
        self.__logger.info("Initiating server shutdown")

        # Terminate both contexts to kill all the threads
        self.__flight_side_context.term()
        self.__ground_side_context.term()

        # Must close all sockets before context will terminate
        self.__command_socket.close()
        self.__routing_command_socket.close()
        self.__routing_command_reply_socket.close()
        self.__main_context.term() 

        throughput_analyzer.AggregateTestPoints()

  

    def __HandleCommand(self, msg):
        """
        Receives a new command message and dispatches the message to the
        proper command handler.
        """
        self.__logger.debug("Command Received: {}".format(msg))

        return_id = msg[0]
        cmd       = msg[1]

        # Client Register
        if   cmd == SERVER_CONFIG.REG_CMD: 
            status, server_pub_port, server_sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(return_id, status, server_pub_port, server_sub_port)

        # Client subscribe
        elif cmd == SERVER_CONFIG.SUB_CMD: 
            option = SERVER_CONFIG.SUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)

        # Client unsubscribe
        elif cmd == SERVER_CONFIG.USUB_CMD:
            option = SERVER_CONFIG.USUB_OPTION 
            status = self.__HandleRoutingCoreConfiguration(msg, option)

        # List subscriptions
        elif cmd == SERVER_CONFIG.LIST_CMD:
            client_sub_dict = self.__HandleListSubscription()
            self.__ListSubscriptionResponse(return_id, client_sub_dict)

    def __HandleListSubscription(self):
        """
        Gets a dictionary detailing the subscription configuration of 
        all flight and ground clients
        """
        return self.__routing_table

    def __ListSubscriptionResponse(self, return_id, client_sub_dict):
        """
        Send a serialized subscription dictionary to the client with ID return_id.
        """

        self.__logger.debug("Sending ListSubscription Response")
        self.__command_socket.send_multipart([return_id, pickle.dumps(client_sub_dict)])


    def __HandleRoutingCoreConfiguration(self, msg, option):
        """
        Handle subscribe or unsubscribe operation.
        """
        client_name         = msg[2]
        client_type         = msg[3]
        subscriptions       = msg[4:] # Subscriptions are listed


        self.__logger.info("{} {} to {}".format(option, client_name, subscriptions))

        # Configure subscriptions
        if(client_type == SERVER_CONFIG.FLIGHT_TYPE):
            pub_client_type = SERVER_CONFIG.GROUND_TYPE
        elif(client_type == SERVER_CONFIG.GROUND_TYPE):
            pub_client_type = SERVER_CONFIG.FLIGHT_TYPE
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            return -1

        if(subscriptions == ['']): # Empty message in zmq means subscribe to all
            subscriptions = [pub_client for pub_client in self.__routing_table[pub_client_type]]

        for pub_client in subscriptions:
            if(option == SERVER_CONFIG.USUB_OPTION):
                self.__routing_table[pub_client_type][pub_client].remove(client_name)
            elif(option == SERVER_CONFIG.SUB_OPTION):
                self.__routing_table[pub_client_type][intern(pub_client)].add(client_name)
            
            # Tell receiving_client to subcribe or unsubscribe
            self.__routing_command_socket.send_multipart([client_name.encode(), option.encode(), pub_client.encode()])
            # Wait for response
            try:
                self.__routing_command_reply_socket.recv()
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    self.__logger.warning("No response from {}".format(client_name))
                else:
                    raise

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

        try:

            # If the client already registered we don't need to create another thread.
            # Just return the port numbers.
            if client_name in self.__routing_table:
                server_sub_port = self.__book_keeping[client_name]['sub_port']
                server_pub_port = self.__book_keeping[client_name]['pub_port']
                return (1, server_pub_port, server_sub_port)

            else: # The client is not registered. Create a new dictionary entry
                self.__routing_table[client_type][client_name] = set() # A set of subscribed clients
                self.__book_keeping[client_name] = dict()


            # Based on the client_type create a PublisherThread
            if(client_type == SERVER_CONFIG.FLIGHT_TYPE):

                server_sub_port = self.__server_flight_sub_port
                server_pub_port = interconnect.GetRandomPort()
                pub_thread = GeneralPublisherThread(self.__ground_side_context, client_name, SERVER_CONFIG.GROUND_PUB_ADDRESS,\
                                                                                             server_pub_port)

                pub_thread.start()
                status = 1
            elif(client_type == SERVER_CONFIG.GROUND_TYPE):

                server_sub_port = self.__server_ground_sub_port
                server_pub_port = interconnect.GetRandomPort()
                pub_thread = GeneralPublisherThread(self.__flight_side_context, client_name, SERVER_CONFIG.FLIGHT_PUB_ADDRESS,\
                                                                                             server_pub_port)

                pub_thread.start()

                # Store the port numbers for future reference
                self.__book_keeping[client_name]['pub_port'] = server_pub_port
                self.__book_keeping[client_name]['sub_port'] = server_sub_port

                status = 1 # Successful registration
            else:
                raise TypeError


            # Check if a protocol adapter should be created
            if(proto.lower() in self.__reference_adapter_dict):

                # Create an adapter betweent the client and server.
                # The adapter connects to the ports intended for the client
                # And returns new ports for the client to connect to. 
                server_pub_port, server_sub_port = self.__CreateAdapter(client_type,\
                                                                        client_name,\
                                                                        server_pub_port,\
                                                                        server_sub_port,\
                                                                        proto.lower())
                # Store the new port numbers for future reference
                self.__book_keeping[client_name]['pub_port'] = server_pub_port
                self.__book_keeping[client_name]['sub_port'] = server_sub_port
         
            elif proto.lower() == "zmq":
                pass
            else:
                raise TypeError



        except TypeError:
            traceback.print_exc()
            self.__logger.error("Registration Error. Either:")
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            self.__logger.error("Protocol type: {} not recognized".format(proto))

            status = 0
            server_pub_port = 0
            server_sub_port = 0
       
        return (status, server_pub_port, server_sub_port)

    def __CreateAdapter(self, client_type, client_name, server_pub_port, server_sub_port, proto):
        # Get ports for the adapter to connect to
        from_server_pub_port = server_pub_port # Server port publishing to adapter
        to_server_sub_port   = server_sub_port   # Server port subscribed to adapter
        
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

        # Return new port numbers for the client to connect to 
        return to_client_pub_port, from_client_sub_port

    def __TerminateAdapters(self):
        for proto in self.__adapter_process_dict:
            self.__adapter_process_dict[proto].terminate()

    def __RegistrationResponse(self, return_name, status, server_pub_port,\
                                                        server_sub_port):
        """
        Send response to the registering client.
        """

        # Pack the data as little endian integers to make it convinient
        # for the embedded systems to recieve 
        msg = [
               bytes(return_name),\
               struct.pack("<I", status),\
               struct.pack("<I", server_pub_port),\
               struct.pack("<I", server_sub_port)
              ]

        self.__logger.debug("Registration Status: {}".format(bytes(status)))
        self.__logger.debug("{} registered.".format(return_name))
        self.__logger.debug("{} Server Pub Port {}".format(return_name, server_pub_port))
        self.__logger.debug("{} Server Sub Port {}".format(return_name, server_sub_port))
        self.__command_socket.send_multipart(msg)


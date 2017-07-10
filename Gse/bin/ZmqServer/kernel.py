import os
import sys
import time
import zmq
import logging
import datetime
import threading

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream


from utils.logging_util import GetLogger
from server_utils.ServerConfig import ServerConfig
from kernel_threads import GeneralSubscriptionThread,\
                           FlightSubRunnable, GroundSubRunnable

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class ZmqKernel(object):

    def __init__(self, command_port):
        self.__context = zmq.Context()

        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger("zmq_kernel",log_path)
        self.__logger.debug("Logger Active")

        # Setup routing table
        self.__routing_table = {}

        # Flight and ground client pub/sub port sets
        self.__flight_client_sub_port = None
        self.__flight_client_pub_port = None

        self.__ground_client_sub_port = None
        self.__ground_client_pub_port = None

        # Setup flight and ground subcription threads

        name = "FlightSubscriptionThread"
        self.__flight_sub_thread = GeneralSubscriptionThread(name,\
             FlightSubRunnable, self.__context, self.__SetFlightSubThreadPorts)
 
        name = "GroundSubscriptionThread"
        self.__ground_sub_thread = GeneralSubscriptionThread(name,\
             GroundSubRunnable, self.__context, self.__SetGroundSubThreadPorts)
                    
   
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
        return self.__context
    
    def Start(self):
        """
        Start main event loop of the zmq kernel
        """
        try:
            self.__logger.debug("Kernel reactor started.")
            
            self.__flight_sub_thread.start()
            self.__ground_sub_thread.start()
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
        cmd       = msg[2] # Zmq inserts a delimiting frame at msg index 1

        if cmd == 'REG':
            status, pub_port, sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(return_id, status, pub_port, sub_port)


    def __HandleRegistration(self, msg):
        """
        Receives a client registration message.
        Returns a tuple containing the registration status, pub, and sub ports 
        """
        name        = msg[3]
        client_type = msg[4]
        proto       = msg[5]
        self.__logger.debug("Registering {name} as {client_type} client "
                            "using {proto} protocol."\
                       .format(name=name, client_type=client_type, proto=proto))
     
        #TODO: Generate meaningful registration status
        status = 1
        self.__AddToRoutingTable(name, client_type)

        client_pub_port          = self.__GetClientPubPort(client_type) 
        client_sub_port          = self.__GetClientSubPort(client_type) 
        return (status, client_pub_port, client_sub_port)


    def __RegistrationResponse(self, return_id, status, client_pub_port,\
                                                        client_sub_port):
        """
        Send response to the registering client
        """
        # ZMQ requires the return id followed by an empty byte
        msg = [
               bytes(return_id),\
               b'',\
               bytes(status),\
               bytes(client_pub_port),\
               bytes(client_sub_port)
              ]

        self.__command_socket.send_multipart(msg)

    def __GetClientPubPort(self, client_type):
        """
        Return the publish based on client_type 
        """
        if   client_type.lower() == "flight":
            return self.__flight_client_pub_port
        elif client_type.lower() == "ground":
            return self.__ground_client_pub_port
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            self.__logger.error("Exiting.")
            self.Quit()

    def __GetClientSubPort(self, client_type):
        """
        Based on client_type return the subscription port.
        """
        if   client_type.lower() == "flight":
            return self.__flight_client_sub_port
        elif client_type.lower() == "ground":
            return self.__ground_client_sub_port
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            self.__logger.error("Exiting.")
            self.Quit()

    def __SetGroundSubThreadPorts(self, sub_port, pub_port):
        """
        Sets the pub/sub ports for the ground subscription thread.
        I.e:
            Subscribe to ground clients and
            Publish   to flight clients
        """
        self.__ground_client_sub_port = sub_port
        self.__flight_client_pub_port = pub_port

    def __SetFlightSubThreadPorts(self, sub_port, pub_port):
        """
        Sets the pub/sub ports for the flight subscription thread.
        I.e:
            Subscribe to flight clients and
            Publish   to ground clients
        """
        self.__logger.debug("sub {} pub {}".format(sub_port, pub_port))
        self.__flight_client_sub_port = sub_port
        self.__ground_client_pub_port = pub_port



    def __AddToRoutingTable(self, name, client_type):
        """
        Based on it's type, the client is added to the routing table. 
        """
        pass
        





if __name__ == "__main__":
    cmd_port = sys.argv[1] 
       
    kernel = ZmqKernel(cmd_port) 
    context = kernel.GetContext()
     
    kernel.Start()

    

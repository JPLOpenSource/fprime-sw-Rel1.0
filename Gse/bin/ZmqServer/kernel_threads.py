import os
import zmq
import threading
import logging

from itertools import cycle
from logging import DEBUG, INFO

from server_utils.zhelpers import zpipe
from utils.logging_util import GetLogger
from server_utils.ServerConfig import ServerConfig

from router import RoutingTable 

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance() 

class ForwardingEngine(threading.Thread):
    """
    """
    def __init__(self, ID, context, routing_table, loopback_port):
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(ID, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
        
        self.__routing_table = routing_table

        # Setup thread input pipes 
        i, r = zpipe(context)
        self.__input_pipe = i 
        self.__recv_pipe = r
        

        # Setup loopback socket
        self.__general_subscription_socket = context.socket(zmq.DEALER) 
        self.__general_subscription_socket.connect("tcp://localhost:{}"\
                                                   .format(loopback_port))

        # Initialze class base
        threading.Thread.__init__(self, target=self.__ForwardingRunnable)

    def GetInput(self):
        return self.__input_pipe

    def __ForwardingRunnable(self):
        try:
            while(True):

                msg = self.__recv_pipe.recv_multipart()
                self.__logger.debug("Received: {}".format(msg))

                publisher_id = msg[0]
                
                for client_id in self._routing_table[publisher_id]:
                    self.__general_subscription_socket.send_multipart([\
                                                                        bytes(client_id),\
                                                                        msg[1:]\
                                                                      ])
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__recv_pipe.close()
                self.__input_pipe.close()
            else:
                raise


class GeneralLoadBalancerThread(threading.Thread):
    """
    """
    def __init__(self, name, context, routing_table, general_sub_port):
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        # Setup thread input
        i, r = zpipe(context)
        self.__input_pipe = i
        self.__recv_pipe = r
        
        # Create all forwarding engines
        self.__forwarding_engines = [ForwardingEngine('1', context, routing_table, general_sub_port)]
        # Store their input socket in a cycle
        self.__engine_inputs = []
        for e in self.__forwarding_engines:
            self.__engine_inputs.append(e.GetInput())
        self.__engine_inputs = cycle(self.__engine_inputs)

        # Setup broker to send messages to forwarding engines
        self.__broker = context.socket(zmq.ROUTER)
        self.__broker.bind("inproc://loadbalancer")

        # Initialze class base
        threading.Thread.__init__(self, target=self.__LBRunnable)
    
    def GetInput(self):
        return self.__input_pipe

    def __LBRunnable(self):
        self.__logger.debug("Starting")

        try:

            while(True): 
                msg = self.__recv_pipe.recv_multipart() 
                self.__logger.debug("Received: {}".format(msg))

                self.__engine_inputs.next().send_multipart(msg) 

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__recv_pipe.close()
            else:
                raise


class  GeneralSubscriptionThread(threading.Thread):
    """
    Defines the required setup for a client subscription thread. 

    @params name: Name of the thread
    @params runnable: The main function of the thread
    @params InitializeKernelPorts: Callback function to set the port numbers of
                                   the publish and subscribe ports
    """
    def __init__(self, client_type, context, InitializeKernelPorts):

        name = "{}_SubscriptionThread".format(client_type)
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        # Setup socket to receive all target messages
        self.__sub_socket = context.socket(zmq.ROUTER)
        try:
            sub_port = self.__sub_socket.bind_to_random_port("tcp://*")
        except zmq.ZMQError as e: 
            self.__logger.error("Unable to bind sub port.")  
            raise e
        self.__logger.debug("Subcription port: {}".format(sub_port))

        # Setup socket to publish to clients
        self.__pub_socket = context.socket(zmq.DEALER)
        try:
            pub_port = self.__pub_socket.bind_to_random_port("tcp://*")
        except zmq.ZMQBindError as e:
            self.__logger.error("Unable to bind pub port.")
            raise e
        self.__logger.debug("Publish port: {}".format(pub_port))

        # Callback the server of the allocated ports
        InitializeKernelPorts(sub_port, pub_port)

        # Create an instance of the routing table
        self.__routing_table = RoutingTable.getInstance() 
        publisher_table = self.__routing_table.GetPublisherTable(client_type)

        # Create and start router loadbalancer
        name = "{}_Loadbalancer".format(client_type)
        self.__loadbalancer = GeneralLoadBalancerThread(name, context,\
                                                      publisher_table, sub_port)
        self.__loadbalancer.start()


        # Initialze class base
        threading.Thread.__init__(self, target=self.__SubscriptionRunnable)  
                                 

    def __SubscriptionRunnable(self):
        """
        Client subscription thread. 

        @param sub_socket: Client subscription socket 
        @param pub_socket: Client publishing socket
        @param logger: This thread's logger
        """

        logger.debug("Entering SubscriptionRunnable")

        while True:
            try:
                msg = self.__sub_socket.recv_multipart() 
                logger.debug("Packet Received: {}".format(msg))

    
                #self.__pub_socket.send_multipart(msg, zmq.NOBLOCK) 
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break
                if e.errno == zmq.EAGAIN:
                    continue
                else:
                    raise


        logger.info("Exiting FlightSubRunnable")
        sub_socket.close()
        pub_socket.close()


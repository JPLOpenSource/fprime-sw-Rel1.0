import os
import zmq
import time
import signal
import threading
import logging
from logging import DEBUG, INFO

from utils.logging_util import GetLogger
from utils import throughput_analyzer

# Global server config class
from server.ServerUtils.server_config import ServerConfig
SERVER_CONFIG = ServerConfig.getInstance() 



class GeneralSubscriberThread(threading.Thread):
    """
    A subscriber_thread receives packets from flight or ground clients
    on it's ROUTER socket. The packets are published from a PUB socket
    to publisher_threads. 
    """

    def __init__(self, context, client_type, server_sub_port, pub_address):
        """
        A thread that receives packets from clients.
        @params context: ZMQ context.
        @params client_type: Type of client
        @params server_sub_port: What port the server is listening on.
        @params pub_address: What address to publish packets to.
        """

        # Setup Logger
        name = "{}_SubscribeThread".format(client_type) 
        self.__name = name
        log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        self.__sub_socket = context.socket(zmq.ROUTER)
        self.__sub_socket.setsockopt(zmq.LINGER, 0) # Immediatly close socket
        self.__sub_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm'))) # Set zmq msg buffer size.
                                                                                                          # This is how many msgs to 
                                                                                                          # buffer before msgs are dropped.
        self.__sub_socket.setsockopt(zmq.ROUTER_HANDOVER, 1) # Needed for client reconnect
        self.__sub_socket.bind("tcp://*:{}".format(server_sub_port))

        self.__pub_socket = context.socket(zmq.PUB)
        self.__pub_socket.setsockopt(zmq.LINGER, 0) # Immediatly close socket
        self.__pub_socket.bind(pub_address)
        self.__logger.debug("Pub socket connected to {}".format(pub_address))
        
        threading.Thread.__init__(self, target=self.__SubscribeRunnable)

    def __SubscribeRunnable(self):
        """
        The main loop of the thread.
        """
        # Setup logger
        self.__logger.debug("Starting Runnable")
        test_point = throughput_analyzer.GetTestPoint(self.__name + "_test_point")
        test_point.StartAverage() # Start timing the total lifetime

        # Wait until a message is received before receiving
        poller = zmq.Poller()
        poller.register(self.__sub_socket, zmq.POLLIN)

        try:
            while(True):
                socks = dict(poller.poll()) # Block until msg is received
                if(self.__sub_socket in socks):

                    test_point.StartInstance() # Start timing message recv and send latency

                    msg = self.__sub_socket.recv_multipart(copy=False) # Do not copy the message
                    self.__pub_socket.send_multipart(msg, copy=False)  # This tells zmq to that the application
                                                                       # does not need to know the contents of the msg frames. 
                                                                       # (Because we are just passing it to the PUB socket)

                    test_point.SaveInstance() # Stop timer
                    test_point.Increment(1) # Increment the total number of msgs sent

        except zmq.ZMQError as e:
            if(e.errno == zmq.ETERM):
                self.__logger.debug("ETERM received")
                pass
            else:
                raise  

        # Exit
        test_point.SetAverageThroughput() # Stop timing the total lifetime
        test_point.PrintReports()         # Print reports to file
        self.__sub_socket.close()
        self.__pub_socket.close()


class GeneralPublisherThread(threading.Thread):
    """
    A publisher_thread receives packets from a subscriber thread through it's SUB socket.
    The packets are sent through a DEALER socket to a corrosponding client. The client
    only receives packets whose sender_name is prefixed to the packet message and that client
    is subscribed to the sender.
    """
    def __init__(self, context, client_name, pub_address, server_pub_port):
        """
        GeneralPublisherThread constructor.

        @params context: Zmq context
        @params client_name: Name of the client who received messages from this publisher
        @params pub_address: Address of the internal packet publisher_thread.
        @params server_pub_port: Port number for a client to connect to.f
        """

        # Setup Logger
        name = "{}_PublishThread".format(client_name) 
        self.__name = name
        log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        self.__client_name = client_name

        self.__sub_socket = context.socket(zmq.SUB)
        self.__sub_socket.setsockopt(zmq.LINGER, 0) # Immidiatly close socket
        self.__sub_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm'))) # Set zmq msg buffer size
                                                                                                          # This is how many msgs to 
                                                                                                          # Buffer before msgs are dropped
        self.__sub_socket.connect(pub_address)
        self.__logger.debug("Sub Socket conneced to {}".format(pub_address))
        
        self.__pub_socket = context.socket(zmq.DEALER)
        self.__pub_socket.setsockopt(zmq.LINGER, 0) # Immediatly close socket
        self.__pub_socket.bind("tcp://*:{}".format(server_pub_port))

        self.__cmd_socket = context.socket(zmq.SUB) # Socket that listens for subscription commands from the kernel
        self.__cmd_socket.setsockopt(zmq.SUBSCRIBE, '') # Receive all commands from the kernel
        self.__cmd_socket.connect(SERVER_CONFIG.ROUTING_TABLE_CMD_ADDRESS)

        self.__cmd_reply_socket = context.socket(zmq.DEALER) # Socket that replies to the kernel
        self.__cmd_reply_socket.connect(SERVER_CONFIG.ROUTING_TABLE_CMD_REPLY_ADDRESS)


        threading.Thread.__init__(self, target=self.__PublishRunnable)

    def __PublishRunnable(self):
        """
        Main loop of the thread.
        """
        self.__logger.debug("Starting Runnable")

        # Select between the two sockets
        poller = zmq.Poller()
        poller.register(self.__sub_socket, zmq.POLLIN)
        poller.register(self.__cmd_socket, zmq.POLLIN)

        # Create a test_point to record latency and throughput
        test_point = throughput_analyzer.GetTestPoint(self.__name + "_test_point")
        test_point.StartAverage() # Start timing the total lifetime

        try:
            while(True):

                socks = dict(poller.poll()) # Block until a msg is received

                if(self.__sub_socket in socks): # Packet received
                    test_point.StartInstance() # Start timing message recv and send latency

                    msg = self.__sub_socket.recv_multipart()
                    self.__pub_socket.send(msg[1], copy=False) # First part of message is the sender_name
                                                               # We only need to send the fprime packet

                    test_point.SaveInstance() # Stop the timer for recv and send latency
                    test_point.Increment(1) # Increase number of messages processsed

                if(self.__cmd_socket in socks): # A command from the kernel is received
                    self.__logger.debug("Received")
                    cmd_list = self.__cmd_socket.recv_multipart()

                    recipient   = cmd_list[0]
                    option      = cmd_list[1]
                    pub_client  = cmd_list[2] # The publishing client whom to
                                              # subscribe or unsubscribe to.

                    if(cmd_list[0] == self.__client_name): # Check if the message is addressed to us
                        self.__logger.debug("Command received: {}".format(cmd_list))
                        if(option == SERVER_CONFIG.SUB_OPTION): # Command is to subscribe
                            self.__logger.debug("Setting sub")
                            self.__sub_socket.setsockopt(zmq.SUBSCRIBE, pub_client) # Set the socket option to subscribe to a publisher
                        elif(option == SERVER_CONFIG.USUB_OPTION):
                            self.__logger.debug("Setting usub")
                            self.__sub_socket.setsockopt(zmq.UNSUBSCRIBE, pub_client) # Set the socket option to unsubscribe from a publisher

                    # Ack routing table
                    self.__cmd_reply_socket.send(b"{}_pubsub Received".format(self.__client_name))
        
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__logger.debug("ETERM received")
                pass
            else:
                raise

        # Exit
        test_point.SetAverageThroughput() # Stop timing the total lifetime
        test_point.PrintReports() # Print reports to file

        # Close sockets
        self.__sub_socket.close()
        self.__pub_socket.close()
        self.__cmd_socket.close()
        self.__cmd_reply_socket.close()





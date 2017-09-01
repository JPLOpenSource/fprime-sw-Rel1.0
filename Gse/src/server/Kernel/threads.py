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

    def __init__(self, context, client_type, server_sub_port, pub_address):
        # Setup Logger
        name = "{}_SubscribeThread".format(client_type) 
        self.__name = name
        log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        self.__sub_socket = context.socket(zmq.ROUTER)
        self.__sub_socket.setsockopt(zmq.LINGER, 0)
        self.__sub_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm')))
        self.__sub_socket.setsockopt(zmq.ROUTER_HANDOVER, 1) # Needed for client reconnect
        self.__sub_socket.bind("tcp://*:{}".format(server_sub_port))

        self.__pub_socket = context.socket(zmq.PUB)
        self.__pub_socket.setsockopt(zmq.LINGER, 0)        
        self.__pub_socket.bind(pub_address)
        self.__logger.debug("Pub socket connected to {}".format(pub_address))
        
        threading.Thread.__init__(self, target=self.__SubscribeRunnable)

    def __SubscribeRunnable(self):
        self.__logger.debug("Starting Runnable")
        test_point = throughput_analyzer.GetTestPoint(self.__name + "_test_point")
        test_point.StartAverage()

        poller = zmq.Poller()
        poller.register(self.__sub_socket, zmq.POLLIN)

        try:
            while(True):
                socks = dict(poller.poll())
                if(self.__sub_socket in socks):

                    test_point.StartInstance()

                    msg = self.__sub_socket.recv_multipart(copy=False)
                    self.__pub_socket.send_multipart(msg, copy=False)
                   
                    test_point.SaveInstance()
                    test_point.Increment(1)

        except zmq.ZMQError as e:
            if(e.errno == zmq.ETERM):
                self.__logger.debug("ETERM received")
                pass
            else:
                raise  

        # Exit
        test_point.SetAverageThroughput()
        test_point.PrintReports()
        self.__sub_socket.close()
        self.__pub_socket.close()


class GeneralPublisherThread(threading.Thread):
    def __init__(self, context, client_name, pub_address, server_pub_port):
        # Setup Logger
        name = "{}_PublishThread".format(client_name) 
        self.__name = name
        log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        self.__client_name = client_name

        self.__sub_socket = context.socket(zmq.SUB)
        self.__sub_socket.setsockopt(zmq.LINGER, 0)
        self.__sub_socket.setsockopt(zmq.RCVHWM, int(SERVER_CONFIG.get('settings', 'server_socket_hwm')))
        self.__sub_socket.connect(pub_address)
        self.__logger.debug("Sub Socket conneced to {}".format(pub_address))
        
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
        self.__logger.debug("Starting Runnable")

        poller = zmq.Poller()
        poller.register(self.__sub_socket, zmq.POLLIN)
        poller.register(self.__cmd_socket, zmq.POLLIN)

        test_point = throughput_analyzer.GetTestPoint(self.__name + "_test_point")
        test_point.StartAverage()

        try:
            while(True):
                socks = dict(poller.poll())

                if(self.__sub_socket in socks):
                    test_point.StartInstance()

                    msg = self.__sub_socket.recv_multipart()
                    self.__pub_socket.send(msg[1], copy=False)

                    test_point.SaveInstance()
                    test_point.Increment(1)

                if(self.__cmd_socket in socks):
                    self.__logger.debug("Received")
                    cmd_list = self.__cmd_socket.recv_multipart()

                    recipient   = cmd_list[0]
                    option      = cmd_list[1]
                    pub_client  = cmd_list[2] # The publishing client whom to
                                              # subscribe or unsubscribe to.

                    if(cmd_list[0] == self.__client_name):
                        self.__logger.debug("Command received: {}".format(cmd_list))
                        if(option == SERVER_CONFIG.SUB_OPTION):
                            self.__logger.debug("Setting sub")
                            self.__sub_socket.setsockopt(zmq.SUBSCRIBE, pub_client)
                        elif(option == SERVER_CONFIG.USUB_OPTION):
                            self.__logger.debug("Setting usub")
                            self.__sub_socket.setsockopt(zmq.UNSUBSCRIBE, pub_client) 

                    # Ack routing table
                    self.__cmd_reply_socket.send(b"{}_pubsub Received".format(self.__client_name))
        
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__logger.debug("ETERM received")
                pass
            else:
                raise


        test_point.SetAverageThroughput()
        test_point.PrintReports()

        self.__sub_socket.close()
        self.__pub_socket.close()
        self.__cmd_socket.close()
        self.__cmd_reply_socket.close()





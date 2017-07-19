import os
import sys
import time
import zmq
import logging
import datetime
import thread
import threading
import multiprocessing

from logging import DEBUG, INFO, ERROR 

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import SetLevel, GetLogger
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
        SetLevel(logLevel=INFO, fileLevel=INFO, globalLevel=True)
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
        client_type   = "Flight"
        pubsub_type   = "Subscriber"
        SetEndpoints  = self.__flight_sub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__flight_sub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__flight_sub_thread_endpoints.GetOutputBinder()

        self.__flight_sub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints) 

        client_type   = "Flight"
        pubsub_type   = "Publisher"
        SetEndpoints  = self.__flight_pub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__flight_pub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__flight_pub_thread_endpoints.GetOutputBinder()
 
        self.__flight_pub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints)

        # Setup ground subscriber and publisher threads
        client_type   = "Ground"
        pubsub_type   = "Subscriber"
        SetEndpoints  = self.__ground_sub_thread_endpoints.GetEndpointSetter()
        BindInput     = self.__ground_sub_thread_endpoints.GetInputBinder()
        BindOutput    = self.__ground_sub_thread_endpoints.GetOutputBinder()

        self.__ground_sub_thread = GeneralServerIOThread(client_type, pubsub_type,\
                     self.__context, BindInput, BindOutput, SetEndpoints)

        client_type   = "Ground"
        pubsub_type   = "Publisher"
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
        
        return_id = msg[0]
        cmd       = msg[1] 

        if   cmd == 'REG':
            status, server_pub_port, server_sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(return_id, status, server_pub_port, server_sub_port)

        elif cmd == 'SUB':
            status = self.__HandleSubscription(msg)
            self.__RoutingCoreConfigurationResponse(return_id, status)

        elif cmd == 'USUB':
            pass

    def __RoutingCoreConfigurationResponse(self, return_id, status):
        pass#self.__command_socket.send_multipart([return_id, status])

    def __HandleSubscription(self, msg):
        client_name         = msg[2]
        client_type         = msg[3]
        subscriptions       = msg[4:]
        
        option = "subscribe"
        if(client_type.lower() == "flight"):
            
            publisher_dict = self.__RoutingCore.routing_table.GetPublisherTable("ground")
            if(subscriptions == ['']): # Empty message in zmq means subscribe to all
                self.__RoutingCore.routing_table.ConfigureAll(option, client_name, publisher_dict)
            else:
                self.__RoutingCore.routing_table.ConfigureFlightToGround(option,\
                                                                   client_name,\
                                                                  subscriptions)
        elif(client_type.lower() == "ground"):
            
            publisher_dict = self.__RoutingCore.routing_table.GetPublisherTable("flight")
            if(subscriptions == ['']):
                self.__RoutingCore.routing_table.ConfigureAll(option, client_name, publisher_dict)
            else:
                self.__RoutingCore.routing_table.ConfigureGroundToFlight(option,\
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
        client_name = msg[2]
        client_type = msg[3]
        proto       = msg[4]
        self.__logger.info("Registering {client_name} as {client_type} client "
                            "using {proto} protocol."\
                       .format(client_name=client_name, client_type=client_type.lower(),\
                               proto=proto))
     
        #TODO: Generate meaningful registration status
        status = 1

        try:
            self.__AddClientToRoutingCore(client_name, client_type)
         
            server_pub_port          = self.__GetServerPubPort(client_type) 
            server_sub_port          = self.__GetServerSubPort(client_type) 
        except TypeError:
            self.__logger.error("Client type: {} not recognized.".format(client_type))

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
            raise TypeError 
            

    def __AddClientToRoutingCore(self, client_name, client_type):
        """
        Based on it's type, add client to the routing core. 
        """

        if client_type.lower() == "flight":
            serverIO_subscriber_output_address = self.__flight_sub_thread_endpoints.GetOutputAddress()
            serverIO_publisher_input_address = self.__flight_pub_thread_endpoints.GetInputAddress()

            # Add to routing table
            self.__RoutingCore.routing_table.AddFlightClient(client_name)

        elif client_type.lower() == "ground":
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
        

class TestKernel:

    @classmethod
    def setup_class(cls):
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        cls.logger = GetLogger("KERNEL_UNIT_TEST",log_path, logLevel=DEBUG,\
                                               fileLevel=ERROR)
        cls.logger.debug("Logger Active")



        cmd_port = 5555 
        timeout  = 15
        cls.k = ZmqKernel(cmd_port, timeout)  
        kernel_thread = threading.Thread(target=cls.k.Start)

        # Create 'clients'
        cls.flight1_name = "Flight1"
        cls.flight2_name = "Flight2"
        cls.ground1_name = "Ground1"
        cls.ground2_name = "Ground2"

        cls.k._ZmqKernel__AddClientToRoutingCore(cls.flight1_name, "Flight")
        cls.k._ZmqKernel__AddClientToRoutingCore(cls.flight2_name, "Flight")
        cls.k._ZmqKernel__AddClientToRoutingCore(cls.ground1_name, "Ground")
        cls.k._ZmqKernel__AddClientToRoutingCore(cls.ground2_name, "Ground")

        context = zmq.Context()
        # Get Server's Flight and Ground publish and subscribe ports
        server_flight_publish_port = cls.k._ZmqKernel__GetServerPubPort("flight")                
        server_flight_subscribe_port = cls.k._ZmqKernel__GetServerSubPort("flight")

        server_ground_publish_port = cls.k._ZmqKernel__GetServerPubPort("ground")
        server_ground_subscribe_port = cls.k._ZmqKernel__GetServerSubPort("ground")
        
        # Setup flight sockets 
        cls.flight1_send = context.socket(zmq.DEALER) # Send telemetry to ground
        cls.flight1_send.setsockopt(zmq.IDENTITY, cls.flight1_name)
        cls.flight1_send.connect("tcp://localhost:{}".format(server_flight_subscribe_port))
        #
        cls.flight1_recv = context.socket(zmq.ROUTER) # Receive commands from ground
        cls.flight1_recv.setsockopt(zmq.IDENTITY, cls.flight1_name)
        cls.flight1_recv.setsockopt(zmq.RCVTIMEO, 2)
        cls.flight1_recv.connect("tcp://localhost:{}".format(server_flight_publish_port))

        # Setup ground sockets
        cls.ground1_recv = context.socket(zmq.ROUTER) # Receive telemetry from flight
        cls.ground1_recv.setsockopt(zmq.IDENTITY, cls.ground1_name)
        cls.ground1_recv.setsockopt(zmq.RCVTIMEO, 2)
        cls.ground1_recv.connect("tcp://localhost:{}".format(server_ground_publish_port))
        #
        cls.ground1_send = context.socket(zmq.DEALER) # Send commands from ground
        cls.ground1_send.setsockopt(zmq.IDENTITY, cls.ground1_name)
        cls.ground1_send.connect("tcp://localhost:{}".format(server_ground_subscribe_port))

        # Create server command port
        cls.cmd_send = context.socket(zmq.DEALER)
        cls.cmd_send.connect("tcp://localhost:{}".format(cmd_port))

        kernel_thread.start()
        time.sleep(2)

    
    @classmethod
    def teardown_class(cls):
        pass
        #cls.k.stop()
#        loop = cls.k._ZmqKernel__loop
#        loop.add_callback(loop.stop)

    def Test_GroundSubThreadInputPort(self):  
        ep_port = self.k._ZmqKernel__ground_sub_thread_endpoints.GetInputPort() # Endpoint port
        k_port = self.k._ZmqKernel__GetServerSubPort("ground")                  # Kernel Port 
        assert ep_port == k_port

    def Test_GroundSubThreadOutputAddress(self):
        PASSED = True

        ep_port  = self.k._ZmqKernel__ground_sub_thread_endpoints.GetOutputAddress()

        ps_pair1  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground1_name)
        r_port1   = ps_pair1.serverIO_subscriber_output_address  

        ps_pair2 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground2_name)
        r_port2   = ps_pair2.serverIO_subscriber_output_address

        assert ep_port == r_port1
        assert ep_port == r_port2
       

    def Test_GroundPubThreadOutputPort(self):
        ep_port = self.k._ZmqKernel__ground_pub_thread_endpoints.GetOutputPort()
        k_port  = self.k._ZmqKernel__GetServerPubPort("ground")

        assert ep_port == k_port
    
    def Test_GroundPubThreadInputAddress(self):
        PASSED = True 

        ep_port  = self.k._ZmqKernel__ground_pub_thread_endpoints.GetInputAddress()
        
        ps_pair1  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground1_name)
        r_port1   = ps_pair1.serverIO_publisher_input_address  

        ps_pair2  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground2_name)
        r_port2   = ps_pair2.serverIO_publisher_input_address
        
        assert ep_port == r_port1
        assert ep_port == r_port2


    def Test_FlightSubThreadInputPort(self):
        ep_port = self.k._ZmqKernel__flight_sub_thread_endpoints.GetInputPort()
        k_port = self.k._ZmqKernel__GetServerSubPort("flight")

        assert ep_port == k_port

    def Test_FlightSubThreadOutputAddress(self):
        PASSED = True 

        ep_port  = self.k._ZmqKernel__flight_sub_thread_endpoints.GetOutputAddress()

        ps_pair1  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight1_name)
        r_port1   = ps_pair1.serverIO_subscriber_output_address  

        ps_pair2 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight2_name)
        r_port2   = ps_pair2.serverIO_subscriber_output_address

        assert ep_port == r_port1
        assert ep_port == r_port2
       

    def Test_FlightPubThreadOutputPort(self):
        ep_port = self.k._ZmqKernel__flight_pub_thread_endpoints.GetOutputPort()
        k_port  = self.k._ZmqKernel__GetServerPubPort("flight")

        assert ep_port == k_port

    def Test_FlightPubThreadInputAddress(self):
        ep_port = self.k._ZmqKernel__flight_pub_thread_endpoints.GetInputAddress()

        ps_pair1 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight1_name)
        r_port1  = ps_pair1.serverIO_publisher_input_address

        ps_pair2 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight2_name)
        r_port2  = ps_pair2.serverIO_publisher_input_address

        assert ep_port == r_port1
        assert ep_port == r_port2


    def Test_XSubPacketBrokerAddress(self):
        flight_broker = self.k._ZmqKernel__RoutingCore._RoutingCore__FlightPacketBroker
        ground_broker = self.k._ZmqKernel__RoutingCore._RoutingCore__GroundPacketBroker

        flight_broker_xsub_address = flight_broker.GetInputAddress()
        ground_broker_xsub_address = ground_broker.GetInputAddress()


        # Test against flight PubSubPairs
        ps_pair1    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight1_name)
        xs_address1 = ps_pair1.broker_subscriber_input_address 

        ps_pair2    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight2_name)
        xs_address2 = ps_pair2.broker_subscriber_input_address

        assert flight_broker_xsub_address == xs_address1 
        assert flight_broker_xsub_address == xs_address2 

    
        # Test against ground PubSubPairs
        ps_pair1    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground1_name)
        xs_address1 = ps_pair1.broker_subscriber_input_address

        ps_pair2    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground2_name)
        xs_address2 = ps_pair2.broker_subscriber_input_address

        assert ground_broker_xsub_address == xs_address1
        assert ground_broker_xsub_address == xs_address2



    def TestXPubPacketBrokerAddress(self):
        flight_broker = self.k._ZmqKernel__RoutingCore._RoutingCore__FlightPacketBroker
        ground_broker = self.k._ZmqKernel__RoutingCore._RoutingCore__GroundPacketBroker

        flight_broker_xpub_address = flight_broker.GetOutputAddress()
        ground_broker_xpub_address = ground_broker.GetOutputAddress()

        # Test against flight PubSubPairs
        ps_pair1    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight1_name)
        xp_address1 = ps_pair1.broker_publisher_output_address 

        ps_pair2    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight2_name)
        xp_address2 = ps_pair2.broker_publisher_output_address 

        assert ground_broker_xpub_address == xp_address1
        assert ground_broker_xpub_address == xp_address2

        # Test against ground PubSubPairs
        ps_pair1    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground1_name)
        xp_address1 = ps_pair1.broker_publisher_output_address 

        ps_pair2    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground2_name)
        xp_address2 = ps_pair2.broker_publisher_output_address 

        assert flight_broker_xpub_address == xp_address1
        assert flight_broker_xpub_address == xp_address2




    def Test_AllGroundCommandsToFlight(self):
        """
        Test flight client subscribing to multiple ground clients.
        """
    
        # Subscribe flight client 1 to all ground clients
        pub_dict = self.k._ZmqKernel__RoutingCore.routing_table.GetPublisherTable("ground")
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAll("subscribe",\
                                                                self.flight1_name, pub_dict)

        time.sleep(2)

        # Send Flight1 a command from the Ground1
        cmd1 = "Command 1"
        self.ground1_send.send_multipart([cmd1.encode()])

        try:
            msg = self.flight1_recv.recv_multipart()
            print msg

            assert msg[1] == cmd1

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print("Recv Timeout. Expected a command for flight client.") 
                assert False
            else:
                raise 

        # Send FlightClient1 a command from Ground2
        cmd2 = "Command 2"
        self.ground1_send.send_multipart([cmd2.encode()])

        try:
            msg = self.flight1_recv.recv_multipart()
            print msg
 
            assert msg[1] == cmd2

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print("Recv Timeout. Expected a command for flight client.") 
                assert False
            else:
                raise 




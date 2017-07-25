import zmq
import time
import struct
import threading

from logging import DEBUG, ERROR

from ServerUtils.server_config import ServerConfig
from Kernel.kernel import ZmqKernel
from utils.logging_util import GetLogger

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class TestKernel:

    @classmethod
    def setup_class(cls):
        # Setup Logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        cls.logger = GetLogger("KERNEL_UNIT_TEST",log_path, logLevel=DEBUG,\
                                               fileLevel=ERROR)
        cls.logger.debug("Logger Active")

        cmd_port = 5555 
        timeout_s  = 27
        cls.k = ZmqKernel(cmd_port, timeout_s)  
        kernel_thread = threading.Thread(target=cls.k.Start)

        # Create 'clients'
        cls.flight1_name = "Flight1"
        cls.flight2_name = "Flight2"

        cls.ground1_name = "Ground1"
        cls.ground2_name = "Ground2"

        cls.cmd_client_name = "CmdClient"
        cls.subtest_flight_client_name = "FlightSubClient"
        cls.subtest_ground_client_name = "GroundSubClient"


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
        timeout_ms = 10

        # Flight1
        cls.flight1_send = context.socket(zmq.DEALER) # Send telemetry to ground
        cls.flight1_send.setsockopt(zmq.IDENTITY, cls.flight1_name)
        cls.flight1_send.connect("tcp://localhost:{}".format(server_flight_subscribe_port))
        #
        cls.flight1_recv = context.socket(zmq.ROUTER) # Receive commands from ground
        cls.flight1_recv.setsockopt(zmq.IDENTITY, cls.flight1_name)
        cls.flight1_recv.setsockopt(zmq.RCVTIMEO, timeout_ms)
        cls.flight1_recv.connect("tcp://localhost:{}".format(server_flight_publish_port))
        # Flight2
        cls.flight2_send = context.socket(zmq.DEALER) # Send telemetry to ground
        cls.flight2_send.setsockopt(zmq.IDENTITY, cls.flight2_name)
        cls.flight2_send.connect("tcp://localhost:{}".format(server_flight_subscribe_port))
        #
        cls.flight2_recv = context.socket(zmq.ROUTER) # Receive commands from ground
        cls.flight2_recv.setsockopt(zmq.IDENTITY, cls.flight2_name)
        cls.flight2_recv.setsockopt(zmq.RCVTIMEO, timeout_ms)
        cls.flight2_recv.connect("tcp://localhost:{}".format(server_flight_publish_port))



        # Setup ground sockets

        # Ground1
        cls.ground1_recv = context.socket(zmq.ROUTER) # Receive telemetry from flight
        cls.ground1_recv.setsockopt(zmq.IDENTITY, cls.ground1_name)
        cls.ground1_recv.setsockopt(zmq.RCVTIMEO, timeout_ms)
        cls.ground1_recv.connect("tcp://localhost:{}".format(server_ground_publish_port))
        #
        cls.ground1_send = context.socket(zmq.DEALER) # Send commands from ground
        cls.ground1_send.setsockopt(zmq.IDENTITY, cls.ground1_name)
        cls.ground1_send.connect("tcp://localhost:{}".format(server_ground_subscribe_port))
        # Ground2
        cls.ground2_recv = context.socket(zmq.ROUTER) # Receive telemetry from flight
        cls.ground2_recv.setsockopt(zmq.IDENTITY, cls.ground2_name)
        cls.ground2_recv.setsockopt(zmq.RCVTIMEO, timeout_ms)
        cls.ground2_recv.connect("tcp://localhost:{}".format(server_ground_publish_port))
        #
        cls.ground2_send = context.socket(zmq.DEALER) # Send commands from ground
        cls.ground2_send.setsockopt(zmq.IDENTITY, cls.ground2_name)
        cls.ground2_send.connect("tcp://localhost:{}".format(server_ground_subscribe_port))


        # Create server command port
        cls.cmd_client = context.socket(zmq.DEALER)
        cls.cmd_client.setsockopt(zmq.IDENTITY, cls.cmd_client_name)
        cls.cmd_client.connect("tcp://localhost:{}".format(cmd_port))


        # Create subtest flight client 
        cls.subtest_flight_client = context.socket(zmq.DEALER)
        cls.subtest_flight_client.setsockopt(zmq.IDENTITY, cls.subtest_flight_client_name)
        cls.subtest_flight_client.connect("tcp://localhost:{}".format(cmd_port))


        # Create subtest ground client 
        cls.subtest_ground_client = context.socket(zmq.DEALER)
        cls.subtest_ground_client.setsockopt(zmq.IDENTITY, cls.subtest_ground_client_name)
        cls.subtest_ground_client.connect("tcp://localhost:{}".format(cmd_port))


        kernel_thread.start()
        time.sleep(2)

    
    def setUp(self):
        time.sleep(1)

    def Test_Subcription(self):

        # Unsubscribe all from subtest clients 
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAllFlightPublishers("unsubscribe",\
                                                                    self.subtest_ground_client_name)

        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAllGroundPublishers("unsubscribe",\
                                                                    self.subtest_flight_client_name)

        # Subscribe Ground Client
        self.subtest_ground_client.send_multipart([b"SUB", self.subtest_ground_client_name.encode(),\
                                                   b"GROUND", b""])  
        time.sleep(1) # Allow subcription message to reach

        flight_pubs = self.k._ZmqKernel__RoutingCore.routing_table.GetPublisherTable("Flight")
        for flight_name in flight_pubs:
            assert self.subtest_ground_client_name in flight_pubs[flight_name]


        # Subscribe Flight Client
        self.subtest_flight_client.send_multipart([b"SUB", self.subtest_flight_client_name.encode(),\
                                                   b"FLIGHT", b""])
        time.sleep(1)

        ground_pubs = self.k._ZmqKernel__RoutingCore.routing_table.GetPublisherTable("Ground")
        for ground_name in ground_pubs:
            assert self.subtest_flight_client_name in ground_pubs[ground_name]



    def Test_GroundSubThreadInputPort(self):  
        """
        Test GroundSubscriberThread input port.
        """
        ep_port = self.k._ZmqKernel__ground_sub_thread_endpoints.GetInputPort() # Endpoint port
        k_port = self.k._ZmqKernel__GetServerSubPort("ground")                  # Kernel Port 
        assert ep_port == k_port

    def Test_GroundSubThreadOutputAddress(self):
        """
        Test GroundSubcriberThread output address.
        """
        PASSED = True

        ep_port  = self.k._ZmqKernel__ground_sub_thread_endpoints.GetOutputAddress()

        ps_pair1  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground1_name)
        r_port1   = ps_pair1.serverIO_subscriber_output_address  

        ps_pair2 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground2_name)
        r_port2   = ps_pair2.serverIO_subscriber_output_address

        assert ep_port == r_port1
        assert ep_port == r_port2
       

    def Test_GroundPubThreadOutputPort(self):
        """
        Test GroundPublisherThread output port.
        """
        ep_port = self.k._ZmqKernel__ground_pub_thread_endpoints.GetOutputPort()
        k_port  = self.k._ZmqKernel__GetServerPubPort("ground")

        assert ep_port == k_port
    
    def Test_GroundPubThreadInputAddress(self):
        """
        Test GroundPublisherThread input address.
        """
        ep_port  = self.k._ZmqKernel__ground_pub_thread_endpoints.GetInputAddress()
        
        ps_pair1  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground1_name)
        r_port1   = ps_pair1.serverIO_publisher_input_address  

        ps_pair2  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.ground2_name)
        r_port2   = ps_pair2.serverIO_publisher_input_address
        
        assert ep_port == r_port1
        assert ep_port == r_port2


    def Test_FlightSubThreadInputPort(self):
        """
        Test FlightSubscriberThread input port.
        """
        ep_port = self.k._ZmqKernel__flight_sub_thread_endpoints.GetInputPort()
        k_port = self.k._ZmqKernel__GetServerSubPort("flight")

        assert ep_port == k_port

    def Test_FlightSubThreadOutputAddress(self):
        """
        Test FlightSubscriberThread output address.
        """
        ep_port  = self.k._ZmqKernel__flight_sub_thread_endpoints.GetOutputAddress()

        ps_pair1  = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight1_name)
        r_port1   = ps_pair1.serverIO_subscriber_output_address  

        ps_pair2 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight2_name)
        r_port2   = ps_pair2.serverIO_subscriber_output_address

        assert ep_port == r_port1
        assert ep_port == r_port2
       

    def Test_FlightPubThreadOutputPort(self):
        """
        Test FlightPublisherThread output port.
        """
        ep_port = self.k._ZmqKernel__flight_pub_thread_endpoints.GetOutputPort()
        k_port  = self.k._ZmqKernel__GetServerPubPort("flight")

        assert ep_port == k_port

    def Test_FlightPubThreadInputAddress(self):
        """
        Test FlightPublisherThread input address.
        """
        ep_port = self.k._ZmqKernel__flight_pub_thread_endpoints.GetInputAddress()

        ps_pair1 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight1_name)
        r_port1  = ps_pair1.serverIO_publisher_input_address

        ps_pair2 = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.flight2_name)
        r_port2  = ps_pair2.serverIO_publisher_input_address

        assert ep_port == r_port1
        assert ep_port == r_port2


    def Test_XSubPacketBrokerAddress(self):
        """
        Test PacketBroker XSUB addresses.
        """
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
        """
        Test PacketBroker XPUB addresses.
        """
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


    def Test_ClientRegistration(self):
        """
        Test client registration.
        """
        real_sub_port = self.k._ZmqKernel__ground_sub_thread_endpoints.GetInputPort()
        real_pub_port = self.k._ZmqKernel__ground_pub_thread_endpoints.GetOutputPort()

        print("Real Sub: {}".format(real_sub_port))
        print("Real Pub: {}".format(real_pub_port))

        # Send a registration call
        self.cmd_client.send_multipart([b"REG", b"GROUND", b"ZMQ"])  

        try:
            msg = self.cmd_client.recv_multipart()
            print msg
            status   = struct.unpack('<I',msg[0])[0]
            pub_port = struct.unpack('<I', msg[1])[0]
            sub_port = struct.unpack('<I', msg[2])[0]
            print("Received: Pub {} Sub {}".format(pub_port, sub_port))
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print("Registration reply not received")
                assert False
            else:
                raise

        assert int(status)   == 1
        assert real_sub_port == int(sub_port)
        assert real_pub_port == int(pub_port)

        # Check client's PubSubPair exists within routing core
        s_pair    = self.k._ZmqKernel__RoutingCore.GetPubSubPair(self.cmd_client_name)

    def Test_FlightClientSubscriptionChange(self):

        # Unsubscribe flight1 from all
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAllGroundPublishers("unsubscribe",\
                                                            self.flight1_name) 

         # Subscribe flight1 to ground1
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureGroundPublishers("subscribe",\
                                                            self.flight1_name, [self.ground1_name]) 

        # Unsubscribe flight1 to ground1
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureGroundPublishers("unsubscribe",\
                                                            self.flight1_name, [self.ground1_name]) 


        time.sleep(1)
        cmd = "Do This"
        # Send from ground1
        self.ground1_send.send_multipart([cmd.encode()])
        try:
            msg = self.flight1_recv.recv_multipart()
            print "Unexpected Message Received." 
            assert False 
            

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print("No message received")
                assert True 
            else:
                raise 

        # Subscribe again to ground1
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureGroundPublishers("subscribe",\
                                                            self.flight1_name, [self.ground1_name]) 
        
        time.sleep(1)
        cmd = "Do Something Else"
        # Send from ground1
        self.ground1_send.send_multipart([cmd.encode()])
        try:
            msg = self.flight1_recv.recv_multipart()
            assert True 
            print "Message Received." 

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print("No message received")
                assert False 
            else:
                raise 


        # Clear routing table
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAllGroundPublishers("unsubscribe",\
                                                                    self.flight1_name)

        # Subscribe to ground2
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureGroundPublishers("subscribe",\
                                                            self.flight1_name, [self.ground2_name]) 

        time.sleep(1)

        cmd = "Ground2 Cmd"
        # Send from ground1
        self.ground2_send.send_multipart([cmd.encode()])
        try:
            msg = self.flight1_recv.recv_multipart()
            assert True 
            print "Message Received." 

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print("No message received")
                assert False 
            else:
                raise 

        # Clear routing table
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAllFlightPublishers("unsubscribe",\
                                                                    self.flight1_name)
        time.sleep(1)
        try:
            msg = self.flight1_recv.recv_multipart()
            assert False 
            print "Message Received." 

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print("No message received")
                assert True 
            else:
                raise 



    def Test_AllGroundCommandsToFlight(self):
        """
        Test a flight client subscribing to multiple ground clients.
        """
    
        # Subscribe flight client 1 to all ground clients 
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAllGroundPublishers("subscribe",\
                                                                self.flight1_name)

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

    def Test_AllFlightTelemToGround(self):
        """
        Test a ground client subscribing to multiple flight clients.
        """

        # Subscribe to all
        self.k._ZmqKernel__RoutingCore.routing_table.ConfigureAllFlightPublishers("subscribe",\
                                                                self.ground1_name)

        time.sleep(2)

        # Send Ground1 telemetry from Flight1
        tlm1 = "Data1"
        self.flight1_send.send_multipart([tlm1.encode()])

        try:
            msg = self.ground1_recv.recv_multipart()
            print msg

            assert msg[1] == tlm1

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print(" Recv Timeout. Expected telemetry for ground client.")
                assert False
            else:
                raise

        # Send Ground1 telemetry from Flight2
        tlm2 = "Data2"
        self.flight2_send.send_multipart([tlm2.encode()])

        try:
            msg = self.ground1_recv.recv_multipart()
            print msg

            assert msg[1] == tlm2

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                print(" Recv Timeout. Expected telemetry for ground client.")
                assert False
            else:
                raise



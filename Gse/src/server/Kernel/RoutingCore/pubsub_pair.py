import zmq
import threading
from logging import DEBUG, INFO
from utils.logging_util import GetLogger
from utils.throughput_analyzer import ThroughputAnalyzer

from server.ServerUtils.server_config import ServerConfig

SERVER_CONFIG = ServerConfig.getInstance()


def ForwardToBroker(client_name, input_socket, pub_socket):
    """
    Thread of control for forwarding packets towards a broker.
    Consumes packets from a SubscriberServerIOThread.
    Forwards packets to a broker.

    @params client_name: Name of pubsub pair assigned to a client
    @params input_socket: Socket to receive packets from X-Client Subscriber thread.
    @params pub_socket: Socket to output packets to X-PacketBroker.
    """
    # Setup logger
    name = "{}_PubSubPair_PacketForwarder".format(client_name)
    log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
    logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=INFO)
    logger.debug("Logger Active")
    logger.debug("Entering Runnable")

    try:
        analyzer = ThroughputAnalyzer()
        analyzer.Start()
        while(True):
            # Read from serverIO subscriber 
            msg = input_socket.recv_multipart()
            logger.debug("Received: {}".format(msg))

            # Send to broker
            packet = msg[1] # Extract packet from zmq frame
            pub_socket.send_multipart([client_name, packet]) # Publish with client's name prefixed
            analyzer.Increment(1)

    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            input_socket.close()
            pub_socket.close()
            logger.debug("Exiting Runnable")
            analyzer.Stop()
            logger.debug("Message Throughput: {} msg/s".format(analyzer.Get()))
 

def ReceiveFromBroker(client_name, output_socket, sub_socket, cmd_socket, cmd_reply_socket):
    """
    Thread of control for receiveing packets from a broker
    Consumes packets from a broker.
    Forwards packets to a PublisherServerIOThread

    @params client_name: Name of pubsub pair assigned to a client
    @params output_socket: Socket to output packets to X-Client Publisher thread
    @params sub_socket: Socket to receive packets from X-PacketBroker
    @params cmd_socket: Socket to receive commands from the Routing Table
    """
    # Setup logger
    name = "{}_PubSubPair_PacketReceiver".format(client_name)
    log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
    logger = GetLogger(name, log_path, logLevel=DEBUG, fileLevel=INFO)
    logger.debug("Logger Active")
    logger.debug("Entering Runnable")

    # Setup poller so we can handle both packets and routing commands
    poller = zmq.Poller()
    poller.register(sub_socket, zmq.POLLIN)
    poller.register(cmd_socket, zmq.POLLIN)

    try:
        analyzer = ThroughputAnalyzer()
        analyzer.Start()
        while(True):

            socks = dict(poller.poll(0))
        
            if sub_socket in socks:
                # Receive from broker
                msg = sub_socket.recv_multipart()
                logger.debug("Received: {}".format(msg))

                packet = msg[1] # Extract packet
             
                # Send to serverIO publisher 
                output_socket.send_multipart([packet])
                analyzer.Increment(1)

            if cmd_socket in socks:
                cmd_list = cmd_socket.recv_multipart()

                recipient   = cmd_list[0]
                option      = cmd_list[1]
                pub_client  = cmd_list[2] # The publishing client whom to
                                          # subscribe or unsubscribe to.

                if(cmd_list[0] == client_name):
                    logger.debug("Command received: {}".format(cmd_list))
                    if(option == 'subscribe'):
                        sub_socket.setsockopt(zmq.SUBSCRIBE, pub_client)
                    elif(option == 'unsubscribe'):
                        sub_socket.setsockopt(zmq.UNSUBSCRIBE, pub_client) 

                    # Ack routing table
                    cmd_reply_socket.send(b"Received")


                        
    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            output_socket.close()
            sub_socket.close()
            cmd_socket.close()
            cmd_reply_socket.close()
            logger.debug("Exiting Runnable")
            analyzer.Stop()
            logger.debug("Message Throughput: {} msg/s".format(analyzer.Get()))



class PubSubPair(object):
    """
    A 'shadow' representation of a client.
    
    @params name: Name of the client's pubsub pair.
    @params context: zmq context
    @params router_command_address: Inproc address of router command socket
    @params serverIO_subscriber_output_address: Inproc address of X-Client
            subscriber thread.
    @params serverIO_publisher_input_address: Inproc address of X-Client 
            publisher thread.
    @params broker_subscriber_input_address: Inproc address of X-PacketBroker
            XSUB socket.
    @params broker_publisher_output_address: Inproc address of X-PacketBroker
            XPUB socket.
    """
    def __init__(self, client_name, context, routing_table_command_address,\
                                      routing_table_command_reply_address,\
                                      serverIO_subscriber_output_address,\
                                      serverIO_publisher_input_address,\
                                      broker_subscriber_input_address,\
                                      broker_publisher_output_address):

        # Make addresses available for testing purposes
        self.routing_table_command_address = routing_table_command_address 
        self.routing_table_command_reply_address = routing_table_command_reply_address
        self.serverIO_subscriber_output_address = serverIO_subscriber_output_address
        self.serverIO_publisher_input_address = serverIO_publisher_input_address
        self.broker_subscriber_input_address = broker_subscriber_input_address
        self.broker_publisher_output_address = broker_publisher_output_address

        # Setup Logger
        self.__client_name = client_name
        self.__log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(client_name, self.__log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
        
        # Setup input socket to consume subcriber thread output
        input_socket = context.socket(zmq.ROUTER)
        input_socket.setsockopt(zmq.IDENTITY, client_name)
        input_socket.connect(serverIO_subscriber_output_address)

        # Setup output socket to produce for publisher thread input
        output_socket = context.socket(zmq.DEALER)
        output_socket.setsockopt(zmq.IDENTITY, client_name)
        output_socket.connect(serverIO_publisher_input_address)

        # Setup publishing socket to produce for broker subscription 
        pub_socket = context.socket(zmq.PUB)
        pub_socket.setsockopt(zmq.IDENTITY, client_name)
        pub_socket.connect(broker_subscriber_input_address)

        # Setup subscribing socket to consume from broker publishing
        sub_socket = context.socket(zmq.SUB)
        sub_socket.connect(broker_publisher_output_address)

        # Setup command socket to receive subscription commands from the router
        cmd_socket = context.socket(zmq.SUB)
        cmd_socket.setsockopt(zmq.SUBSCRIBE, '')
        cmd_socket.connect(routing_table_command_address)

        # Setup command reply socket to ACK the routing table
        cmd_reply_socket = context.socket(zmq.DEALER)
        cmd_reply_socket.connect(routing_table_command_reply_address)

        # Create forwarding and receiving threads
        self.__PacketForwarder = threading.Thread(target=ForwardToBroker,\
                          args=(client_name, input_socket, pub_socket))

        self.__PacketReceiver  = threading.Thread(target=ReceiveFromBroker,\
                      args=(client_name, output_socket, sub_socket, cmd_socket, cmd_reply_socket))
        
        
    def Start(self):
        self.__PacketForwarder.start()
        self.__PacketReceiver.start()


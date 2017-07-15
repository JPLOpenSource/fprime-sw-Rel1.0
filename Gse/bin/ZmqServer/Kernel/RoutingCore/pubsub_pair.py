
import zmq

from utils.logging_util import GetLogger

from ServerUtils.server_config import ServerConfig

SERVER_CONFIG = ServerConfig.getInstance()


def ForwardToBroker(pair_name, input_socket, pub_socket):
    """
    Thread of control for forwarding packets towards a broker.
    """
    # Setup logger
    name = "{}_PacketForwarder".format(pair_name)
    logger = GetLogger(name, logLevel=DEBUG, fileLevel=INFO)

    try:
        while(True):
            # Read from serverIO subscriber 
            msg = input_socket.recv_multipart()
            # Send to broker
            pub_socket.send_multipart(msg)

    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            input_socket.close()
            pub_socket.close()
 

def ReceiveFromBroker(pair_name, output_socket, sub_socket, cmd_socket):
    """
    Thread of control for receiveing packets from a broker
    """
    # Setup logger
    name = "{}_PacketReceiver".format(pair_name)
    logger = GetLogger(name, logLevel=DEBUG, fileLevel=INFO)

    try:
        while(True):
            # Receive from broker
            msg = pub_socket.recv_multipart()

            # Send to serverIO publisher 
            output_socket.send_multipart(msg)
            
    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            output_socket.close()
            sub_socket.close()






class PubSubPair(object):
    """
    """
    def __init__(self, name, context, serverIO_subscriber_output_address,\
                                      serverIO_publisher_input_address,\
                                      broker_subscriber_input_address,\
                                      broker_publisher_output_address):
        # Setup Logger
        self.__name = name
        self.__log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, self.__log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
        
        # Setup input socket to consume subcriber thread output
        self.__input_socket = context.socket(zmq.ROUTER)
        self.__input_socket.connect(serverIO_subscriber_output_address)

        # Setup output socket to produce for publisher thread input
        self.__output_socket = context.socket(zmq.DEALER)
        self.__output_socket.connect(serverIO_publisher_input_address)

        # Setup publishing socket to produce for broker subscription 
        self.__pub_socket = context.socket(zmq.PUB)
        self.__pub_socket.connect(broker_subscriber_input_address)

        # Setup subscribing socket to consume from broker publishing
        self.__sub_socket = context.socket(zmq.SUB)
        self.__sub_socket.connect(broker_publisher_output_address)

        # TODO Make cmd socket


        # Create forwarding and receiving threads
        PacketForwarder = threading.Thread(target=ForwardToBroker,\
                          args=(name, input_socket, pub_socket)

        PacketReceiver  = threading.Thread(target=ReceiveFromBroker,\
                          args=(name, output_socket, sub_socket, cmd_socket)










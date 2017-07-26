import zmq
import threading
from logging import DEBUG, INFO

from utils.logging_util import GetLogger

from ServerUtils.server_config import ServerConfig
from Kernel.interconnect import BindToRandomInprocEndpoint
from pubsub_pair import PubSubPair
from packet_broker import PacketBroker
from routing_table import RoutingTable


# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class RoutingCore(object):
    """
    """

    def __init__(self, context):
        # Setup Logger
        name = "RoutingCore"
        self.__log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, self.__log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
   
        self.__context = context
        self.__pubsub_pair_dict = {} 

        self.__FlightPacketBroker = PacketBroker(SERVER_CONFIG.FLIGHT_TYPE, self.__context)
        self.__GroundPacketBroker = PacketBroker(SERVER_CONFIG.GROUND_TYPE, self.__context)

        self.routing_table = RoutingTable(context)

        self.__FlightPacketBroker.Start()
        self.__GroundPacketBroker.Start()

    def Quit(self):
        self.routing_table.Quit()


    def GetPubSubPair(self, client_name):
        return self.__pubsub_pair_dict[client_name]

    def CreatePubSubPair(self, client_name, client_type, serverIO_subscriber_output_address,\
                                                         serverIO_publisher_input_address):

        # Do not duplicate if the PubSubPair exists
        if client_name in self.__pubsub_pair_dict:
            return

        if client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:
            broker_subscriber_input_address = self.__FlightPacketBroker.GetInputAddress() 
            broker_publisher_output_address = self.__GroundPacketBroker.GetOutputAddress() 

        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:
            broker_subscriber_input_address = self.__GroundPacketBroker.GetInputAddress() 
            broker_publisher_output_address = self.__FlightPacketBroker.GetOutputAddress() 
        else:
            self.__logger.info("Type: {}".format(client_type.lower()))

            raise TypeError  
           
        self.__logger.debug("Creating PubSubPair")
        self.__logger.debug("Client Type: {}".format(client_type))
        self.__logger.debug("Broker Input: {}".format(broker_subscriber_input_address))
        self.__logger.debug("Broker Output: {}".format(broker_publisher_output_address))

        routing_table_command_address       = self.routing_table.GetCommandSocketAddress()
        routing_table_command_reply_address = self.routing_table.GetCommandReplySocketAddress()

        psp = PubSubPair(client_name, self.__context,
                                    routing_table_command_address,\
                                    routing_table_command_reply_address,\
                                    serverIO_subscriber_output_address,\
                                    serverIO_publisher_input_address,\
                                    broker_subscriber_input_address,\
                                    broker_publisher_output_address)

        psp.Start()
        self.__pubsub_pair_dict[client_name] = psp
                                    



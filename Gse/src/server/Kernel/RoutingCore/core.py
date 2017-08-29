import zmq
import time
import threading
from logging import DEBUG, INFO

from utils.logging_util import GetLogger

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.interconnect import BindToRandomInprocEndpoint
from server.Kernel.client_process import ClientProcess

from packet_broker import PacketBroker
from routing_table import RoutingTable


# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class RoutingCore(object):
    """
    The routing core is responsible for the Flight and Ground
    PacketBrokers and for creating new ClientProcesses. 
    """

    def __init__(self, context):
        # Setup Logger
        name = "RoutingCore"
        self.__log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, self.__log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
   
        self.__context = context

        self.__FlightPacketBroker = PacketBroker(SERVER_CONFIG.FLIGHT_TYPE, self.__context)
        self.__GroundPacketBroker = PacketBroker(SERVER_CONFIG.GROUND_TYPE, self.__context)

        self.routing_table = RoutingTable(context)

        self.__FlightPacketBroker.Start()
        self.__GroundPacketBroker.Start()

    def Quit(self):
        """
        Quit the routing table.

        The Flight and Ground PacketBrokers are destroyed
        when the ZmqKernel terminates the shared zmq context. 
        """
        self.routing_table.Quit()
        self.__logger.info("Exiting")

    def CreateClientProcess(self, client_name, client_type):
        """
        Use the client_type to determine what connections are required.
        Then create the ClientProcesses.
        Finally, add the client_name to the routing_table.
        """

        # Setup the required addresses
        if client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:
            broker_subscriber_input_address = self.__FlightPacketBroker.GetInputAddress() 
            broker_publisher_output_address = self.__GroundPacketBroker.GetOutputAddress() 

        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:
            broker_subscriber_input_address = self.__GroundPacketBroker.GetInputAddress() 
            broker_publisher_output_address = self.__FlightPacketBroker.GetOutputAddress() 
        else:
            raise TypeError  
        
        # Create the ClientProcess
        self.__logger.debug("Creating ClientProcess")
        self.__logger.debug("Client Type: {}".format(client_type))
        
        client_process = ClientProcess(client_name, client_type,\
                                            broker_subscriber_input_address,\
                                            broker_publisher_output_address)

        
        # Add client_name to the routing_table
        if client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:
            self.routing_table.AddFlightClient(client_name)

        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:
            self.routing_table.AddGroundClient(client_name)
        else:
            self.__logger.info("Type not recognized: {}".format(client_type.lower()))
            raise TypeError


        return client_process
                              



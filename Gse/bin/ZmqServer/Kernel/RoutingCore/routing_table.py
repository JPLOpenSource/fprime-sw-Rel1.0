import zmq
from logging import DEBUG, INFO

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import GetLogger
from ServerUtils.server_config import ServerConfig
from ServerUtils.zhelpers import zpipe
from Kernel.interconnect import BindToRandomInprocEndpoint

SERVER_CONFIG = ServerConfig.getInstance()

class RoutingTable(object):
    """
    Maintains the zmq server's routing table.
    Mediates resource access by multiple threads through a zmq ROUTER socket.
    """
    
    def __init__(self, context): 
        name = "Routing_Table"
        # Setup logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG,\
                                                             fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        # Routing dictionaries
        self.__flight_publishers = {}
        self.__ground_publishers = {}

        # Setup command socket
        self.__command_socket = context.socket(zmq.PUB)
        self.__command_socket_adr = BindToRandomInprocEndpoint(self.__command_socket)

    def Quit(self):
        self.__command_socket.close()

    def GetCommandSocketAddress(self):
        """
        Return command socket inproc address.
        """
        return self.__command_socket_adr


    def GetPublisherTable(self, client_type):
        """
        Return the desired publisher table based on 
        client_type.
        """
        if client_type.lower() == "flight":
            return self.__flight_publishers
        elif client_type.lower() == "ground":
            return self.__ground_publishers

    def AddFlightClient(self, client_name):
        """
        Create a flight publisher entry and create it's publish set.
        """
        self.__flight_publishers[client_name] = set()

    def AddGroundClient(self, client_name):
        """
        Create a ground publisher entry and create it's publish set.
        """
        self.__ground_publishers[client_name] = set()

    def ConfigureFlightPublishers(self, option, ground_client_name, flight_client_list):
        """
        Subscribe a ground client to a list of flight clients by adding the
        ground client's id each flight client's publish set.
        """
        for flight_client_name in flight_client_list:
            try:
                if(option.lower() == "subscribe"):
                    self.__flight_publishers[flight_client_name].add(ground_client_name)
                elif(option.lower() == "unsubscribe"):
                    self.__flight_publishers[flight_client_name].remove(ground_client_name)
                    
                # Send command to all pubsub pairs
                self.__command_socket.send_multipart([ground_client_name, option, flight_client_name])

            except KeyError as e:
                self.__HandleKeyError(e, ground_client_name)

    def ConfigureGroundPublishers(self, option, flight_client_name, ground_client_list):
        """
        Subscribe a flight client to a list of ground clients by adding the
        flight client's id each ground client's publish set.        
        """
        for ground_client_name in ground_client_list:
            try:
                if(option.lower() == "subscribe"):
                    self.__ground_publishers[ground_client_name].add(flight_client_name)
                elif(option.lower() == "unsubscribe"):
                    self.__ground_publishers[ground_client_name].remove(flight_client_name)

                # Send command to all pubsub pairs
                self.__command_socket.send_multipart([flight_client_name, option, ground_client_name])

            except KeyError as e:
                self.__HandleKeyError(e, flight_client_name)

    
    def ConfigureAllFlightPublishers(self, option, receiving_client_name):
        pub_dict = self.__flight_publishers
        self.ConfigureAll(option, receiving_client_name, pub_dict)

    def ConfigureAllGroundPublishers(self, option, receiving_client_name):
        pub_dict = self.__ground_publishers
        self.ConfigureAll(option, receiving_client_name, pub_dict)

    def ConfigureAll(self, option, receiving_client_name, publishing_client_dict):
        """
        Configures all clients in publishing_client_dict to sub/usub to the
        publishing_client.
        """

        # Iterate through all publishing_client entries
        # And add receiving_client to their pubisher sets
        try:
            for publishing_client_name in publishing_client_dict:
                if(option.lower() == "subscribe"): 
                    publishing_client_dict[publishing_client_name].add(receiving_client_name)
                elif(option.lower() == "unsubscribe"): 
                    publishing_client_dict[publishing_client_name].remove(receiving_client_name)

                # Send command to all
                self.__command_socket.send_multipart([receiving_client_name, option, publishing_client_name])
        except KeyError as e:
            self.__HandleKeyError(e, receiving_client_name)


        def __HandleKeyError(e, receiving_client_name)
            key = e.args[0]
            if(key == receiving_client_name):
                pass # Attempted to unsubscribe from a non-subscription
            else:
                self.__logger.warning("{} not found in publishing client dict.".format(key))


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
    
    __instance = None

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

    def ConfigureGroundToFlight(self, option, ground_client_name, flight_client_list):
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

            except KeyError:
                self.__logger.warning("Unable to subscribe ground client {g} to "
                                      "flight client {f}. Flight client {f} "
                                      "is not registered".\
                                      format(g=ground_client_name, f=flight_client_name))
                continue

    def ConfigureFlightToGround(self, option, flight_client_name, ground_client_list):
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

            except KeyError:
                self.__logger.warning("Unable to subscribe flight client {f} to "
                                      "ground client {g}. Ground client {g} "
                                      "is not registered".\
                                      format(g=ground_client_name, f=flight_client_name))
                continue

    def ConfigureAllFlightToGround(self, option, flight_client_name):

        # Iterate througha all ground_client entries
        for ground_client_name in self.__ground_publishers:
            if(option.lower() == "subscribe"): 
                self.__ground_publishers[ground_client_name].add(flight_client_name)
            elif(option.lower() == "unsubscribe"): 
                self.__ground_publishers[ground_client_name].remove(flight_client_name)

            # Send command to all
            self.__command_socket.send_multipart([flight_client_name, option, ground_client_name])
    def ConfigureAllGroundToFlight(self, option, ground_client_name):
        pass



    def getInstance():
        """
        Return instance of singleton.
        """ 
        if(RoutingTable.__instance is None):
            RoutingTable.__instance = RoutingTable()
        return RoutingTable.__instance

    getInstance = staticmethod(getInstance)




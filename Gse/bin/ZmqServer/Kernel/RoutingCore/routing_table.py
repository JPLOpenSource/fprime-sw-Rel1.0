from logging import DEBUG, INFO

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import GetLogger
from ServerUtils.server_config import ServerConfig
from ServerUtils.zhelpers import zpipe

SERVER_CONFIG = ServerConfig.getInstance()

class RoutingTable(object):
    """
    Maintains the zmq server's routing table.
    Mediates resource access by multiple threads through a zmq ROUTER socket.
    """
    
    __instance = None

    def __init__(self): 

        name = "RoutingTable"
        # Setup logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG,\
                                                             fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        # Routing dictionaries
        self.__flight_publishers = {}
        self.__ground_publishers = {}


    def GetPublisherTable(self, client_type):
        """
        Return the desired publisher table based on 
        client_type.
        """
        if client_type.lower() == "flight":
            return self.__flight_publishers
        elif client_type.lower() == "ground":
            return self.__ground_publishers

    def AddFlightClient(self, client_id):
        """
        Create a flight publisher entry and create it's publish set.
        """
        self.__flight_publishers[client_id] = set()

    def AddGroundClient(self, client_id):
        """
        Create a ground publisher entry and create it's publish set.
        """
        self.__ground_publishers[client_id] = set()

    def SubscribeGroundToFlight(self, ground_client_id, flight_client_list):
        """
        Subscribe a ground client to a list of flight clients by adding the
        ground client's id each flight client's publish set.
        """
        for flight_client_id in flight_client_list:
            try:
                self.__flight_publishers[flight_client_id].add(ground_client_id)
            except KeyError:
                self.__logger.warning("Unable to subscribe ground client {g} to"
                                      "flight client {f}. Flight client {f}"
                                      "is not registered".\
                                      format(g=ground_client_id, f=flight_client_id))
                continue

    def SubcribeFlightToGround(self, flight_client_id, ground_client_list):
        """
        Subscribe a flight client to a list of ground clients by adding the
        flight client's id each ground client's publish set.        
        """
        for ground_client_id in ground_client_list:
            try:
                self.__ground_publishers[ground_client_id].add(flight_client_id)
            except KeyError:
                self.__logger.warning("Unable to subscribe flight client {f} to"
                                      "ground client {g}. Ground client {g}"
                                      "is not registered".\
                                      format(g=ground_client_id, f=flight_client_id))
                continue

    def getInstance():
        """
        Return instance of singleton.
        """ 
        if(RoutingTable.__instance is None):
            RoutingTable.__instance = RoutingTable()
        return RoutingTable.__instance

    getInstance = staticmethod(getInstance)




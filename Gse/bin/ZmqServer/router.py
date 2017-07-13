from logging import DEBUG, INFO

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import GetLogger
from server_utils.ServerConfig import ServerConfig


class RoutingTable(object):
    """
    Maintains the zmq server's routing table.
    Mediates resource access by multiple threads through a zmq ROUTER socket.
    """
    def __init__(self):
        self.NAME = "ROUTINGTABLE"

        # Setup logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(self.NAME, log_path, logLevel=DEBUG,\
                                                             fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        # Routing dictionaries
        self.__flight_publishers = {}
        self.__ground_publishers = {}

        # Setup zmq components
        self.__zmq_context = zmq.Context()
        self.__flight_router = self.__zmq_context.socket(zmq.ROUTER)  
        self.__ground_router = self.__zmq_context.socket(zmq.ROUTER)
        self.__flight_router.setsockopt(zmq.LINGER, 0) # Shut down immediately
        self.__ground_router.setsockopt(zmq.LINGER, 0)


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



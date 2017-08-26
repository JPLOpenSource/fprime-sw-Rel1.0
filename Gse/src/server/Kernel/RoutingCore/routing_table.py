import zmq
from logging import DEBUG, INFO

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import GetLogger
from server.ServerUtils.server_config import ServerConfig
from server.ServerUtils.zhelpers import zpipe
from server.Kernel.interconnect import BindToRandomIpcEndpoint

SERVER_CONFIG = ServerConfig.getInstance()

class RoutingTable(object):
    """
    Maintains the zmq server's routing table.
    """
    
    def __init__(self, context): 
        name = "Routing_Table"
        # Setup logger
        log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, log_path, logLevel=DEBUG,\
                                                             fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 

        # Routing dictionaries
        self.__flight_publishers = {}
        self.__ground_publishers = {}

        self.__flights_subscribed_to_all = set() # Set of the flight clients who are subscribed 
                                                 # to all ground clients 
        self.__grounds_subscribed_to_all = set()

        self.__outstanding_subscriptions = [] # List of unsuccessfuly recorded subscriptions 

        # Setup command socket
        self.__command_socket     = context.socket(zmq.PUB)
        self.__command_socket.bind(SERVER_CONFIG.ROUTING_TABLE_CMD_ADDRESS)
        self.__logger.debug("Command socket: {}".format(SERVER_CONFIG.ROUTING_TABLE_CMD_ADDRESS))

        # Set command reply socket
        self.__command_reply_socket = context.socket(zmq.ROUTER)
        self.__command_reply_socket.setsockopt(zmq.RCVTIMEO, 500) # Timeout after 500 ms
        self.__command_reply_socket.bind(SERVER_CONFIG.ROUTING_TABLE_CMD_REPLY_ADDRESS)
        self.__logger.debug("Command reply socket: {}".format(SERVER_CONFIG.ROUTING_TABLE_CMD_REPLY_ADDRESS))

    def Quit(self):
        self.__command_socket.close()
        self.__command_reply_socket.close()

    def GetCommandSocketAddress(self):
        """
        Return command socket inproc address.
        """
        return self.__command_socket_adr

    def GetCommandReplySocketAddress(self):
        """
        Return command reply socket inproc address.
        """
        return self.__command_reply_socket_adr

    def GetAllClientSubscription(self):
        sub_dict = {SERVER_CONFIG.FLIGHT_TYPE:dict(), 
                    SERVER_CONFIG.GROUND_TYPE:dict()}

        self.__logger.debug("GetAllClientSubscription")
        # Initialize sub_dict
        for flight_client in self.__flight_publishers:
            sub_dict[SERVER_CONFIG.FLIGHT_TYPE][flight_client] = set()  
        for ground_client in self.__ground_publishers:
            sub_dict[SERVER_CONFIG.GROUND_TYPE][ground_client] = set()


        # Get Ground Subscriptions
        for flight_client in self.__flight_publishers:
            for ground_client in self.__ground_publishers:
                if ground_client in self.__flight_publishers[flight_client]:
                    sub_dict[SERVER_CONFIG.GROUND_TYPE][ground_client].add(flight_client)

        # Get Flight Subscriptions
        for ground_client in self.__ground_publishers:
            for flight_client in self.__flight_publishers:
                if flight_client in self.__ground_publishers[ground_client]:
                    sub_dict[SERVER_CONFIG.FLIGHT_TYPE][flight_client].add(ground_client)

        return sub_dict



    def GetPublisherTable(self, client_type):
        """
        Return the desired publisher table based on 
        client_type.
        """
        if client_type.lower() == SERVER_CONFIG.FLIGHT_TYPE:
            return self.__flight_publishers
        elif client_type.lower() == SERVER_CONFIG.GROUND_TYPE:
            return self.__ground_publishers

    def AddFlightClient(self, client_name):
        """
        Create a flight publisher entry and create it's publish set.
        """
        self.__flight_publishers[client_name] = set()

        sub_all_set   = self.__grounds_subscribed_to_all
        self.SetNewClientSubscription(client_name, self.__flight_publishers, sub_all_set)
        self.SyncOutstanding(client_name, self.__flight_publishers)

    def AddGroundClient(self, client_name):
        """
        Create a ground publisher entry and create it's publish set.
        """
        self.__ground_publishers[client_name] = set()

        sub_all_set   = self.__flights_subscribed_to_all
        self.SetNewClientSubscription(client_name, self.__ground_publishers, sub_all_set)
        self.SyncOutstanding(client_name, self.__ground_publishers)

    def SetNewClientSubscription(self, publisher_name, publisher_dict, sub_all_set):
        """
        Add to publisher_set any receiving client who is subscribed to all.
        """
        self.__logger.debug("Adding sub-all-clients to {}".format(publisher_name))
        publisher_set = publisher_dict[publisher_name]
        for receiving_client in sub_all_set:
            publisher_set.add(receiving_client)
            self.ConfigureClientPublishers( SERVER_CONFIG.SUB_OPTION, receiving_client, [publisher_name], publisher_dict)
    
    def SyncOutstanding(self, publishing_client_name, publisher_dict):
        """
        Check if publishing_client name is in outstanding_subscriptions.
        If yes, add recv_client to publisher_set.
        """
        self.__logger.debug("Syncing Outstanding")
        publisher_set = publisher_dict[publishing_client_name]
        for recv_client, pub_client in self.__outstanding_subscriptions:
            if pub_client == publishing_client_name:
                publisher_set.add(recv_client)

    def ConfigureFlightPublishers(self, option, ground_client_name, flight_client_list):
        """
        Add ground_client_name to each flight publisher's set.
        """
        self.__logger.info("{} {} to {}".format(option, ground_client_name, flight_client_list))

        pub_dict = self.__flight_publishers
        self.ConfigureClientPublishers(option, ground_client_name, flight_client_list, pub_dict)

    def ConfigureGroundPublishers(self, option, flight_client_name, ground_client_list):
        """
        Add flight_client_name to each ground publisher's set.
        """
        self.__logger.info("{} {} to {}".format(option, flight_client_name, ground_client_list))

        pub_dict = self.__ground_publishers 
        self.ConfigureClientPublishers(option, flight_client_name, ground_client_list, pub_dict)

    def ConfigureClientPublishers(self, option, receiving_client_name, publishing_client_list,\
                                                                       pub_dict):
        """
        Subscribe a receiving client to a list of publishing clients by adding the
        receiving client's name to each publishing client's set.

        Notify the subscribing client of each publisher to subscribe to.
        """
        for publishing_client_name in publishing_client_list:
            # Subscribe or unsubscrobe the receiving_client's PubSubPair to every publishing_client_name
            self.__command_socket.send_multipart([receiving_client_name.encode(), option.encode(),\
                                                  publishing_client_name.encode()])
            
            # Do not update the publisher list if receiving client does not exist.
            try:
                msg = self.__command_reply_socket.recv()
                print("ROUTING TABLE RECV {}".format(msg))
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    self.__logger.warning("{} not registered. Unable to subscribe {} to {}."\
                                          .format(receiving_client_name,receiving_client_name,\
                                                  publishing_client_list))
                    return
                else:
                    raise

            # Command to receiving client was successfuly reached
            # Add to sending clients pub dict
            try:
                if(option.lower() == SERVER_CONFIG.SUB_OPTION):
                    pub_dict[publishing_client_name].add(receiving_client_name)
                elif(option.lower() == "unsubscribe"):
                    pub_dict[publishing_client_name].remove(receiving_client_name)

            except KeyError as e:
                self.__HandleKeyError(e, receiving_client_name)

                # If publishing client does not exist, add to an outstanding list
                if(e.args[0] == publishing_client_name):
                    recv_pub = receiving_client_name, publishing_client_name
                    self.__outstanding_subscriptions.append(recv_pub)

    
    def ConfigureAllFlightPublishers(self, option, ground_client_name):
        """
        Add ground_client's name to all flight publisher's sets. 
        """
        self.__logger.info("{} {} to all Flight-Clients".format(option, ground_client_name))

        pub_dict = self.__flight_publishers
        self.ConfigureAll(option, ground_client_name, pub_dict)

        # Add receiving_client to all subscribe list
        sub_set = self.__grounds_subscribed_to_all
        self.ConfigureSubscribedToAll(option, ground_client_name, sub_set)


    def ConfigureAllGroundPublishers(self, option, flight_client_name):
        """
        Add flight_client's name to all ground publisher's sets.
        """
        self.__logger.info("{} {} to all Ground-Clients".format(option, flight_client_name))

        pub_dict = self.__ground_publishers
        self.ConfigureAll(option, flight_client_name, pub_dict)

        # Add receiving_client to all subscribe list
        sub_set = self.__flights_subscribed_to_all
        self.ConfigureSubscribedToAll(option, flight_client_name, sub_set)

    def ConfigureSubscribedToAll(self, option, receiving_client_name, sub_set):
        """
        Add or remove receiving_client from its type's subscribe to all set. 
        """
        try:
            if(option.lower() == SERVER_CONFIG.SUB_OPTION):
                sub_set.add(receiving_client_name)
            elif(option.lower() == SERVER_CONFIG.USUB_OPTION):
                sub_set.remove(receiving_client_name)
        except KeyError as e:
            self.__HandleKeyError(e, receiving_client_name) 

    def ConfigureAll(self, option, receiving_client_name, publishing_client_dict):
        """
        Configures all clients in publishing_client_dict to sub/usub to the
        publishing_client.
        """

        # Iterate through all publishing_client entries
        # And add receiving_client to their pubisher sets
        self.__logger.debug("Adding {} to {}".format(receiving_client_name, publishing_client_dict))
        
        for publishing_client_name in publishing_client_dict:
            try:
                # Tell receiving_client to subcribe or unsubscribe
                self.__command_socket.send_multipart([receiving_client_name.encode(), option.encode(), publishing_client_name.encode()])

                
                if(option.lower() == SERVER_CONFIG.SUB_OPTION): 
                    publishing_client_dict[publishing_client_name].add(receiving_client_name)
                elif(option.lower() == SERVER_CONFIG.USUB_OPTION): 
                    publishing_client_dict[publishing_client_name].remove(receiving_client_name)

            except KeyError as e:
                self.__HandleKeyError(e, receiving_client_name)



    def __HandleKeyError(self, e, receiving_client_name):
        key = e.args[0]
        if(key == receiving_client_name):
            pass # Attempted to unsubscribe from a non-subscription.

        else:    # Must be unable to find publishing_client_name within publishing dict.
            self.__logger.warning("{} is not a registered publisher.".format(key))


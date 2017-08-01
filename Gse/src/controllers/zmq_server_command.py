class ServerCommandInterface(object):
    def __init__(self):
        self.__socket = None

    def connect(self, socket):
        self.__socket = socket

    def GetSubscriptions(self):
        self.__socket.send_multipart([b"LIST"])

        try:
            msg = self.__socket.recv_multipart() 
            client_sub_dict = pickle.loads(msg[0])
            return client_sub_dict 

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                click.echo("List Subcriptions response timeout")
                return None

    def SubscribeClientTo(self, client_name, client_type, pub_list):
        """
        Specific client subscription method
        """
        self.ConfigureClientSubscription(client_name, client_type, pub_list, "SUB") 
    def UnsubscribeClientFrom(self, client_name, client_type, pub_list):
        """
        Specific client unsubscription method
        """
        self.ConfigureClientSubscription(client_name, client_type, pub_list, "USUB") 

    def ConfigureClientSubscription(self, client_name, client_type, pub_list, option):
        """
        Generalized sub/usub method
        """
        if(type(pub_list) is not type(list()) ):
            pub_list = [pub_list]
        
        for pub_client in pub_list:
            self.__socket.send_multipart([option.encode(), client_name.encode(),\
                                              client_type.encode(), pub_client.encode()])
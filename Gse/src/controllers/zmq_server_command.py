class ServerCommandInterface(object):
    def __init__(self):
        self.__cmd_socket = None

    def connect(self, socket):
        self.__cmd_socket = socket


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
            self.__cmd_socket.send_multipart([option.encode(), client_name.encode(),\
                                              client_type.encode(), pub_client.encode()])
    
    def GetPublisherDict():
        self.__cmd_socket.send_multipart([b"LIST"])

        msg = self.__cmd_socket.recv_multipart() 
        client_pub_dict = pickle.loads(msg[0])

        return client_pub_dict 
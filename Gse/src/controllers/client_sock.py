##########################################
#
# Quick client sockets example.
# reder@jpl.nasa.gov
#
##########################################
#
from Tkinter import *

import Tkinter
import socket
import struct
import time
import select
import zmq

from controllers import client_sock_plugins
from controllers.exceptions import ServerReceiveError, ServerSendError


class ClientSocket(object):
    """
    ClientSocket base class.
    """
    def __init__(self, host_addr, port, gui_name, main_panel=None):
        self.__host_addr  = host_addr
        self.__port       = port
        self.__gui_name   = gui_name
        self.__main_panel = main_panel

        # Define in implementation
        self._publisher_socket  = None
        self._subscriber_socket = None
        self._server_cmd_socket = None # TCP does not need this.

    ###################################
    ## Standard ClientSocket methods ##
    ###################################
    def GetSubscriberSocket(self):
        return self._subscriber_socket

    def GetPublisherSocket(self):
        return self._publisher_socket

    def GetServerCommandSocket(self):
        return self._server_cmd_socket

    def register_main_panel(self, main_panel):
        self.__mainPanel = main_panel

    def UpdateMainPanelStatus(self, string, color="black"):
        try:
            self.main_panel.statusUpdate(string, color)
        except AttributeError: # Api does not register main panel
            pass

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        """
        A specific disconnect routine is required.
        """
        raise NotImplementedError

    @classmethod
    def GetClientSocket(cls, host_addr, port, gui_name, main_panel=None):
        """
        A specific factory class function is required. 
        @returns Instantiated ClientSocket implementation if connection successful, 
                 None is connection unsuccessful.
        """
        raise NotImplementedError

class ZmqClientSocket(ClientSocket):
    """
    Class to perform client side socket connection
    """

    def __init__(self, host_addr, port, gui_name, main_panel=None):
        """
        Initialize zmq components and register to server
        """
        # Initialize Base Class
        super(ZmqClientSocket, self).__init__(host_addr, port, gui_name, main_panel)

        try:
            self.__zmq_initialized = False # Let the destructor know if all zmq components were initialzed

            ####################
            ## Zmq Components ##
            ####################
            self.__zmq_context       = None
            self.__server_cmd_socket = None # Server command socket
            
            self.__server_pub_port   = None # The port the server sends telemetry, events, files
            self.__server_sub_port   = None # The port the server receives commands, files

            self.__gui_sub_socket    = None # The socket the gui receives telemetry, events, files 
            self.__gui_pub_socket    = None # The socket the gui sends commands, files

            self.__zmq_context = zmq.Context()

            #########################################################
            ## Setup server command socket and handle registration ##
            #########################################################
            self.__server_cmd_socket = self.__zmq_context.socket(zmq.DEALER)

            # Set socket options
            self.__server_cmd_socket.setsockopt(zmq.IDENTITY, gui_name.encode())
            self.__server_cmd_socket.setsockopt(zmq.RCVTIMEO, 2000) # 2 sec timeout
            self.__server_cmd_socket.setsockopt(zmq.LINGER, 0)      # Immidiately close socket
            
            self.__server_cmd_socket.connect("tcp://{}:{}".format(str(host_addr), str(port)))

            # Register the GUI with the server
            # TODO: Create unique ground-client name
            self.__server_cmd_socket.send_multipart([b"REG", b"GROUND", b"ZMQ"])

            response = self.__server_cmd_socket.recv_multipart()
            self.__server_pub_port = struct.unpack("<I", response[1])[0]
            self.__server_sub_port = struct.unpack("<I", response[2])[0]

            time.sleep(1)

            ###########################
            ## Setup pub/sub sockets ##
            ###########################
            self.__gui_pub_socket = self.__zmq_context.socket(zmq.DEALER)
            self.__gui_sub_socket = self.__zmq_context.socket(zmq.ROUTER)

            # Set socket options
            self.__gui_pub_socket.setsockopt(zmq.IDENTITY, gui_name.encode())
            self.__gui_pub_socket.setsockopt(zmq.LINGER, 0) # Immidiately close socket
            self.__gui_sub_socket.setsockopt(zmq.LINGER, 0)
            self.__gui_sub_socket.setsockopt(zmq.IDENTITY, gui_name.encode())

            self.__gui_pub_socket.connect("tcp://{}:{}".format(host_addr, self.__server_sub_port))
            self.__gui_sub_socket.connect("tcp://{}:{}".format(host_addr, self.__server_pub_port))


            ############
            ## Finish ##
            ############
            print("Publishing to port: {} | Subscribed to port: {}".\
            format(self.__server_sub_port, self.__server_pub_port))

            s = "Connected to server (host addr %s)" % (host_addr)
            self.UpdateMainPanelStatus(s)

            self.__zmq_initialized = True

            # Setup Listen, Publish, and Command sockets
            self._publisher_socket   = client_sock_plugins.ZmqPublisherSocket(self.__gui_pub_socket)
            self._subscriber_socket  = client_sock_plugins.ZmqSubscriberSocket(self.__gui_sub_socket)
            self._commander_socket   = client_sock_plugins.ZmqCommanderSocket(self.__server_cmd_socket)

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                # EAGAIN occurs if a zmq recv call times out.
                # In this case we only await the registration response,
                # So close command socket and terminate context.
                print("Server Connection Timeout.")
                self.__server_cmd_socket.close()
                self.__zmq_context.term()
            raise


    def disconnect(self):
        """
        Tell server to close, close all sockets, and terminate the zmq context.
        """
        if(self.__zmq_initialized):
            self.__server_cmd_socket.close()
            self.__gui_sub_socket.close()
            self.__gui_pub_socket.close()
            self.__zmq_context.term()



    def SubscribeToTargets(self, targets):
        if targets is not None:
            for target in targets:
                 # Subscribe to all targets
                self.__server_cmd_socket.send_multipart([b"SUB", self.__gui_name.encode(), b"GROUND", target.encode()])


    

    @classmethod
    def GetClientSocket(cls, host_addr, port, gui_name, main_panel=None):
        """
        Factory function to create ClientSocket.
        Returns None if connection cannot be made. 
        """
        try:
            print("HOST: {}".format(host_addr))
            print("PORT: {}".format(port))
            print("NAME: {}".format(gui_name))

            clientSocket = ZmqClientSocket(host_addr, port, gui_name)
            clientSocket.register_main_panel(main_panel)
            return clientSocket

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                string = "Unable to connect to {}:{}".format(host_addr, port)
                print(string)

                try: # To update main_panel. If API is used main_panel == None
                    main_panel.statusUpdate(string, "red")
                except AttributeError:
                    pass


                return None
            else:
                raise

    
# Main loop
#
def main():
    port = 60002

    s = ClientSocket("192.168.1.100", port)
    i = 0
    while 1:
        try:
            x_est = s.receive()
            print x_est
        except RuntimeError:
            print "Socket connection terminated"
            break


if __name__ == "__main__":
    main()

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

class ClientSocket:
    """
    Class to perform client side socket connection
    """

    def __init__(self, main_panel, host_addr, port, gui_name):
        """
        Initialize zmq components and register to server
        """
        try:
            self.__gui_name = gui_name
            self.__zmq_initialized = False # Let the destructor know if all zmq components were initialzed
            self.__mainPanel = main_panel

            ####################
            ## Zmq Components ##
            ####################
            self.__zmq_context       = None
            self.__server_cmd_socket = None # Server command socket
            
            self.__server_pub_port   = None # The port the server sends telemetry, events, files
            self.__server_sub_port   = None # The port the server receives commands, files

            self.__gui_sub_socket   = None # The socket the gui receives telemetry, events, files 
            self.__gui_pub_socket   = None # The socket the gui sends commands, files

            self.__zmq_context = zmq.Context()

            #########################################################
            ## Setup server command socket and handle registration ##
            #########################################################
            self.__server_cmd_socket = self.__zmq_context.socket(zmq.DEALER)

            # Set socket options
            self.__server_cmd_socket.setsockopt(zmq.IDENTITY, gui_name.encode())
            self.__server_cmd_socket.setsockopt(zmq.RCVTIMEO, 2000) # 2 sec timeout
            self.__server_cmd_socket.setsockopt(zmq.LINGER, 0)      # Immidiately close socket
            
            self.__server_cmd_socket.connect("tcp://{}:{}".format(host_addr, port))

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
            self.__mainPanel.statusUpdate(s, 'red')

            self.__zmq_initialized = True

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                # EAGAIN occurs if a zmq recv call times out.
                # In this case we only await the registration response,
                # So close command socket and terminate context.
                self.__server_cmd_socket.close()
                self.__zmq_context.term()
            raise


    def __del__(self):
        self.disconnect()

    def SubscribeToTargets(self, targets):
        if targets is not None:
            for target in targets:
                 # Subscribe to all targets
                self.__server_cmd_socket.send_multipart([b"SUB", self.__gui_name.encode(), b"GROUND", target.encode()])



    def disconnect(self):
        """
        Tell server to close, close all sockets, and terminate the zmq context.
        """
        if(self.__zmq_initialized):
            self.__server_cmd_socket.close()
            self.__gui_sub_socket.close()
            self.__gui_pub_socket.close()
            self.__zmq_context.term()


    def receiveFromServer(self):
        """
        Return a list of messages. A single message will be returned
        in a single indexed list.
        """
        try:
            msg = self.__gui_sub_socket.recv_multipart()
            return msg

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                return None
            else:
                raise
   

    def sendToServer(self, msg):
        """
        Sends msg to the server's subscribe port.
        """
        try:
            
            if(type(msg) is list):
                self.__gui_pub_socket.send_multipart(msg)
            else:
                self.__gui_pub_socket.send_multipart([msg])

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                return
            else:
                raise


def GetClientSocket(main_panel, host_addr, port, gui_name):
    """
    Factory function to create ClientSocket
    """
    try:

        clientSocket = ClientSocket(main_panel, host_addr, port, gui_name)
        return clientSocket

    except zmq.ZMQError as e:
        if e.errno == zmq.EAGAIN:
            string = "Unable to connect to {}:{}".format(host_addr, port)
            main_panel.statusUpdate(string, "red")
            print(string)
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

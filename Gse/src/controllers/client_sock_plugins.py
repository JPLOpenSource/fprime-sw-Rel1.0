#!/bin/env python
#===============================================================================
# NAME: client_sock_plugins.py
#
# DESCRIPTION: This module contains a SubscriberSocket and PublisherSocket base 
#              class. Also includeed are a TCP and ZMQ implmementation.
#              The implementations are used by the client_sock.ClientSocket
#              class. Using two implementations allows for backwards compatability
#              between the TCP and ZMQ servers.     
#       
#              The implementation classes are not responsible for creating or
#              destroying their sockets. They only operate on the provided socket
#              and provide an quit routine that gracefully exits the socket operation.
#
#              The client_sock.ClientSocket is responsible for creation and destruction
#              of the TCP or ZMQ sockets.
#
# AUTHOR: David Kooi
# DATE CREATED: August 1, 2017
#
# Copyright 2017, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================



import zmq
import select
import struct

from controllers.exceptions import ServerReceiveError, ServerSendError


####################
## Abstract       ##
## Classes        ##
####################

class __SubscriberSocket(object):
    """
    Generic Subscriber socket.
    """

    def __init__(self, socket):
        self._socket = socket
    
    def receiveFromServer(self):
        """
        Override for specific implementation
        @returns Complete FPrime packet byte string: [size][desc][data]
        """
        raise NotImplementedError

    def quit(self):
        """
        Override to provide a socket exit.
        """
        raise NotImplementedError
   
class __PublisherSocket(object):
    """
    Generic Publisher socket. 
    """

    def __init__(self, socket):
        self._socket = socket

    def publishToServer(self, msg):
        """
        Override for specific implementation.
        @params msg: Complete FPrime packet byte string: [size][desc][data]
        """
        raise NotImplementedError

    def quit(self):
        """
        Override to provide a socket exit.
        """
        raise NotImplementedError


########################
## TCP Implementation ##
########################

class TcpSubscriberSocket(__SubscriberSocket):

    def __init__(self, socket):
        super(TcpSubscriberSocket, self).__init__(socket)

        self.__exit_flag = False


    def receiveFromServer(self):
        """
        @returns One FPrime packet
        """
        pkt_len  = self.__recv(4)
        pkt_desc = self.__recv(4)

        desc = int(struct.unpack(">I",pkt_desc)[0])
        size = int(struct.unpack(">I",pkt_len)[0])

        data = self.__recv(size - u32_type.U32Type().getSize())

        return pkt_len + pkt_desc + data


     def __recv(self, l):
        """
        Read l bytes from socket.
        """
        chunk =""
        msg = ""
        n = 0
        while l > n:
            if self.__exit_flag:
                raise Exception("Exiting receive loop")

            # Check if the socket is ready to read
            fd = select.select([self.sock], [], [], .25)
            if fd[0]:
                chunk = self.sock.recv(l-n)
                if chunk == '':
                    return ''
                    #raise RuntimeError("socket connection broken")
                msg = msg + chunk
                n = len(msg)
        return msg

    def quit(self):

        self.__exit_flag = True


class TcpPublisherSocket(__PublisherSocket):

    def publishToServer(self, packet):
        """
        Sends one FPrime packet to the server
        """
        try:
            self._socket.sendall(packet)
        except IOError:
            print "EXCEPTION: Could not send message (%s) to socket" % msg

    def quit(self):
        pass


########################
## ZMQ Implementation ##
########################

class ZmqSubscriberSocket(__SubscriberSocket):

    def receiveFromServer(self):
        """
        @returns One FPrime packet
        """
        try:
            msg = self._socket.recv_multipart()
            return msg[1] # [0]: ZMQServer ID
                          # [1]: FPrime Packet

        except zmq.ZMQError as e:
            raise ServerReceiveError("ZMQ Receive Error: {}.".format(e.errno))


class ZmqPublisherSocket(__PublisherSocket):

    def publishToServer(self, packet):
        """
        Sends msg to the server's subscribe port.
        """
        try:
            
            if(type(msg) is list):
                self._socket.send_multipart(msg)
            else:
                self._socket.send_multipart([msg])

        except zmq.ZMQError as e:
            raise ServerSendError("Unable to send message.")


class ZmqCommanderSocket(object):

    def __init__(self, socket):
        self._socket = socket

    def sendCommand(self, msg):
        try:
            self._socket.send_multipart(msg)
        except zmq.ZMQError as e:
            raise ServerSendError("Unable to send message.")

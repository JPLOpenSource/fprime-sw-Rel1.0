import zmq

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


####################
## Implementation ##
## Classes        ##
####################



class TcpSubscriberSocket(__SubscriberSocket):

    def receiveFromServer(self):
        """
        @returns One FPrime packet
        """
        pkt_len = self._socket.recv(4)

        pkt_desc = self._socket.recv(4)

        desc = int(struct.unpack(">I",pkt_desc)[0])
        size = int(struct.unpack(">I",pkt_len)[0])

        data = self._socket.recv(size - u32_type.U32Type().getSize())

        return pkt_len + pkt_desc + data

class TcpPublisherSocket(__PublisherSocket):

    def publishToServer(self, packet):
        """
        Sends one FPrime packet to the server
        """
        self._socket.send(packet)


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
            raise ServerReceiveError("Unable to send message.")


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

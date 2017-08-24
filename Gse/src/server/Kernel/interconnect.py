import os
import zmq
import random
import binascii

###################################################################
## Wrapper classes for Publisher and Subscriber Thread Endpoints ##
###################################################################

def GetRandomPort():
    port = random.randint(50000,60000)
    return port

def BindToRandomTcpEndpoint(socket):
    port = socket.bind_to_random_port("tcp://*")
    return port

def BindToRandomInprocEndpoint(socket):
    address = "inproc://%s" % binascii.hexlify(os.urandom(8))
    socket.bind(address)
    return address

class SubscriberThreadEndpoints(object):
    def __init__(self):
        self.__input_port = None 
        self.__output_address = None  
    def SetEndpoints(self, input_port, output_address):
        self.__input_port = input_port
        self.__output_address = output_address
    def GetInputPort(self):
        return self.__input_port
    def GetOutputAddress(self):
        return self.__output_address
    def GetOutputBinder(self):
        return BindToRandomInprocEndpoint
    def GetInputBinder(self):
        return BindToRandomTcpEndpoint
    def GetEndpointSetter(self):
        return self.SetEndpoints

class PublisherThreadEndpoints(object):
    def __init__(self):
        self.__input_address = None 
        self.__output_port = None
    def SetEndpoints(self, input_address, output_port):
        self.__input_address = input_address
        self.__output_port = output_port
    def GetInputAddress(self):
        return self.__input_address
    def GetOutputPort(self):
        return self.__output_port
    def GetOutputBinder(self):
        return BindToRandomTcpEndpoint
    def GetInputBinder(self):
        return BindToRandomInprocEndpoint
    def GetEndpointSetter(self):
        return self.SetEndpoints


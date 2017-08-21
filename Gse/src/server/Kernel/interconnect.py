import os
import zmq
import binascii

###################################################################
## Wrapper classes for Publisher and Subscriber Thread Endpoints ##
###################################################################

def BindToRandomTcpEndpoint(socket):
    port = socket.bind_to_random_port("tcp://*")
    return port
def BindToRandomInprocEndpoint(socket):
    address = "inproc://%s" % binascii.hexlify(os.urandom(8))
    socket.bind(address)
    return address
def BindToRandomIpcEndpoint(socket):
    address = "ipc:///tmp/pipe_%s" % binascii.hexlify(os.urandom(8))
    try:
        socket.bind(address)
    except zmq.ZMQError as e:
        print e
        raise e
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
        return BindToRandomIpcEndpoint
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
        return BindToRandomIpcEndpoint
    def GetEndpointSetter(self):
        return self.SetEndpoints


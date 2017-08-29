import os
import zmq
import types
import random
import binascii

# Global server config class
from server.ServerUtils.server_config import ServerConfig
SERVER_CONFIG = ServerConfig.getInstance()


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
    address = "ipc:///tmp/pipe.%s" % binascii.hexlify(os.urandom(8))
    try:
        socket.bind(address)
    except zmq.ZMQError as e:
        print e
        raise e
    return address

def GetRandomPort():
    return random.randrange(50000,60000)

def SendOutputToClient(logger, msg, output_socket):
    #logger.debug("Received: {}".format(msg))
    #logger.debug("Sending: {}".format(msg[1]))
    output_socket.send(msg[1]) # Only send packet

def SendOutputToBroker(logger, msg, output_socket):
    #logger.debug("Sending: {}".format(msg))
    output_socket.send_multipart(msg) # Send source header and packet 


def CheckRoutingCommandEnabled(logger, client_name, sub_socket, cmd_socket, cmd_reply_socket):
    print("Check command")
    cmd_list = cmd_socket.recv_multipart()

    recipient   = cmd_list[0]
    option      = cmd_list[1]
    pub_client  = cmd_list[2] # The publishing client whom to
                              # subscribe or unsubscribe to.

    if(cmd_list[0] == client_name):
        logger.debug("Command received: {}".format(cmd_list))
        if(option == 'subscribe'):
            sub_socket.setsockopt(zmq.SUBSCRIBE, pub_client)
        elif(option == 'unsubscribe'):
            sub_socket.setsockopt(zmq.UNSUBSCRIBE, pub_client) 

        # Ack routing table
        cmd_reply_socket.send(b"{}_pubsub Received".format(client_name))
def CheckRoutingCommandDisabled(logger, client_name, sub_socket, cmd_socket, cmd_reply_socket):
    pass

# Needed to provide copies of CheckRoutingCommand functions
def copy_func(f, name=None):
    return types.FunctionType(f.func_code, f.func_globals, name or f.func_name,
        f.func_defaults, f.func_closure)

class SubscriberThreadEndpoints(object):
    def __init__(self, output_address, input_port):
        self.__input_port = input_port
        self.__output_address = output_address 

    # Getters and Setters
    def SetEndpoints(self, input_port, output_address):
        self.__input_port = input_port
        self.__output_address = output_address
    def GetInputPort(self):
        return self.__input_port
    def GetOutputAddress(self):
        return self.__output_address

    # Endpoint binding methods
    def BindOutputEndpoint(self, output_socket):
        output_socket.connect(self.__output_address)
        return self.__output_address
    def BindInputEndpoint(self, input_socket):
        input_socket.bind("tcp://*:{}".format(self.__input_port))
        return self.__input_port

    # Socket creation methods
    def GetInputSocket(self, context):
        return context.socket(zmq.ROUTER)
    def GetOutputSocket(self, context):
        return context.socket(zmq.PUB)

    # Set output_socket specifics
    def GetOutputSocketFunc(self):
        return copy_func(SendOutputToBroker)

    # Setup routing table commands
    def GetCmdSocket(self, context):
        return context.socket(zmq.SUB)
    def GetCmdReplySocket(self, context):
        return None
    def GetCheckRoutingCommandFunc(self):
        return copy_func(CheckRoutingCommandDisabled)

class PublisherThreadEndpoints(object):
    def __init__(self, input_address, output_port):
        self.__input_address = input_address
        self.__output_port = output_port

    # Getters and Setters
    def SetEndpoints(self, input_address, output_port):
        self.__input_address = input_address
        self.__output_port = output_port
    def GetInputAddress(self):
        return self.__input_address
    def GetOutputPort(self):
        return self.__output_port

    # Endpoint binding methods
    def BindOutputEndpoint(self, output_socket):
        output_socket.bind("tcp://*:{}".format(self.__output_port))
        return self.__output_port
    def BindInputEndpoint(self, input_socket):
        input_socket.connect(self.__input_address)
        return self.__input_address

    # Socket creation methods
    def GetInputSocket(self, context):
        return context.socket(zmq.SUB)
    def GetOutputSocket(self, context):
        return context.socket(zmq.DEALER)

    # Set output_socket specifics
    def GetOutputSocketFunc(self):
        return copy_func(SendOutputToClient)

    # Setup routing table commands
    def GetCmdSocket(self, context):
        cmd_socket = context.socket(zmq.SUB)
        cmd_socket.setsockopt(zmq.SUBSCRIBE, '')
        cmd_socket.connect(SERVER_CONFIG.ROUTING_TABLE_CMD_ADDRESS)
        return cmd_socket
    def GetCmdReplySocket(self, context):
        cmd_reply_socket = context.socket(zmq.DEALER)
        cmd_reply_socket.connect(SERVER_CONFIG.ROUTING_TABLE_CMD_REPLY_ADDRESS)
        return cmd_reply_socket
    def GetCheckRoutingCommandFunc(self):
        return copy_func(CheckRoutingCommandEnabled)


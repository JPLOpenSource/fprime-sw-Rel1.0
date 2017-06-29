import os
import sys
import zmq
import logging
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import GetLogger


class ZmqKernel(object):
    def __init__(self, command_port, context):
        # Setup Logger
        cwd = os.getcwd() 
        log_path = os.path.join(cwd, "logs")
        self.__logger = GetLogger("zmq_kernel",log_path)
        self.__logger.debug("Logger Active")

        # Setup pub/sub runnable 
        xpub_port = command_port + 1
        xsub_port = command_port + 2
        self.__pubsub_thread = _PubSubThread(context, xpub_port, xsub_port)
        
        # Setup command socket
        self.__command_socket = context.socket(zmq.ROUTER)
        self.__command_socket.bind("tcp://*:{}".format(command_port))

        # Create Reactor 
        self.__loop = IOLoop.instance()
        
        # Wrap sockets in ZMQStreams for IOLoop handlers
        self.__command_socket = ZMQStream(self.__command_socket)

        # Register handlers
        self.__command_socket.on_recv(self.HandleCommand)

    def Start(self):
        """
        Start main event loop of the zmq kernel
        """
        try:
            self.__loop.start()
        except KeyboardInterrupt:
            pass

    def HandleCommand(self, msg):
        """
        Receives a new command message and dispatches the message to the
        proper command handler.
        """
        self.__logger.debug("Command Received: {}".format(msg))
        
        return_id = msg[0]
        cmd       = msg[2] # Zmq inserts a delimiting frame at msg index 1

        if cmd == 'REG':
            HandleRegistration(msg)


    def HandleRegistration(self, msg):
        """
        Receives a registration message.
        """
            name     = msg[3]
            obj_type = msg[4]
            
class _PubSubThread(object):
    """
    Private class to handle the publish/subscribe operation
    """
    def __init__(self, context, pub_port, sub_port):
        # Setup Logger
        cwd = os.getcwd() 
        log_path = os.path.join(cwd, "logs")
        self.__logger = GetLogger("zmq_kernel_pubsub",log_path)
        self.__logger.debug("Logger Active")

        # Setup XPub/XSub sockets
        self.__xpub_socket = context.socket(zmq.XPUB)
        self.__xpub_socket.bind("tcp://*:{}".format(xpub_port))

        self.__xsub_socket = context.socket(zmq.XSUB)
        self.__xsub_socket.bind("tcp://*:{}".format(xsub_port))

        # Create Reactor 
        self.__loop = IOLoop.instance()
        
        # Wrap sockets in ZMQStreams for IOLoop handlers
        self.__xpub_socket = ZMQStream(self.__xpub_socket)
        self.__xsub_socket = ZMQStream(self.__xsub_socket)

        # Register handlers
        self.__xpub_socket.on_recv(self.HandlePublishPort)
        self.__xsub_socket.on_recv(self.HandleSubscribePort)


   def Start(self):
    """
    Start main event loop of the zmq kernel
    """
    try:
        self.__loop.start()
    except KeyboardInterrupt:
        pass


    def HandlePublishPort(self, msg):
        pass

    def HandleSubscribePort(self, msg):
        pass



   
        
def CommandSender(context, cmd_port):
    
    req_socket = context.socket(zmq.REQ)
    req_socket.connect("tcp://localhost:{}".format(cmd_port))

    req_socket.send_multipart([b"REG", b"FP1"])

if __name__ == "__main__":
    cmd_port = 5555
   
    

    context = zmq.Context()
    
    CommandSender(context, cmd_port)

    kernel = ZmqKernel(5555, context)
    kernel.Start()


import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback


class ZmqKernel(object):
    def __init__(self, command_port, context):
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

        try:
            self.__loop.start()
        except KeyboardInterrupt:
            pass

    def HandleCommand(self):
       pass 

        


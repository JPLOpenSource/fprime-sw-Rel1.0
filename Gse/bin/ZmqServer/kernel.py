import os
import sys
import zmq
import logging
import threading

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback 
from zmq.eventloop.zmqstream import ZMQStream

from utils.logging_util import GetLogger
from kernel_threads import GeneralSubscriptionThread,\
                           FlightSubRunnable, GroundSubRunnable


#TODO: Create server config file
class ZmqKernel(object):

    def __init__(self, command_port, context):
        # Setup Logger
        cwd = os.getcwd() 
        log_path = os.path.join(cwd, "logs")
        self.__logger = GetLogger("zmq_kernel",log_path)
        self.__logger.debug("Logger Active")

        # Setup routing table
        self.__routing_table = {}

        # Flight and ground client pub/sub port sets
        self.__flight_client_sub_port = None
        self.__flight_client_pub_port = None

        self.__ground_client_sub_port = None
        self.__ground_client_pub_port = None

        # Setup flight and ground subcription threads
        self.__SERVER_RUNNING = threading.Event() # Thread event flag to
        self.__SERVER_RUNNING.set()               # indicate shutdown

        name = "FlightSubscriptionThread"
        self.__flight_sub_thread = GeneralSubscriptionThread(name,\
                    FlightSubRunnable, context, self.__SetFlightSubThreadPorts,\
                    self.__SERVER_RUNNING)
 
        name = "GroundSubcriptionThread"
        self.__ground_sub_thread = GeneralSubscriptionThread(name,\
                    GroundSubRunnable, context, self.__SetGroundSubThreadPorts,\
                    self.__SERVER_RUNNING)
   
        # Setup command/status socket
        self.__command_socket = context.socket(zmq.ROUTER)
        try:
            self.__command_socket.bind("tcp://*:{}".format(command_port))
        except ZMQError as e:
            if e.errno == zmq.EADDRINUSE:
                logger.error("Unable to bind command socket to port {}"\
                             .format(command_port))
                raise e

        # Create Reactor 
        self.__loop = IOLoop.instance()
        
        # Wrap sockets in ZMQStreams for IOLoop handlers
        self.__command_socket = ZMQStream(self.__command_socket)

        # Register handlers
        self.__command_socket.on_recv(self.__HandleCommand)

    def Start(self):
        """
        Start main event loop of the zmq kernel
        """
        try:
            self.__logger.debug("Kernel reactor started.")
            
            self.__flight_sub_thread.start()
            self.__ground_sub_thread.start()
            self.__loop.start()
        except KeyboardInterrupt:
            self.Quit()  
          
    def Quit(self):
        """
        Shut down server
        """
        self.__logger.info("Initiating server shutdown")
        self.__SERVER_RUNNING.clear() 

    def __SetGroundSubThreadPorts(self, sub_port, pub_port):
        """
        Sets the pub/sub ports for the ground subscription thread.
        I.e:
            Subscribe to ground clients and
            Publish   to flight clients
        """
        self.__ground_client_sub_port = sub_port
        self.__flight_client_pub_port = pub_port

    def __SetFlightSubThreadPorts(self, sub_port, pub_port):
        """
        Sets the pub/sub ports for the flight subscription thread.
        I.e:
            Subscribe to flight clients and
            Publish   to ground clients
        """
        self.__flight_client_sub_port = sub_port
        self.__ground_client_pub_port = pub_port

    def __HandleCommand(self, msg):
        """
        Receives a new command message and dispatches the message to the
        proper command handler.
        """
        self.__logger.debug("Command Received: {}".format(msg))
        
        return_id = msg[0]
        cmd       = msg[2] # Zmq inserts a delimiting frame at msg index 1

        if cmd == 'REG':
            status, pub_port, sub_port = self.__HandleRegistration(msg)
            self.__RegistrationResponse(return_id, status, pub_port, sub_port)


    def __HandleRegistration(self, msg):
        """
        Receives a client registration message.
        Returns a tuple containing the registration status, pub, and sub ports 
        """
        name        = msg[3]
        client_type = msg[4]
        proto       = msg[5]
        self.__logger.debug("Registering {name} as {client_type} client "
                            "using {proto} protocol."\
                       .format(name=name, client_type=client_type, proto=proto))
     
        #TODO: Generate meaningful registration status
        status = 1
        self.__AddToRoutingTable(name, client_type)

        client_pub_port          = self.__GetClientPubPort(client_type) 
        client_sub_port          = self.__GetClientSubPort(client_type) 
        return (status, client_pub_port, client_sub_port)


    def __RegistrationResponse(self, return_id, status, xp_port, xs_port):
        """
        Send response to the registering client
        """
        # ZMQ requires the return id followed by an empty byte
        msg = [
               bytes(return_id),\
               b'',\
               bytes(status),\
               bytes(xp_port),\
               bytes(xs_port)
              ]

        self.__command_socket.send_multipart(msg)

    def __GetClientPubPort(self, client_type):
        """
        Return the publish based on client_type 
        """
        if   client_type.lower() == "flight":
            return self.__flight_client_pub_port
        elif client_type.lower() == "ground":
            return self.__ground_client_pub_port
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            self.__logger.error("Exiting.")
            self.Quit()

    def __GetClientSubPort(self, client_type):
        """
        Return the subscription port based on client_type 
        """
        if   client_type.lower() == "flight":
            return self.__flight_client_sub_port
        elif client_type.lower() == "ground":
            return self.__ground_client_sub_port
        else:
            self.__logger.error("Client type: {} not recognized.".format(client_type))
            self.__logger.error("Exiting.")
            self.Quit()


    def __AddToRoutingTable(self, name, client_type):
        """
        Based on it's type, the client is added to the routing table. 
        """
        pass
        





def MockTarget(context, cmd_port): 
    
    target_name = "FP1" 

    # Setup Logger 
    cwd = os.getcwd() 
    log_path = os.path.join(cwd, "logs") 
    logger = GetLogger("mock_target",log_path) 
    logger.debug("Logger Active") 
    
    command_socket = context.socket(zmq.REQ) 
    command_socket.connect("tcp://localhost:{}".format(cmd_port))
    

    # Register target
    command_socket.send_multipart([b"REG", target_name.encode(), b"flight", b"ZMQ"])
    msg = command_socket.recv_multipart()
    logger.debug("Command Sended Received:")
    logger.debug(msg) 

    # Setup pub/sub ports
    pub_port = msg[1]
    sub_port = msg[2]

    pub_socket = context.socket(zmq.PUB)
    sub_socket = context.socket(zmq.SUB)

    pub_socket.connect("tcp://localhost:{}".format(pub_port))
    sub_socket.connect("tcp://localhost:{}".format(sub_port))

    logger.debug("Publishing to port: {}".format(pub_port))
    logger.debug("Subscribed to port: {}".format(sub_port))



if __name__ == "__main__":
    cmd_port = 5555
       
    context = zmq.Context()
    
    mock_target = threading.Thread(target=MockTarget,args=(context, cmd_port))
    mock_target.start()

    kernel = ZmqKernel(5555, context)
    kernel.Start()

    

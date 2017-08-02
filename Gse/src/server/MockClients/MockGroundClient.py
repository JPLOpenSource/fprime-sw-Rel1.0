import sys
import zmq
import threading
import logging

from server.ServerUtils.server_config import ServerConfig
from utils.logging_util import GetLogger

# Modules required for test
from controllers.channel_loader import ChannelLoader
from models.serialize import *
import struct

SERVER_CONFIG = ServerConfig.getInstance()




def MockGroundClient(context, cmd_port, client_name):


    # Setup Logger   
    log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
    logger = GetLogger("{}".format(client_name),log_path, logLevel = logging.INFO) 
    logger.debug("Logger Active") 

    command_socket = context.socket(zmq.DEALER)
    command_socket.setsockopt(zmq.IDENTITY, client_name)
    command_socket.connect("tcp://localhost:{}".format(cmd_port))

    # Register target
    command_socket.send_multipart([b"REG", b"ground", b"ZMQ"])
    msg = command_socket.recv_multipart()
    logger.debug("Command Reply Received:{}".format(msg))

    # Subscribe
    command_socket.send_multipart([b"SUB", client_name.encode(), b"ground", b''])


    # Setup pub/sub ports
    server_pub_port = struct.unpack("<I", msg[1])[0]
    server_sub_port = struct.unpack("<I", msg[2])[0]

    pub_socket = context.socket(zmq.DEALER)
    sub_socket = context.socket(zmq.ROUTER)

    # Set publisher identity
    pub_socket.setsockopt(zmq.IDENTITY, client_name.encode())
    sub_socket.setsockopt(zmq.IDENTITY, client_name.encode())


    pub_socket.connect("tcp://localhost:{}".format(server_sub_port))
    sub_socket.connect("tcp://localhost:{}".format(server_pub_port))

    logger.debug("Publishing to port: {}".format(server_sub_port))
    logger.debug("Subscribed to port: {}".format(server_pub_port))

    while True:
        try:
            msg = sub_socket.recv_multipart()
            logger.debug("{}".format(msg[1]))
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break
            else:
                raise
   

    logger.debug("Closing")
    command_socket.close()
    pub_socket.close()
    sub_socket.close()
    

if __name__ == "__main__":
    cmd_port = sys.argv[1]
    client_name   = sys.argv[2]



    context = zmq.Context()

    mock_client = threading.Thread(target=MockGroundClient,\
                                     args=(context, cmd_port, client_name))
    mock_client.start()


    try:
        while True:
            pass
    except KeyboardInterrupt:
        context.term()
        

    print("Closing MockGroundClient")
    
    

    

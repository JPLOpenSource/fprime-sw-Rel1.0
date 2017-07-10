import sys
import time
import zmq
import threading
import datetime


sys.path.append("/Users/dkooi/Workspace/fprime-sw/Gse/generated/Ref") 

from server_utils.ServerConfig import ServerConfig
from utils.logging_util import GetLogger

# Modules required for test
from controllers.channel_loader import ChannelLoader
from models.serialize import *
from server_utils import test_utils
import struct

SERVER_CONFIG = ServerConfig.getInstance()

def MockFlightClient(context, cmd_port, client_name): 
   
    # Setup Logger   
    log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
    logger = GetLogger("mock_target",log_path) 
    logger.debug("Logger Active") 

    logger.debug("Context: {}".format(context))
    command_socket = context.socket(zmq.REQ) 
    logger.debug("Created cmd socket")
    command_socket.connect("tcp://localhost:{}".format(cmd_port))
    logger.debug("Connected cmd socket")
    
    # Register target
    command_socket.send_multipart([b"REG", client_name.encode(), b"flight",\
                                                                 b"ZMQ"])
    msg = command_socket.recv_multipart()
    logger.debug("Command Reply Received:{}".format(msg))

    # Setup pub/sub ports
    server_pub_port = msg[1]
    server_sub_port = msg[2]

    pub_socket = context.socket(zmq.DEALER)
    sub_socket = context.socket(zmq.ROUTER)

    # Set publisher identity
    pub_socket.setsockopt(zmq.IDENTITY, client_name.encode())

    pub_socket.connect("tcp://localhost:{}".format(server_sub_port))
    sub_socket.connect("tcp://localhost:{}".format(server_pub_port))

    logger.debug("Publishing to port: {}".format(server_sub_port))
    logger.debug("Subscribed to port: {}".format(server_pub_port))


    # Get Sensor1 dictionary
    channel_loader = ChannelLoader()
    channel_loader.create("/Users/dkooi/Workspace/fprime-sw/Gse/generated/Ref/"
                          "channels")
    ch_dict  = channel_loader.getChDict() 
    sensor1  = ch_dict[103]
    
    

    # Get channel tlm values
    name = sensor1.getName()
    compName = sensor1.getCompName()
    ch_id = sensor1.getId()
    ch_desc = sensor1.getChDesc()
    ch_type = sensor1.getType()
    timeBase = sensor1.getTimeBase()
    timeContext = sensor1.getTimeContext()
    formatString = sensor1.getFormatString()

    value    = sensor1.getType()
    
    # Create static fprime types
    data_len  = u32_type.U32Type(0)
    pk_desc   = u32_type.U32Type(1)
    ch_id     = u32_type.U32Type(ch_id)
    time_base = u16_type.U16Type(0)
    time_cxt  = u8_type.U8Type(0)    

    sine_wave = test_utils.GetSineWave() 

    while True: 
        try:
            for val in sine_wave: 
                # Set variable values
                ch_time = datetime.datetime.now()
                sensor1.setTime(0, 0, ch_time.second, ch_time.microsecond)          
                
                # Time Values
                time_s  = sensor1.getTimeSec()
                time_us = sensor1.getTimeUsec()  
        
                # Time as fprime type
                time_s  = u32_type.U32Type(time_s)
                time_us = u32_type.U32Type(time_us) 

                value.val  = float(val)
                
                
               
                # Create channel packet          
                packet = data_len.serialize() + pk_desc.serialize() +\
                         ch_id.serialize() + time_base.serialize() +\
                         time_cxt.serialize() + time_s.serialize() +\
                         time_us.serialize() + value.serialize()

                pub_socket.send_multipart([packet])
               
                time.sleep(0.1)           

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                logger.debug("ETERM received") 
                break
            else:
                raise


    # Quit
    logger.debug("Closing")
    command_socket.close()
    pub_socket.close()
    sub_socket.close()

   


if __name__ == "__main__":
    cmd_port = sys.argv[1] 
    client_name = "F1"
    
    context = zmq.Context()

    mock_flight_client = threading.Thread(target=MockFlightClient,\
                                          args=(context, cmd_port, client_name))
    mock_flight_client.start() 
    
    try:
        while True:
            pass   
    except KeyboardInterrupt: 
        print("Closing MockFlightClient")
        context.term() 




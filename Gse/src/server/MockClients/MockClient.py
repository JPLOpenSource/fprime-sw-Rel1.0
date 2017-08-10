import sys
import time
import zmq
import threading
import datetime

from logging import INFO

sys.path.append("/Users/dkooi/Workspace/fprime-sw/Gse/generated/Ref") 

from server.ServerUtils.server_config import ServerConfig
from utils.logging_util import GetLogger
from utils.throughput_analyzer import ThroughputAnalyzer


# Modules required for test
from controllers.channel_loader import ChannelLoader
from models.serialize import *
from server.ServerUtils import test_utils
import struct

SERVER_CONFIG = ServerConfig.getInstance()

def MockClient(context, cmd_port, client_name, client_type, throughput): 
    latency = 1 / float(throughput)
    print("LATENCY: {}".format(latency))

    # Setup Logger   
    log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath")  
    logger = GetLogger("{}".format(client_name),log_path, chLevel=INFO) 
    logger.debug("Logger Active") 
 
    command_socket = context.socket(zmq.DEALER) 
    command_socket.setsockopt(zmq.IDENTITY, client_name)

    logger.debug("Created cmd socket")
    command_socket.connect("tcp://localhost:{}".format(cmd_port))
    logger.debug("Connected cmd socket")
    
    # Register target
    command_socket.send_multipart([b"REG", client_type.encode(), b"ZMQ"])
    msg = command_socket.recv_multipart()
    logger.debug("Command Reply Received:{}".format(msg))

    # Subscribe to all commands
    command_socket.send_multipart([b"SUB", client_name.encode(), client_type.encode(), b''])

    # Setup pub/sub ports
    server_pub_port = struct.unpack("<I", msg[1])[0]
    server_sub_port = struct.unpack("<I", msg[2])[0]

    pub_socket = context.socket(zmq.DEALER)
    sub_socket = context.socket(zmq.ROUTER)
    sub_socket.setsockopt(zmq.RCVTIMEO, 0) # Do not wait to receive
    sub_socket.setsockopt(zmq.LINGER, 0)   # Do not wait to close
    pub_socket.setsockopt(zmq.LINGER, 0)   # Do not wait to close


    # Set publisher identity
    pub_socket.setsockopt(zmq.IDENTITY, client_name.encode())
    sub_socket.setsockopt(zmq.IDENTITY, client_name.encode())
    sub_socket.setsockopt(zmq.RCVHWM, 100)

    pub_socket.connect("tcp://localhost:{}".format(server_sub_port))
    sub_socket.connect("tcp://localhost:{}".format(server_pub_port))

    logger.debug("Publishing to port: {}".format(server_sub_port))
    logger.debug("Subscribed to port: {}".format(server_pub_port))


    # Setup Poller
    poller = zmq.Poller()
    poller.register(pub_socket, zmq.POLLOUT)
    poller.register(sub_socket, zmq.POLLIN)


    sine_wave = test_utils.GetSineWave() 
    ramp = test_utils.GetRamp()
    
    time.sleep(1)
    try:

        analyzer = ThroughputAnalyzer(client_name + "_analyzer")
        analyzer.StartAverage()
        start_time = time.time()
        while True: 
     

                for val in ramp: 

                    socks = dict(poller.poll())

                    if pub_socket in socks:

                        if(throughput != 0):
                            if( (time.time() - start_time) >= latency ):
                                analyzer.StartInstance()

                                start_time = time.time()
                                data = client_name.encode() +" " + bytes(val)
                                logger.debug("Sending: {}".format(bytes(val)))
                                pub_socket.send(data)

                                analyzer.SaveInstance()
                                analyzer.Increment(1)



                    if sub_socket in socks:
                        msg = sub_socket.recv_multipart()
                        logger.debug("{}".format(msg[1]))

                     


    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            logger.debug("ETERM received") 
            pass
        else:
            raise



    # Quit
    analyzer.SetAverageThroughput()
    analyzer.PrintReports()

    logger.debug("Closing")
    command_socket.close()
    pub_socket.close()
    sub_socket.close()

   


def SetupMockTelemetry():
    number = 1
    if number == 1:
        ch_idx = 103
    else:
        ch_idx = 104


    # Get Sensor1 dictionary
    channel_loader = ChannelLoader()
    channel_loader.create("/Users/dkooi/Workspace/fprime-sw/Gse/generated/Ref/"
                          "channels")
    ch_dict  = channel_loader.getChDict() 
    sensor1  = ch_dict[ch_idx]
    
    

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


    # Set variable values
    ch_time = datetime.datetime.now()
    sensor1.setTime(0, 0, ch_time.second, ch_time.microsecond)          
    
    # Time Values
    time_s  = sensor1.getTimeSec()
    time_us = sensor1.getTimeUsec()  

    # Time as fprime type
    time_s  = u32_type.U32Type(time_s)
    time_us = u32_type.U32Type(time_us) 

    value.val  = float(ch_idx)
    
    
   
    # Create channel packet          
    packet = data_len.serialize() + pk_desc.serialize() +\
             ch_id.serialize() + time_base.serialize() +\
             time_cxt.serialize() + time_s.serialize() +\
             time_us.serialize() + value.serialize()

    pub_socket.send(packet)




if __name__ == "__main__":
    cmd_port    = sys.argv[1] 
    client_name = sys.argv[2]
    client_type = sys.argv[3]
    throughput  = int(sys.argv[4])

    
    context = zmq.Context()

    mock_flight_client = threading.Thread(target=MockClient,\
                                           args=(context, cmd_port, client_name, client_type, throughput))
    mock_flight_client.start() 
    
    try:
        while True:
            pass   
    except KeyboardInterrupt: 
        print("Closing MockFlightClient")
        context.term() 




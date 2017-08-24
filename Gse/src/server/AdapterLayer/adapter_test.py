import zmq
import time

from server.AdapterLayer.plugins.space_packet_adapter import SpacePacketAdapter 
from server.AdapterLayer.adapter_process import AdapterProcess

s = SpacePacketAdapter('spacepacket', 'gui_1', 5000, 5001, 5002, 5003)
process = AdapterProcess(s)
process.start()



c = zmq.Context()
s = c.socket(zmq.DEALER)
s.setsockopt(zmq.IDENTITY, "gui_1")
s.connect("tcp://localhost:5003")

while(True):
    print("Sending")
    s.send(b"hello")
    time.sleep(1)



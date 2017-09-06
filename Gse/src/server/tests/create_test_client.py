# Register a test client to the server

import zmq

c = zmq.Context()
s = c.socket(zmq.DEALER)
s.setsockopt(zmq.IDENTITY,b"test_1")
s.connect("tcp://localhost:5555")
s.send_multipart([b"REG",b"FLIGHT",b"spacepacket"])


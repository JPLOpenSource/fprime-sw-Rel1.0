# Test that the AdapterProcess works.

import zmq
import time
import signal
import threading

from adapter_process import AdapterProcess

class TestAdapter():
    """
    TestAdapter maintains two threads.
    The two threads communicate between each other.
    """
    def __init__(self):

        self.context = zmq.Context()
        self.thread_1 = threading.Thread(target=self.__thread_1_runnable, args=(self.context,))
        self.thread_2 = threading.Thread(target=self.__thread_2_runnable, args=(self.context,))

    def __thread_1_runnable(self, context):
        input_socket = context.socket(zmq.ROUTER)
        input_socket.bind("tcp://*:5555")

        try:
            while(True):
                msg = input_socket.recv_multipart()
                print("Received: {}".format(msg))
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                input_socket.close()

    def __thread_2_runnable(self, context):
        output_socket = context.socket(zmq.DEALER)
        output_socket.connect("tcp://localhost:5555")

        try:
            while(True):
                output_socket.send(b"Hello")
                time.sleep(1)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                output_socket.close()

    def Start(self):
        """
        Start threads.
        """
        self.thread_1.start()
        time.sleep(0.01) # Let thread startup
        self.thread_2.start()
    
    def Quit(self):
        """
        Quit the test adapter.
        """
        self.context.term()


if __name__ == "__main__":
    """
    Wrap the TestAdapter in an AdapterProcess. 
    """
    ta = TestAdapter()
    adapter_process = AdapterProcess(ta)
    adapter_process.start()
    
    try: 
        signal.pause()
    except KeyboardInterrupt:
        pass

    adapter_process.terminate()






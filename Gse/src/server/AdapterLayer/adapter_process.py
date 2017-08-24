import signal
from multiprocessing import Process


class AdapterProcess(Process):
    def __init__(self, Adapter):
        Process.__init__(self)
        self.__adapter = Adapter

    def run(self):
        self.__adapter.Start() 
        try:
            signal.pause() # Sleep until interrupted
        except KeyboardInterrupt:
            pass

        self.__adapter.Quit()


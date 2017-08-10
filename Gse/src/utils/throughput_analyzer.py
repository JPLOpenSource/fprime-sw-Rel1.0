import time


class ThroughputAnalyzer(object):
    def __init__(self):
        self.__start_time = 0
        self.__delta      = 0
        self.__count      = 0

    def Start(self):
        self.__start_time = time.time()
    def Increment(self, count):
        self.__count += count
    def Stop(self):
        self.__delta = time.time() - self.__start_time

    def Get(self):
        return self.__count / self.__delta

import zmq
import threading
from logging import DEBUG, INFO

from utils.logging_util import GetLogger
from utils.throughput_analyzer import ThroughputAnalyzer

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.interconnect import BindToRandomInprocEndpoint

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class PacketBroker(object):
    def __init__(self, client_type, context):
        # Setup Logger
        name = "{}_PacketBroker".format(client_type)
        self.__log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
        self.__logger = GetLogger(name, self.__log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
   
        self.__xsub = context.socket(zmq.XSUB) 
        self.__xsub_address = BindToRandomInprocEndpoint(self.__xsub)

        self.__xpub = context.socket(zmq.XPUB)
        self.__xpub_address = BindToRandomInprocEndpoint(self.__xpub)

        self.__ProxyThread = threading.Thread(target=self.__HandleProxy)

        self.__logger.debug("Creating PacketBroker")
        self.__logger.debug("Type: {}".format(client_type))
        self.__logger.debug("XSUB Address: {}".format(self.__xsub_address))
        self.__logger.debug("XPUB Address: {}".format(self.__xpub_address))


    def Start(self):
        self.__ProxyThread.start()


    def __HandleProxy(self):
        self.__logger.debug("Entering Runnable")

        poller = zmq.Poller()
        poller.register(self.__xpub, zmq.POLLIN)
        poller.register(self.__xsub, zmq.POLLIN)
        try:
            analyzer = ThroughputAnalyzer()
            analyzer.Start()
            while(True):
                socks = dict(poller.poll(0))
                if self.__xsub in socks: # XSUB receives packets
                    msg = self.__xsub.recv_multipart()
                    self.__logger.debug("XSUB Received: {}".format(msg))
                    self.__xpub.send_multipart(msg) 
                    analyzer.Increment(1)

                if self.__xpub in socks: # XPUB receives subscription messages and passes them through
                    msg = self.__xpub.recv_multipart()
                    self.__logger.debug("XPUB Received: {}".format(msg))
                    self.__xsub.send_multipart(msg)

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__xsub.close()
                self.__xpub.close()
                self.__logger.debug("Exiting Runnable")
                analyzer.Stop()
                self.__logger.debug("Message Throughput: {} msg/s".format(analyzer.Get()))


    def GetInputAddress(self):
        """
        Return xsub address.
        """
        return self.__xsub_address
    def GetOutputAddress(self):
        """
        Return xpub address.
        """
        return self.__xpub_address

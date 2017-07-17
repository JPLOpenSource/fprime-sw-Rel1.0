import zmq
import threading
from logging import DEBUG, INFO

from utils.logging_util import GetLogger

from ServerUtils.server_config import ServerConfig
from Kernel.interconnect import BindToRandomInprocEndpoint

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class PacketBroker(object):
    def __init__(self, client_type, context):
        # Setup Logger
        name = "{}_PacketBroker".format(client_type)
        self.__log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath") 
        self.__logger = GetLogger(name, self.__log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.__logger.debug("Logger Active") 
   
        self.__xsub = context.socket(zmq.XSUB)
        self.__xsub_address = BindToRandomInprocEndpoint(self.__xsub)

        self.__xpub = context.socket(zmq.XPUB)
        self.__xpub_address = BindToRandomInprocEndpoint(self.__xpub)

        self.__ProxyThread = threading.Thread(target=self.__HandleProxy)


    def Start(self):
        self.__ProxyThread.start()


    def __HandleProxy(self):
        self.__logger.debug("Entering Runnable")
        try:
            while(True):

                msg = self.__xsub.recv_multipart()
                self.__logger.debug("Received: {}".format(msg))
                self.__xpub.send_multipart(msg) 

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                self.__xsub.close()
                self.__xpub.close()
                self.__logger.info("Exiting Runnable")


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

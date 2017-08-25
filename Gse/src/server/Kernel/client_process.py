import zmq
import signal
from logging import DEBUG, INFO, ERROR 
from multiprocessing import Process

from threads import GeneralServerIOThread 
from utils.logging_util import SetGlobalLoggingLevel, GetLogger
from server.ServerUtils.server_config import ServerConfig

from interconnect import SubscriberThreadEndpoints, PublisherThreadEndpoints


# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class ClientProcess(Process):
	def __init__(self, client_name, client_type, broker_subscriber_input_address,\
                                                 broker_publisher_output_address):
		Process.__init__(self)
		signal.signal(signal.SIGINT, self.Quit)
		# Setup logger
		log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
		self.__logger = GetLogger("{}_ClientProcess".format(client_name), log_path, logLevel=DEBUG,\
							                                             fileLevel=DEBUG)
		self.__logger.debug("Logger Active") 

		self.__context = zmq.Context().instance()
		self.__logger.debug("ZMQ Context: {}".format(self.__context.underlying))


		# Create client subscription thread
		self.__sub_thread_endpoints = SubscriberThreadEndpoints(broker_subscriber_input_address)
		pubsub_type   = SERVER_CONFIG.SUB_TYPE
		self.__subscriber_thread = GeneralServerIOThread(client_name, pubsub_type,\
		             				self.__sub_thread_endpoints) 

		# Create client publish thread
		self.__pub_thread_endpoints = PublisherThreadEndpoints(broker_publisher_output_address)
		pubsub_type   = SERVER_CONFIG.PUB_TYPE
		self.__publisher_thread = GeneralServerIOThread(client_name, pubsub_type,\
		             				self.__pub_thread_endpoints) 

		self.daemon = True
	def run(self):
		self.__logger.info("Starting threads")
		self.__subscriber_thread.start()
		self.__publisher_thread.start()

		
		signal.pause() # Wait until interrupt	


	def Quit(self, signum, frame):
		self.__logger.info("Stopping Threads")
		self.__context.term()

	# End point access methods
	def GetSubscriberThreadInputPort(self):
		return self.__sub_thread_endpoints.GetInputPort()
	def GetSubscribterThreadOutputAddress(self):
		return self.__sub_thread_endpoints.GetOutputAddress()
	def GetPublisherThreadInputAddress(self):
		return self.__pub_thread_endpoints.GetInputAddress()
	def GetPublisherThreadOutputPort(self):
		return self.__pub_thread_endpoints.GetOutputPort()

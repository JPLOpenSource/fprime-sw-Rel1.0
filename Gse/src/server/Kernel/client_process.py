import os
import zmq
import time
import signal
from logging import DEBUG, INFO, ERROR 
from multiprocessing import Process

from utils.logging_util import SetGlobalLoggingLevel, GetLogger

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.threads import GeneralServerIOThread 

from server.Kernel import interconnect
from server.Kernel.interconnect import SubscriberThreadEndpoints, PublisherThreadEndpoints


# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

class ClientProcess(Process):
	def __init__(self, client_name, client_type, broker_subscriber_input_address,\
                                                 broker_publisher_output_address):
		"""
		Constructor of ClientProcess. 
		Note: The constructor still operates under the parent process. 
		"""
		Process.__init__(self)
		


		# Save ports, addresses, names, etc for the new process to access.
		self.__client_name = client_name
		self.__client_type = client_type
		self.__broker_subscriber_input_address = broker_subscriber_input_address
		self.__broker_publisher_output_address = broker_publisher_output_address

		# Generate random ports and callback so the kernel can access them.
		self.__input_port = interconnect.GetRandomPort()
		self.__output_port = interconnect.GetRandomPort()

		self.daemon = True # Force kill the process if parent exits.
						   # ClientProcess should exit gracefuly through
						   # the kill_socket, but if it does not
						   # ClientProcess will not remain after the kernel
						   # exits. 

	def run(self):
		"""
		This is the start of the new process.
		"""
		signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupts. 
													 # It is the kernel's responsibility to handle them.
		# Setup logger
		log_path = SERVER_CONFIG.get("filepaths", "server_log_internal_filepath") 
		logger = GetLogger("{}_ClientProcess".format(self.__client_name), log_path, logLevel=DEBUG,\
							                                             fileLevel=DEBUG)
		logger.debug("Logger Active") 

		# Create a process level instance of the context
		context = zmq.Context().instance()
		logger.debug("ZMQ Context: {}".format(context.underlying))
		logger.debug("PID: {}".format(os.getpid()))


		# Create client subscription thread
		sub_thread_endpoints = SubscriberThreadEndpoints(self.__broker_subscriber_input_address, self.__input_port)
		pubsub_type   = SERVER_CONFIG.SUB_TYPE
		subscriber_thread = GeneralServerIOThread(self.__client_name, pubsub_type,\
		             				sub_thread_endpoints) 

		# Create client publish thread
		pub_thread_endpoints = PublisherThreadEndpoints(self.__broker_publisher_output_address, self.__output_port)
		pubsub_type   = SERVER_CONFIG.PUB_TYPE
		publisher_thread = GeneralServerIOThread(self.__client_name, pubsub_type,\
		             				pub_thread_endpoints) 

		logger.info("Starting threads")
		subscriber_thread.start()
		publisher_thread.start()

		# Kill socket
		kill_socket = context.socket(zmq.SUB)
		kill_socket.connect(SERVER_CONFIG.KILL_SOCKET_ADDRESS)
		kill_socket.setsockopt(zmq.SUBSCRIBE, '')

		kill_socket.recv() # Block until kill signal is received		

		# Exit by terminating the context
		# and waiting for threads to close
		logger.debug("Terminating context")
		context.term()
		logger.info("Threads exited")
		

	# End point access methods
	def GetSubscriberThreadInputPort(self):
		return self.__input_port
	def GetSubscribterThreadOutputAddress(self):
		return self.__sub_thread_endpoints.GetOutputAddress()
	def GetPublisherThreadInputAddress(self):
		return self.__pub_thread_endpoints.GetInputAddress()
	def GetPublisherThreadOutputPort(self):
		return self.__output_port

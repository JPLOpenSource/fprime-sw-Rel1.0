import zmq
import time
import signal
from server.Kernel.client_process import ClientProcess
from server.Kernel.interconnect import SubscriberThreadEndpoints, PublisherThreadEndpoints
from server.Kernel.threads import GeneralServerIOThread
from server.Kernel.RoutingCore.packet_broker import PacketBroker


context = zmq.Context().instance()
packet_broker = PacketBroker("flight", context)
in_addr = packet_broker.GetInputAddress()
out_addr = packet_broker.GetOutputAddress()

client_process = ClientProcess("test", "flight", in_addr, out_addr)
time.sleep(2)
client_process.start()

# Create client subscription thread
#client_name = "test"
#pubsub_type = "sub"
#sub_thread_endpoints = SubscriberThreadEndpoints()
#subscriber_thread = GeneralServerIOThread(client_name, pubsub_type,\
#             				sub_thread_endpoints) 
#
#pubsub_type = "pub"
#pub_thread_endpoints = PublisherThreadEndpoints()
#publisher_thread = GeneralServerIOThread(client_name, pubsub_type,\
#             				pub_thread_endpoints) 
#
#subscriber_thread.start()
#publisher_thread.start()
#
#time.sleep(2)

context.term()

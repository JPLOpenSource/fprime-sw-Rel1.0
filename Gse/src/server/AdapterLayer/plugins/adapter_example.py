import struct

from server.AdapterLayer.adapter_base import AdapterBase
from server.ServerUtils.bit_utils import BitArray

def GetObject():
    """
    Required module function.
    @returns class object of the implemented adapter.
    """
    return ExampleAdapter
def GetAdapterName():
    """
    Required module function.
    @returns The name of the adapter. This is the name by which a client registration protocol is matched.
    """
    return "example_protocol"

class ExampleAdapter(AdapterBase):
    """
    Adapter implementation of a example adapter.
    """
    def __init__(self, *args, **kwargs):
        AdapterBase.__init__(self, *args, **kwargs)

    def Decode(self, encoded_packet):
    	"""
    	Receives an example packet from the client. 
        The packet is decoded into FPrime native
        and sent to the server.
    	"""

        # Strip a simple header
        packet = encoded_packet[2:] # Remove 2 bytes
        return packet

    def Encode(self, packet):
    	"""
    	Receives a FPrime native packet from the server.
        The packet is encoded with a example header
        and sent to the receiving client.
    	"""

        # Add a simple header
        header = struct.pack(">I", 0xFF) # Add 2 bytes
    	return header + packet


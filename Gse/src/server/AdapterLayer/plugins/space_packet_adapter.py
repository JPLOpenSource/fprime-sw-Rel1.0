from server.AdapterLayer.adapter_base import AdapterBase
from server.ServerUtils.bit_utils import BitArray

def GetObject():
    return SpacePacketAdapter
def GetAdapterName():
    return "spacepacket"

class SpacePacketAdapter(AdapterBase):
    def __init__(self, *args, **kwargs):
        AdapterBase.__init__(self, *args, **kwargs)

    def Decode(self, encoded_packet):
    	"""
    	From client decode.
    	"""
    	packet = encoded_packet[6:] # Remove spacepacket header
        return packet

    def Encode(self, packet):
    	"""
    	To client encode.
    	"""

    	# Process first 4 octets
    	primary_header = BitArray()  # SpacePacket primary header is 6 octets
    	primary_header.extend(0, 3)  # 3 bits PACKET VERSION NUMBER
    	primary_header.extend(1, 1)  # 1 bit PACKET TYPE ( 0 for telemetry, 1 for telecommand)
    	primary_header.extend(0, 1)  # 1 bit SRC HDR FLAG
    	primary_header.extend(0, 11) # 11 bits for APPLICATION PROCESS IDENTIFIER
    	primary_header.extend(0, 2)  # 2 bits for SEQUENCE FLAGS
    	primary_header.extend(0, 14) # 14 bits for PACKET SEQUENCE COUNT

    	first_4_octets = int(format(primary_header), 2)
    	first_4_octets = struct.pack(">i", first_4_octets) # Pack into 4 byte int
    	
    	# Process last 2 octets
    	primary_header = BitArray()
    	packet_length = len(packet) - 1
    	primary_header.extend(packet_length, 16) # 16 bits for PACKET DATA LENGTH

    	last_2_octets = int(format(primary_header), 2) # Get primary header in integer form
    	last_2_octets = struct.pack(">h", last_2_octets) # Pack into 2 byte short


    	spacepacket_header = first_4_octets + last_2_octets
        return spacepacket_header + packet


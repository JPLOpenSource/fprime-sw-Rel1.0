from server.AdapterLayer.adapter_base import AdapterBase

def GetObject():
    return SpacePacketAdapter
def GetAdapterName():
    return "spacepacket"

class SpacePacketAdapter(AdapterBase):
    def __init__(self, *args, **kwargs):
        AdapterBase.__init__(self, *args, **kwargs)

    def Decode(self, encoded_packet):
        return encoded_packet

    def Encode(self, packet):
        return packet


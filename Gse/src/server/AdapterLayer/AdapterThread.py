

class AdapterThread(object):
    def __init__(self, client_name):
        self.__name = client_name

    def GetAdapterToServerPublishPort(self):
        return self.__atsp_port
    def GetAdapterFromServerSubscribePort(self):
        return self.__afss_port
    def GetAdaterToClientPublishPort(self):
        return self.__atcp_port
    def GetAdapterFromClientSubscribePort

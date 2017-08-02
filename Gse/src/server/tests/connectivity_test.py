import os
import sys
import zmq
import time
import struct
import signal
import random

import threading
from subprocess import Popen

from logging import DEBUG, ERROR

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.kernel import ZmqKernel
from server.MockClients.MockFlightClient import MockFlightClient
from server.MockClients.MockGroundClient import MockGroundClient

from utils.logging_util import GetLogger

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class TestObject(object):
    def __init__(self):
        self._object_process = None

    def _StartMainProcess(self, args):
        self._object_process = Popen(args=args, shell=True)
        

    def Start(*args, **kwargs):
        raise NotImplementedError

    def Quit(self):
        raise NotImplementedError

    def ForceQuit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGKILL)



class RefApp(TestObject):

    def Start(self, server_cmd_port, address, name):
            self.name = name

            cmd  = os.environ['BUILD_ROOT'] + "/Ref/darwin-darwin-x86-debug-llvm-bin/Ref"
            cmd += " -p {port} -a {addr} -n {nm}".format(port=server_cmd_port, addr=address, nm=name)

            self._StartMainProcess(cmd)
    
    def Quit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGINT)
        print("RefApp {} closed.".format(self.name))
        self._object_process.terminate()




class ZmqServer(TestObject):

    def Start(self, server_cmd_port):
        cmd = "python " + os.environ['BUILD_ROOT'] + "/Gse/bin/run_server.py {}".format(server_cmd_port)

        self._StartMainProcess(cmd)

    def Quit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGINT)
        self._object_process.terminate()
        print("ZmqServerClosed")
        



class MockClient(TestObject):
    def __init__(self):
        super(MockClient, self).__init__()

    def Start(self, cmd_port, client_name, m_type):
        self.name = client_name

        if m_type == "flight":
            args = "python " + os.environ['BUILD_ROOT'] + "/Gse/src/server/MockClients/MockFlightClient.py {} {}"\
                    .format(cmd_port, client_name)
        else:
            args = "python " + os.environ['BUILD_ROOT'] + "/Gse/src/server/MockClients/MockGroundClient.py {} {}"\
                    .format(cmd_port, client_name)
            

        
        self._StartMainProcess(args)
    
    def Quit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGINT)
        self._object_process.terminate()
        print("MockClient {} closed.".format(self.name))


def StartGseGui(server_cmd_port, address, name, subscription_list):
    cmd  = "python "
    cmd += os.path.join(os.environ["BUILD_ROOT"], "Gse/bin/gse.py ")

    dict_path = os.path.join(os.environ['BUILD_ROOT'], "Gse/generated/Ref")
    cmd += "-d {dict_path} ".format(dict_path=dict_path)
    cmd += "-p {port} -a {addr} -N {nm} ".format(port=server_cmd_port, addr=address, nm=name)

    for target_name in subscription_list:
        cmd += "-T {nm} ".format(nm=target_name)

    print("Starting gse.py")
    print("Running command")
    print(cmd)
    os.system(cmd)


class TestConnectivity:

    @classmethod
    def setup_class(cls):
        ## Must have build root set
        if os.environ['BUILD_ROOT'] is None:
            print("Must have BUILD_ROOT set.")
            print("Exiting.")
            sys.exit()

        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath")
        cls.logger = GetLogger("CONNECTIVITY_UTEST", log_path, logLevel=DEBUG, fileLevel=ERROR)
        cls.logger.debug("Logger Active")


        # Start Server
        cmd_port   = 5551
        address    = 'localhost'
        timeout_s  = 10

        name = "flight_ref"
        cls.flight_1 = RefApp()
        cls.flight_1.Start(cmd_port, address, name)

        cls.server = ZmqServer()
        cls.server.Start(cmd_port)


        cls.mock_flight_list = []
        for i in range(5):
            name   = "flight_{}".format(i)
            cls.mock_flight_list.append( MockClient() )
            cls.mock_flight_list[i].Start(cmd_port, name, "flight")

        cls.mock_ground_list = []
        for i in range(5):
            name = "ground_{}".format(i)
            cls.mock_ground_list.append( MockClient() )
            cls.mock_ground_list[i].Start(cmd_port, name, "ground")

        time.sleep(10)

    @classmethod
    def teardown_class(cls):
        cls.flight_1.Quit()
        cls.server.Quit()

        for i in range(len(cls.mock_flight_list)):
            cls.mock_flight_list[i].Quit()
        for i in range(len(cls.mock_ground_list)):
            cls.mock_ground_list[i].Quit()

        

    def test_random_ground_disconnect(self):
        pass
        

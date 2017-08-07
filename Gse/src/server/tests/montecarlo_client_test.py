import os
import sys
import zmq
import time
import struct
import signal
import random

from threading import Timer, Event
from subprocess import Popen

from logging import DEBUG, ERROR

from nose import with_setup

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.kernel import ZmqKernel
from server.MockClients.MockFlightClient import MockFlightClient
from server.MockClients.MockGroundClient import MockGroundClient

from utils.logging_util import GetLogger

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class TestObject(object):
    """
    Base class provides a standard interface for
    starting, stopping, and force stopping a client process.
    """
    def __init__(self):
        self._object_process = None
        self._args = None
        
    def Setup(self, *args, **kwargs):
        """
        Override to set self._args.

        self._args is a command line command called by Popen.
        """
        raise NotImplementedError

    def Start(self):
        """
        Start a subprocess.
        """
        self._object_process = Popen(args=self._args, shell=True)

    def Quit(self):
        """
        Handle the subprocess' graceful exit.
        """
        raise NotImplementedError

    def ForceQuit(self):
        """
        SIGKILL the process.
        """
        pid = self._object_process.pid
        os.kill(pid, signal.SIGKILL)



class RefApp(TestObject):

    def Setup(self, server_cmd_port, address, name):
            self.name = name

            cmd  = os.environ['BUILD_ROOT'] + "/Ref/darwin-darwin-x86-debug-llvm-bin/Ref"
            cmd += " -p {port} -a {addr} -n {nm}".format(port=server_cmd_port, addr=address, nm=name)

            self._args = cmd

    def Quit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGINT)
        print("RefApp {} closed.".format(self.name))
        self._object_process.terminate()




class ZmqServer(TestObject):

    def Setup(self, server_cmd_port):
        cmd = "python " + os.environ['BUILD_ROOT'] + "/Gse/bin/run_server.py {}".format(server_cmd_port)

        self._args = cmd

    def Quit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGINT)
        self._object_process.terminate()
        print("ZmqServerClosed")
        



class MockClient(TestObject):
    def __init__(self):
        super(MockClient, self).__init__()

    def Setup(self, cmd_port, client_name, m_type):
        self.name = client_name

        if m_type == "flight":
            args = "python " + os.environ['BUILD_ROOT'] + "/Gse/src/server/MockClients/MockFlightClient.py {} {}"\
                    .format(cmd_port, client_name)
        else:
            args = "python " + os.environ['BUILD_ROOT'] + "/Gse/src/server/MockClients/MockGroundClient.py {} {}"\
                    .format(cmd_port, client_name)
            
        self._args = args
        
    
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
        cls.logger = GetLogger("CONNECTIVITY_UTEST", log_path, logLevel=DEBUG, fileLevel=DEBUG)
        cls.logger.debug("Logger Active")


        # Start Server
        cmd_port   = 5551
        address    = 'localhost'
        timeout_s  = 10

        # Setup Ref App
        name = "flight_ref"
        cls.ref_app = RefApp()
        cls.ref_app.Setup(cmd_port, address, name)

        # Setup and start server
        cls.server = ZmqServer()
        cls.server.Setup(cmd_port)
        cls.server.Start()

        # Setup mock clients
        cls.mock_flight_list = []
        for i in range(3):
            name   = "flight_{}".format(i)
            cls.mock_flight_list.append( MockClient() )
            cls.mock_flight_list[i].Setup(cmd_port, name, "flight")

        cls.mock_ground_list = []
        for i in range(5):
            name = "ground_{}".format(i)
            cls.mock_ground_list.append( MockClient() )
            cls.mock_ground_list[i].Setup(cmd_port, name, "ground")


    @classmethod
    def teardown_class(cls):
        #cls.flight_1.Quit()
        cls.server.Quit()

        cls.destory_clients()

    @classmethod
    def initialize_clients(cls):
        cls.logger.info("Initializing Clients")

        for client in cls.mock_flight_list:
            client.Start()
        for client in cls.mock_ground_list:
            client.Start()

    @classmethod
    def destory_clients(cls):
        cls.logger.info("Destroying Clients")

        for client in cls.mock_flight_list:
            client.Quit()
        for client in cls.mock_ground_list:
            client.Quit()

    def test_server_integrity(self):
        monte_carlo_time_s = 1800 # Time to perform random disconnects
        passthrough_time_s = 600  # Time to test unobsructed data path

        self.initialize_clients()
        time.sleep(4)
        self.monte_carlo_disconnect(monte_carlo_time_s)
        self.passthrough(passthrough_time_s)
        assert self.check_logs()

        self.destory_clients()
        
    def passthrough(self, passthrough_time_s):
        self.logger.info("-------- Pass Through Started --------")
        time.sleep(passthrough_time_s)    

    def monte_carlo_disconnect(self, monte_carlo_time_s):
        action_limit_s = 10

        run_test = Event()
        run_test.set()

        def ToggleTest(run_test):
            run_test.clear()

        def Disconnect(self, kill_list, dead_set):
            for client in kill_list:
                self.logger.info("Disconnecting: {}".format(client.name))
                dead_set.add(client)
                client.ForceQuit()
        def Connect(self, dead_list, living_set):
            for client in dead_list:
                self.logger.info("Connecting: {}".format(client.name))
                living_set.add(client)
                client.Start()
            

        t = Timer(monte_carlo_time_s, ToggleTest, args=(run_test,))
        t.start()


        running_flight = set(self.mock_flight_list)
        running_ground = set(self.mock_ground_list)
        dead_flight  = set()
        dead_ground  = set()
        while(run_test.isSet()):
            # Choose a random number of seconds until random kill
            num_s = random.randrange(0,action_limit_s) 

            # Choose between disconnecting a flight or ground client
            client_tuple = random.choice([(running_flight, dead_flight), (running_ground, dead_ground)])
            living_set = client_tuple[0]
            dead_set   = client_tuple[1]

            try:
                # Choose a random number of clients to kill
                num_to_kill = random.randrange(0, len(living_set))

                kill_set = set()
                for n in range(num_to_kill):
                    client = random.sample(living_set, 1)[0]
                    living_set.remove(client)
                    kill_set.add(client)
                    #self.logger.debug("Removing {} from living_set".format(client.name))


                kill_timer = Timer(num_s, Disconnect, args=(self, kill_set, dead_set))
                kill_timer.start()

            except ValueError:
                pass

            # Choose a random number of seconds until random connect
            num_s = random.randrange(0,action_limit_s)

            # Choose between connecting a flight or ground client
            client_tuple = random.choice([(running_flight, dead_flight), (running_ground, dead_ground)])
            living_set = client_tuple[0]
            dead_set   = client_tuple[1]

            # Choose a random number to connect
            try:
                num_to_conn = random.randrange(0, len(dead_set))


                revive_set = set()
                for n in range(num_to_conn):
                    client = random.sample(dead_set, 1)[0]
                    dead_set.remove(client)
                    revive_set.add(client)
                    #self.logger.debug("Adding {} to living_set".format(client.name))

                revive_timer = Timer(num_s, Connect, args=(self, revive_set, living_set))
                revive_timer.start()

            except ValueError:
                pass

            #self.logger.debug("RF %s"%[cli.name for cli in running_flight])
            #self.logger.debug("DF %s"%[cli.name for cli in dead_flight])
            #self.logger.debug("RG %s"%[cli.name for cli in running_ground])
            #self.logger.debug("DG %s"%[cli.name for cli in dead_ground])
            
            time.sleep(1) # Allow 1 second between montecarlo operations
        
        time.sleep(action_limit_s + 1) # Allow all clients to perform their action

        # Reconnect all dead clients
        #self.logger.debug("Dead Flight: {}".format([cli.name for cli in dead_flight]))
        for client in dead_flight:
            client.Start()
        #self.logger.debug("Dead Ground: {}".format([cli.name for cli in dead_ground]))
        for client in dead_ground:
            client.Start()

        time.sleep(2) # Allow clients to register with server


        # Wait until all are reconnected
        #while(len(running_flight) != len(self.mock_flight_list)):
        #    self.logger.debug("RF {} MF {}".format(len(running_flight), len(self.mock_flight_list)))
        #while(len(running_ground) != len(self.mock_ground_list)):
        #    pass






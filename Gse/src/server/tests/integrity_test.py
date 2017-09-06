import os
import sys
import zmq
import time
import struct
import signal
import random
import argparse
import datetime

from threading import Timer, Event
from subprocess import Popen

from logging import DEBUG, ERROR

from nose import with_setup

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.kernel import ZmqKernel
from server.tests.test_objects import *

from utils.logging_util import GetLogger

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()


class ServerIntegrityTest:
    """
    This test asserts the server remains stable
    in the face of random client disconnects at random times.
    """

    def __init__(self, opts):
        ## Must have build root set
        if os.environ['BUILD_ROOT'] is None:
            print("Must have BUILD_ROOT set.")
            print("Exiting.")
            sys.exit()

        SERVER_CONFIG.WipeServerLogs()
        log_path = SERVER_CONFIG.get("filepaths", "server_log_filepath")
        self.logger = GetLogger("MontecarloIntegrityTest_UTEST", log_path, logLevel=DEBUG, fileLevel=DEBUG)
        self.logger.debug("Logger Active")

        # Server cmd port
        cmd_port   = 5551
        address = "localhost"

        # Setup Ref App
        name = "flight_ref"
        self.ref_app = RefApp()
        self.ref_app.Setup(cmd_port, address, name)

        # Setup and start server
        self.server = ZmqServer()
        self.server.Setup(cmd_port, opts.verbose)
        self.server.Start()

        # Setup mock clients

        self.mock_flight_list = []
        for i in range(opts.num_flight):
            name   = "flight_{}".format(i)
            self.mock_flight_list.append( MockClient() )
            self.mock_flight_list[i].Setup(cmd_port, name, SERVER_CONFIG.FLIGHT_TYPE, opts.flight_throughput, opts.flight_size)

        self.mock_ground_list = []
        for i in range(opts.num_ground):
            name = "ground_{}".format(i)
            self.mock_ground_list.append( MockClient() )
            self.mock_ground_list[i].Setup(cmd_port, name, SERVER_CONFIG.GROUND_TYPE, opts.ground_throughput, opts.ground_size)
            

    def teardown_class(self):
        #self.flight_1.Quit()
        self.destory_clients()
        time.sleep(2)
        self.server.Quit()


    def start_clients(self):
        self.logger.info("Starting Clients")

        for client in self.mock_flight_list:
            client.Start()
        for client in self.mock_ground_list:
            client.Start()

    def destory_clients(self):
        self.logger.info("Destroying Clients")

        for client in self.mock_flight_list:
            client.Quit()
        for client in self.mock_ground_list:
            client.Quit()
        
    def passthrough(self, passthrough_time_s):
        time.sleep(10) # Wait in case clients are still connecting
        self.logger.info("-------- Pass Through Started --------")
        self.passthrough_time = datetime.datetime.now() # Save time of start
        time.sleep(passthrough_time_s)    

    def monte_carlo_disconnect(self, monte_carlo_time_s):
        if(monte_carlo_time_s == 0):
            return

        action_limit_s = 60 # Max time before a connect or kill is performed

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


def WriteAggregate(args):
    """
    Aggregate the data and add a description of the test.
    """
    print("Writing Aggregate")

    analysis_path = SERVER_CONFIG.get('filepaths','throughput_analysis_filepath')

    final_report_path = os.path.join(analysis_path, "aggregate.txt")
    final_report = open(final_report_path, "w")
    final_report.write("Number flight {}\n".format(args.num_flight))
    final_report.write("Number ground {}\n".format(args.num_ground))
    final_report.write("Flight throughput {} msg/s\n".format(args.flight_throughput))
    final_report.write("Flight msg size {} bytes\n".format(args.flight_size))
    final_report.write("Ground throughput {} msg/s\n".format(args.ground_throughput))
    final_report.write("Ground msg size {} bytes\n".format(args.ground_size))
    final_report.write("Montecarlo connect/disconnect time {} seconds\n".format(args.monte_time))
    final_report.write("Passthrough time {} seconds\n".format(args.pass_time))
    final_report.write("\n")

    for (path, dirs, files) in os.walk(analysis_path):
        for dir_name in dirs:
            dir_path = os.path.join(analysis_path, dir_name)
            report_path = os.path.join(dir_path, "report.txt")
            try:
                with open(report_path, "r") as f:
                    for line in f:
                        final_report.write(line)
                    final_report.write("\n")

            except IOError:
                print("Unable to open: {}".format(report_path))
                continue

    final_report.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="FPrime GSE Server Integrity Test")
    parser.add_argument('num_flight', metavar='num_flight', type=int, help="Number of flight clients")
    parser.add_argument('num_ground', metavar='num_ground', type=int, help="Number of ground clients")
    parser.add_argument('flight_throughput', metavar='flight_tp', type=int, help="Messages/second")
    parser.add_argument('flight_size', metavar='flight_msg_size', type=int, help="Bytes/message")
    parser.add_argument('ground_throughput', metavar='ground_tp', type=int, help="Messages/second")
    parser.add_argument('ground_size', metavar='ground_msg_size', type=int, help="Bytes/message")
    parser.add_argument('monte_time', metavar='monte_time', type=int, help="Seconds for montecarlo test")
    parser.add_argument('pass_time', metavar='pass_time', type=int, help="Seconds for data pass through")
    parser.add_argument('-v', '--verbose', action="store_true", help="Set verbose logging level.")

    args = parser.parse_args()  

    # Wipe previous throughput data
    analysis_path = SERVER_CONFIG.get('filepaths','throughput_analysis_filepath')

    test = ServerIntegrityTest(args)
    test.start_clients()

    test.monte_carlo_disconnect(args.monte_time)
    test.passthrough(args.pass_time)

    test.teardown_class()
    time.sleep(10) # Let server exit
    
    # Print aggregate throughput information
    WriteAggregate(args)
    time.sleep(2)

    # Check logs
    datetime_str = test.passthrough_time.strftime('%Y-%m-%d %H:%M:%S,%f') # Get the time of passthrough start
    cmd = "python continuity_log_check.py {} {} {}".format(datetime_str, args.num_flight, args.num_ground)
    p   = Popen(args=cmd, shell=True)
    p.wait()


   


    









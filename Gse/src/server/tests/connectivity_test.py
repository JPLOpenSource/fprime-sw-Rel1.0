import os
import zmq
import time
import struct
import threading
from multiprocessing import Process

from logging import DEBUG, ERROR

from server.ServerUtils.server_config import ServerConfig
from server.Kernel.kernel import ZmqKernel
from utils.logging_util import GetLogger

# Global server config class
SERVER_CONFIG = ServerConfig.getInstance()

def StartRefApp(server_cmd_port, address, name):
        cmd  = os.environ['BUILD_ROOT'] + "/Ref/darwin-darwin-x86-debug-llvm-bin/Ref"
        cmd += " -p {port} -a {addr} -n {nm}".format(port=server_cmd_port, addr=address, nm=name)

        print("Starting Ref App")
        print("Running command:")
        print(cmd)
        os.system(cmd)

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
        cmd_port = 5555 
        timeout_s  = 10

        cls.k = ZmqKernel(cmd_port, console_lvl=DEBUG, file_lvl=ERROR, timeout=timeout_s)  
        cls.kernel_process = Process(target=cls.k.Start)
        cls.kernel_process.start()

        # Start Red App
        cls.ref_process = Process(target=StartRefApp, args=(cmd_port, "localhost", "flight_1"))
        cls.ref_process.start()

        # Start 2 GSE GUIs
        cls.gui1_process = Process(target=StartGseGui, args=(cmd_port, "localhost", "gui_1", ["flight_1"]))
        cls.gui1_process.start()
        #StartGseGui(cmd_port, "localhost", "gui_2", "flight_1")


    @classmethod
    def teardown_class(cls):
        # Kill GUI
        cmd = "ps -ef | grep gse.py | head -n 1 | cut -f 2 -d ' '"
        pid = subprocess.check_output(cmd)
        print("GUI PID: {}".format(pid))
    


        cls.kernel_process.join()
        cls.ref_process.join()
        cls.gui1_process.join()


    def test_all(self):
        assert True

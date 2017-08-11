import os
import sys
import time
import logging
import signal
from subprocess import Popen

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
        #self._object_process.terminate()




class ZmqServer(TestObject):

    def Setup(self, server_cmd_port):
        cmd = "python " + os.environ['BUILD_ROOT'] + "/Gse/bin/run_server.py {} -v".format(server_cmd_port)

        self._args = cmd

    def Quit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGINT)
        #self._object_process.terminate()
        print("ZmqServerClosed")
        



class MockClient(TestObject):
    def __init__(self):
        super(MockClient, self).__init__()

    def Setup(self, cmd_port, client_name, client_type, throughput=0, msg_size=0):
        self.name = client_name


        args = "python " + os.environ['BUILD_ROOT'] + "/Gse/src/server/MockClients/MockClient.py {} {} {} {} {}"\
                .format(cmd_port, client_name, client_type, throughput, msg_size)

        self._args = args
        
    
    def Quit(self):
        pid = self._object_process.pid
        os.kill(pid, signal.SIGINT)
        #self._object_process.terminate()
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
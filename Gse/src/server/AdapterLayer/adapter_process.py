#===============================================================================
# NAME: adapter_process.py
#
# DESCRIPTION: AdapterProcess is a subclass of a multiprocessing.Process.
#              It provides a wrapper to start an Adapter and to stop the
#              Adapter when an interrupt is received.
#
# AUTHOR: David Kooi
#
# EMAIL: david.kooi@nasa.jpl.gov
#        dkooi@ucsc.edu
#
#
# Copyright 2017, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================


import signal
from multiprocessing import Process


class AdapterProcess(Process):
    """
    A Process wrapper for ZmqServer protocol adapters.
    """
    def __init__(self, Adapter):
        Process.__init__(self)
        self.__adapter = Adapter

    def run(self):
        """
        Called by AdapterProcess.start()

        Starts the adapter and quits the adapter when a
        signal is received.
        """
        self.__adapter.Start() 
        try:
            signal.pause() # Sleep until interrupted
        except KeyboardInterrupt:
            pass

        self.__adapter.Quit()


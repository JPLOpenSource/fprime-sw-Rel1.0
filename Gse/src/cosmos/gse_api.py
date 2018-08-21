#!/bin/env python
#===============================================================================
# NAME: gse_api.py
#
# DESCRIPTION: A basic API of command and telemetry monitoring capabilities,
#              implmented for the COSMOS http api
# AUTHOR: Aaron Doubek-Kraft
# EMAIL: aaron.doubek-kraft@jpl.nasa.gov
# DATE CREATED: 8/13/2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================
#
# Python standard modules

import sys
import os
import logging
import time
import signal

from utils import Logger
from utils.ConfigManager import ConfigManager

from cosmos import cosmos_telem_loader
from cosmos import cosmos_telem_queue
from cosmos import cosmos_command_sender
from cosmos import cosmos_http_request

class GseApi(object):
    """
    This class is a general API into the gse.py graphical functionality
    but is indepent of any GUI package.  It is used to build test applicaitons
    for commanding and listening to event and channel telemetry.

    This class will be used to build three command line applications which
    are:

    gse_send(...) to send a command.
    gse_send_and_wait(...) to send command and wait for log event or channel telemetry value.
    gse_monitor(...) to monitor for log event messages or channel telemetry values.
    If blocking then block and update console and log file, if not blocking then
    poll and if message then return it and update console and log file.
    """

    def __init__(self, server_addr='127.0.0.1', port=7777, generated_path='', build_root='', log_file_cmds=None, log_file_events=None, log_file_channel=None, log_file_path=None, log_file_updown=None, listener_enabled=False, verbose=False, deployment=None):
        """
        Constructor.
        @param server_addr: Socket server addr
        @param port: Socket server port number
        @param generated_path: Path to generated dictionaries (not applicable to COSMOS, but will try to parse deployment from here if provided)
        @param log_file_cmds: Name of command log file
        @param log_file_events: Name of log event log file
        @param log_file_channel: Name of channel telemetry log file
        @param log_file_path: Name of common directory path to save log files into
        @param listener_enabled: If True then event/channel telemetry listener thread enabled, else disabled
        @param verbose: Enable diagonistic display of information
        @param deployment: Name of target on COSMOS server
        """
        # 1. Create log files and loggers
        # 2. Load configuration for commands, events, channels, using cosmos API
        # 3. Start listener thread controllers.event_listern.py

        # For every console output log to a default file and stdout.
        logfile = time.strftime("%y%m%d%H%M%S", time.gmtime()) + '_GSEStdOut.log'
        #p = opts.log_file_path + os.sep + "stdout"
        p = '.' + os.sep + "stdout"
        if not os.path.exists(p):
            os.makedirs(p)
        f = p + os.sep + logfile

        # setup default for generated python command / telemetry descriptor files.
        # these are autocoded descriptions of all.
        #
        # Look for BUILD_ROOT and if not set look for generated in "." and then
        # in ".." and if not found then throw an exception.

        config = ConfigManager.getInstance()

        self.build_root = config.get("filepaths", "build_root")
        if 'BUILD_ROOT' in os.environ:
            self.build_root = os.environ['BUILD_ROOT']
        elif build_root != '':
            self.build_root = build_root
        else:
            print "WARNING: BUILD_ROOT not set. Specify on the command line, the environment, or gse.ini."

        # display configuration before starting GUI here...
        sep_line = 80*"="
        if verbose:
            logger = Logger.connectOutputLogger(f,'stdout', logging.INFO)
        else:
            logger = Logger.connectOutputLogger(f,'stdout', logging.WARNING)

        logger.info("Created log: %s" % f)
        logger.info("User: %s" % os.environ['USER'])
        (sysname, nodename, release, version, machine) = os.uname()
        logger.info("OS Name: %s" % sysname)
        logger.info("Machine Network Host Name: %s" % nodename)
        logger.info("Release: %s" % release)
        logger.info("Version: %s" % version)
        logger.info("Machine: %s" % machine)
        logger.info(sep_line)

        self.__url = 'http://' + str(server_addr) + ":" + str(port)
        self.__server_addr = server_addr
        self.__port = port
        self.__logger = logger

        deployment_key = ''
        gen_path_config = config.get("filepaths", "generated_path")
        if deployment is not None:
            #Use deployment if provided
            deployment_key = deployment.upper()
        elif generated_path is not '':
            #Parse from generated_path for backward compatibility
            deployment_key = os.path.basename(generated_path).upper()
        elif gen_path_config is not '':
            #Parse from generated_path retreived from config manager
            deployment_key = os.path.basename(gen_path_config).upper()
        else:
            #Try to load from COSMOS API, using first target besides 'SYSTEM'
            request = cosmos_http_request.COSMOSHTTPRequest(self.__url, "get_target_list", [])
            reply = request.send()
            try:
                deployments = reply["result"]
                for deployment in deployments:
                    if str(deployment) != 'SYSTEM':
                        deployment_key = deployment
                        break
                print "WARNING: No deployment specified, falling back on loading from COSMOS API"
            except KeyError:
                raise Exception("Couldn't get deployments, encountered error: '%s'" % (reply["error"]["message"]))

        print "Using deployment name %s" % deployment_key


        self._telem = cosmos_telem_loader.COSMOSTelemLoader(deployment_key, server_addr, port)
        self._telem_queue = cosmos_telem_queue.COSMOSTelemQueue(deployment_key, self.list("chans"), server_addr, port)
        self._evr_queue = cosmos_telem_queue.COSMOSTelemQueue(deployment_key, self.list("evrs"), server_addr, port)
        self._command_sender = cosmos_command_sender.COSMOSCommandSender(deployment_key, self.__url)

        super(GseApi, self).__init__()

    def disconnect(self):
        '''
        Unregister the listener queues with the COSMOS HTTP API
        '''
        self._telem_queue.destroy_subscription()
        self._evr_queue.destroy_subscription()
        #self._command_sender.destroy_subscription()

    class TimeoutException(Exception):
        pass

    def _timeout_sig_handler(self, signum, frame):
        raise self.TimeoutException()

    def __ctrl_c_sig_handler(self, signum, frame):
        raise Exception('Ctrl-C Received, Exiting.')

    def __loop_queue(self, id, type, timeout=None):
        """
        Grabs all telemetry and data in event listener's queue until the queried event / tlm id is found.
        Returns a tuple with two lists (tlm_list,evr_list)
        """

        tlm_list = []
        evr_list = []
        recv_id= ''

        if timeout:
            signal.signal(signal.SIGALRM, self._timeout_sig_handler)
            signal.alarm(timeout)
            print 'Waiting for', type, 'ID', id

        try:
            notFound = True
            while notFound:
                tlm, evr = self._pop_queue()
                if tlm is None and evr is None:
                    time.sleep(0.1)
                else:
                    if tlm:
                        tlm_name = tlm[0]
                        tlm_value = tlm[1]
                        tlm_id = self.get_tlm_id(tlm_name)
                        tlm_item = (tlm_id, tlm_value, tlm_name)
                        tlm_list.append(tlm_item)
                        if type == "ch" and id == tlm_id:
                            notFound = False
                    if evr:
                        evr_name = evr[0]
                        evr_value = evr[1]
                        evr_id = self.get_evr_id(evr_name)
                        evr_item = (evr_id, evr_value, evr_name)
                        evr_list.append(evr_item)
                        if type == "evr" and id == evr_id:
                            notFound = False

        except self.TimeoutException:
            print 'Timeout reached, unable to find', type, 'ID', id

        if timeout:
            signal.alarm(0)
        return tlm_list, evr_list

    def _pop_queue(self):
      """
      Grabs one event/telemetry from queue
      """
      evr = self._evr_queue.get_next_value()
      tlm = self._telem_queue.get_next_value()

      return tlm, evr

    def receive(self):
      """
      Grabs all telemetry and data in event listener's queue until the queue is emptied.
      Return a list of telemetry and events found.
      """

      tlm_list = []
      evr_list = []
      recv_id= ''

      empty = False
      while not empty:
        tlm, evr = self._pop_queue()
        if tlm is None and evr is None:
            empty = True
        else:
            if tlm:
                tlm_name = tlm[0]
                tlm_value = tlm[1]
                tlm_id = self.get_tlm_id(tlm_name)
                tlm_item = (tlm_id, tlm_value, tlm_name)
                tlm_list.append(tlm_item)
            if evr:
                evr_name = evr[0]
                evr_value = evr[1]
                evr_id = self.get_evr_id(evr_name)
                evr_item = (evr_id, evr_value, evr_name)
                evr_list.append(evr_item)

      return tlm_list, evr_list

    def flush(self):
      """
      Clears the telemetry/event queue and drops all data within it.
      """
      self.receive()

    def list(self, kind="cmds", ids=False):
        """
        Return a list of available commands, EVRs, or Channels.
        @param kind: kind of list desired: cmds, evrs, channels
        @param ids: if True return id numbers, else mnemonics
        @return: list of items
        """
        queryList = []

        if kind is "cmds":
            queryList = self._command_sender.get_opcode_dict().values() if ids else self._command_sender.get_name_dict().values()
        elif kind is "evrs":
            queryList = self._telem.get_event_id_dict().values() if ids else self._telem.get_event_name_dict().values()
        elif kind is "chans":
            queryList = self._telem.get_channel_id_dict().values() if ids else self._telem.get_channel_name_dict().values()
        else:
            print "Requested type is invalid."
        return queryList

    def send(self, cmd_name, args=None):
        """
        Send a command to the target applicaiton.
        @param cmd_name: Valid command mnemonic.
        @param args: Optional argument list for the command.
        """

        try:
            self._command_sender.send_command(cmd_name, args)
        except Exception:
            return -1

        if args is None:
            print 'Sent command', cmd_name
        else:
            print 'Sent command', cmd_name, 'with arguments', args

        return 0


    def send_file(self, src_path, dest_path, offset=0, data_size=512):
      """
      Send a file to the target application.
      If subprocess is True: starts a subprocess to handle the file upload.
      Else: Send file over current socket connection.
      @param src_path: Source path of file to be sent.
      @param dest_path: Destination path of file to be received by target application.
      @param offset: Byte offset into the source file (0 by default).
      @param data_size: Size of data packets (in bytes) being sent to application (default = 512).
      @param subprocess: Spawn new process
      @return: The subprocess if subprocess is True. UplinkStatus if subprocess is False.
      """
      pass

    def recieve_file(self, src, dest):
      """
      Request a file from target application.
      @param src: Source path
      @param dest: Destination path
      @param subprocess: Spawn new process
      @return: DownlinkStatus
      """
      pass

    def create_downlink_subprocess(self):
      """
      Start new process to listen for incoming files.
      @return: Downlink Process
      """
      pass

    def create_uplink_suprocess(self, src_path, dest_path):
      """
      Creates an uplink subprocess.
      @param src_path: Source path of file to be sent
      @param dest_path: Destination path of file to be recieved by target application
      @return: Uplink Process
      """
      pass

    def send_wait_evr(self, cmd_name, evr_name, args=None, timeout=5):
      """
      Send a command and wait (block) until a timeout for an event response.
      @param cmd_name: Valid command mnemonic.
      @param evr_name: the name of a specific EVR to wait for.
      @param args: Optional argument list for the command.
      @param timeout: Optional timeout in seconds (default is 5 seconds).
      @return: A tuple with two lists (tlm_list, evr_list) of data collected while waiting
      """
      # Use code in controllers.commander.Commander.cmd_send(...)
      # Wait by blocking on queue if listener enabled.  Or you block on
      # socket directly.  Reimplement the event_listern.update_task method
      # in this class.
      #TODO:what should return be if timeout
      status = self.send(cmd_name, args)
      if status == -1:
         return [], []
      return self.wait_evr(evr_name, timeout)

    def wait_evr(self, evr_name, timeout=5):
      """
      Wait (block) until a timeout for an event response
      @param evr_name: the name of a specific EVR to wait for.
      @param timeout: Optional timeout in seconds (default is 5 seconds).
      @return: A tuple with two lists (tlm_list, evr_list) of data collected while waiting
      """
      evr_id = self.get_evr_id(evr_name)
      return self.__loop_queue(evr_id, 'evr', timeout)

    def send_wait_tlm(self, cmd_name, tlm_name, args=None, timeout=5):
        """
        Send a command and wait (block) until a timeout for an channel response.
        @param cmd_name: Valid command mnemonic.
        @param tlm_name: the name of a specific tlm to wait for.
        @param args: Optional argument list for the command.
        @param timeout: Optional timeout in seconds (default is 5 seconds).
        @return: A tuple with two lists (tlm_list, evr_list) of data collected while waiting
        """
        # Use code in controllers.commander.Commander.cmd_send(...)
        # Wait by blocking on same queue if listener enabled.  This
        # reimplement the channel_listener.update() not to have the
        # gui notify(..) call.
        status = self.send(cmd_name,args)
        if status == -1:
           return [], []
        return self.wait_tlm(tlm_name, timeout)

    def wait_tlm(self, tlm_name, timeout=5):
        """
        Wait (block) until a timeout for an tlm response
        @param tlm_name: the name of a specific tlm to wait for.
        @param timeout: Optional timeout in seconds (default is 5 seconds).
        @return: A tuple with two lists (tlm_list, evr_list) of data collected while waiting
        """
        channel_id = self.get_tlm_id(tlm_name)
        return self.__loop_queue(channel_id, 'ch', timeout)

    def monitor_evr(self, id=None, blocking=True):
        """
        Monitors for log event messages with the COSMOS HTTP API.  The routine
        uses the python logging module to display to stdout and
        to a log file.
        @param id: This is ether a None for displaying any event log message,
        or a list of id integers for the messages desired to be displayed,
        or a list of string names of the mnemonic for each message to be displayed.
        @param blocking: If True the routine blocks and waits for each messge,
        False it will poll for a message and display if one is present otherwise
        return.
        """
        signal.signal(signal.SIGINT, self.__ctrl_c_sig_handler)
        try:
            while(True):
                evr = self._evr_queue.get_next_value(blocking)
                if evr is not None:
                    evr_name = evr[0]
                    evr_id = self.get_evr_id(evr_name)
                    if (id is None) or (evr_id in id) or (evr_name in id):
                        output = ' '.join(map(lambda item : str(item), evr))
                        self.__logger.info(output)

                if not blocking:
                    break

        except Exception:
            raise Exception


    def monitor_tlm(self, id=None, blocking=True):
        """
        Monitors for channel telemetry with the COSMOS HTTP API.  The routine
        uses the python logging module to display to stdout and
        to a log file.
        @param id: This is ether a None for displaying any channel telemetry,
        or a list of id integers for the channels desired to be displayed,
        or a list of string names of the mnemonic for each channel to be displayed.
        @param blocking: If True the routine blocks and waits for each channel update,
        False it will poll for a channel value and display if one is present otherwise
        return.
        """

        signal.signal(signal.SIGINT, self.__ctrl_c_sig_handler)
        try:
            while(True):
                tlm = self._telem_queue.get_next_value(blocking)
                if tlm is not None:
                    tlm_name = tlm[0]
                    tlm_id = self.get_tlm_id(tlm_name)
                    if (id is None) or (tlm_id in id) or (tlm_name in id):
                        output = ' '.join(map(lambda item : str(item), tlm))
                        self.__logger.info(output)

                if not blocking:
                    break
        except Exception:
            raise Exception

    def get_evr_id(self, evr_name):
      """
      Given an evr name, return the corresponding evr id
      @param evr_name: the name of a specific evr
      @return: the id of evr_name
      """
      return self._telem.get_event_id_dict()[evr_name.upper()]

    def get_tlm_id(self, tlm_name):
      """
      Given a tlm name, return the corresponding tlm id
      @param tlm_name: the name of a specific tlm
      @return: the id of tlm_name
      """
      return self._telem.get_channel_id_dict()[tlm_name.upper()]

    def get_cmd_id(self, command_name):
      """
      Given a command_name (mnemonic), return the corresponding command op code id
      @param command_name: the name of a specific command (mnemonic)
      @return: the id (op code) of command_name
      """
      return self._command_sender.get_opcode_dict()[command_name]

    def get_evr_name(self, evr_id):
      """
      Given an evr id, return the corresponding evr name
      @param evr_id: the id of a specific id
      @return: the name of evr_id
      """
      return self._telem.get_event_name_dict()[evr_id]

    def get_tlm_name(self, tlm_id):
      """
      Given a tlm id, return the corresponding tlm name
      @param tlm_id: the id of a specific tlm
      @return: the name of tlm_id
      """
      return self._telem.get_channel_name_dict()[tlm_id]

    def get_cmd_name(self, command_id):
      """
      Given a command_id (opcode), return the corresponding command name (mnemonic)
      @param command_id: the id of a specific command (opcode)
      @return: the name (mnemonic) of command_id
      """
      return self._command_sender.get_name_dict()[command_id]


def main():

    # Example usage of api methods
    api = GseApi(verbose=True, deployment="REF") #telemetry isn't logged with monitor_*() unless output is verbose
    print "\nStarting main() example script:\n"

    # Getters, setters, and listers
    cmd_list = api.list("cmds")
    evr_list = api.list("evrs")
    chan_list = api.list("chans")
    cmd_id_list = api.list("cmds", ids=True)
    evr_id_list = api.list("evrs", ids=True)
    chan_id_list = api.list("chans", ids=True)
    print "Channel " + chan_list[0] + " has id " + str(api.get_tlm_id(chan_list[0]))
    print "Channel with id " + str(chan_id_list[0]) + " is named " + api.get_tlm_name(chan_id_list[0])
    print "Event " + evr_list[0] + " has id " +  str(api.get_evr_id(evr_list[0]))
    print "Event with id " + str(evr_id_list[0]) + " is named " + api.get_evr_name(evr_id_list[0])
    print "Command " + cmd_list[0] + " has opcode " +  str(api.get_cmd_id(cmd_list[0]))
    print "Command with opcode " + str(cmd_id_list[0]) + " is named " + api.get_cmd_name(cmd_id_list[0])

    # List all channel and event values received
    print "\nTesting receive()"
    time.sleep(1) #Allow time for queue to populate with telemetry
    chan_values, evr_values = api.receive()
    print "Received channel values: " + str(chan_values)
    print "Received event values: " + str(evr_values)

    # Empty event and channel queues
    print "\nTesting flush()"
    time.sleep(1)
    api.flush()
    chan_values, evr_values = api.receive()
    print "Channel values after flush: " + str(chan_values)
    print "Event values after flush: " + str(chan_values)

    #send a command
    print "\nTesting send()"
    cmdSucceeded = api.send("CMD_NO_OP")
    print "Command succeeded" if cmdSucceeded == 0 else "Failed to send command"

    #wait for particular channel telemetry
    print "\nTesting wait_tlm()"
    print "Found " + str(api.wait_tlm("BD_CYCLES")[0][-1])

    #wait for a particular evr
    print "\nTesting wait_evr()"
    api.send("CMD_NO_OP")
    print "Found " + str(api.wait_evr("NOOPRECEIVED")[1][-1])

    #send a command and wait for a related EVR
    print "\nTesting send_wait_evr()"
    print "Found " + str(api.send_wait_evr("CMD_NO_OP_STRING", "NOOPSTRINGRECEIVED", [10, "Testing123"])[1][-1])

    #send a command and wait for related channel telemetry
    print "\nTesting send_wait_tlm()"
    print "Found " + str(api.send_wait_tlm("CMD_NO_OP", "COMMANDSDISPATCHED")[0][-1])

    # Log next event or channel packet to file, or none if no packets are queued
    print "\nTesting non-blocking monitor_evr() and monitor_tlm()"
    time.sleep(1)
    api.monitor_evr(blocking=False)
    api.monitor_tlm(blocking=False)

    # Log all channel or EVR telemetry to file until ctrl-c exit
    print "\nTesting blocking monitor_tlm() (channel telemetry will be logged until Ctrl-C exit)"
    try:
        api.monitor_tlm()
    except Exception:
        print "\nTesting blocking evr_tlm() (events will be logged until Ctrl-C exit)"

    try:
        api.monitor_evr()
    except Exception:
        print "\nTesting blocking monitor_tlm() with list of ids"

    try:
        api.monitor_tlm(id=['BD_CYCLES', 'SENDSTATE'])
    except Exception:
        print "\nTesting blocking monitor_evr() with list of ids"

    try:
        api.monitor_evr(id=['NOOPRECEIVED'])
    except Exception:
        print "\nDisconnecting and exiting"

    #cleanup remote queues
    api.disconnect()

if __name__ == "__main__":
    main()

#!/bin/env python
#===============================================================================
# NAME: cosmos_command_sender.py
#
# DESCRIPTION: Util class to send commands to COSMOS over HTTP.
# AUTHOR: Aaron Doubek-Kraft
# EMAIL: aaron.doubek-kraft@jpl.nasa.gov
# DATE CREATED: 8/16/2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from cosmos import cosmos_http_request
from cosmos import cosmos_command_loader

class COSMOSCommandSender:
    '''
    Class to send commands to a target via the COSMOS API over HTTP. Internally
    constructs a COSMOSCommandLoader instance to get all available commands and
    their arguments for the given target.
    '''

    def __init__(self, target, url):
        '''
        Constructor.
        @param target: name of this target on COSMOS telem server.
        @oaram url: url where COSMOS server listens for HTTP requests.
        '''
        self._target = target
        self._url = url
        self._command_loader = cosmos_command_loader.COSMOSCommandLoader(target, url)

    def _create_command_string(self, command, args):
        '''
        Given a command and an array of arguments to the command, create the
        corresponding COSMOS command string. COSMOS commands have the form
        'TARGET COMMAND with ARG1_NAME ARG1_VALUE, ..., ARGN_NAME, ARGN_VALUE'
        @param command: The name of the command.
        @param args: A list of arguments to the command.
        '''

        arg_metadata = self._command_loader.get_args(command)
        arg_str = ''

        if args is None and arg_metadata is not None:
            raise Exception("No arguments provided, but %s requires %d" % (command, len(arg_metadata)))

        if args is not None:
            if arg_metadata is None or len(args) != len(arg_metadata):
                reqd_arg_len = (0 if (arg_metadata is None) else len(arg_metadata))
                raise Exception("%d arguments provided, but %s takes %d" % (len(args), command, reqd_arg_len))

            arg_names = map(lambda arg : arg["name"], arg_metadata)
            arg_strs = []
            for (i, name) in enumerate(arg_names):
                arg_strs.append('%s %s' % (name, args[i]))

            arg_str = ' with '
            arg_str += ", ".join(arg_strs)

        return ('%s %s' % (self._target, command)) + arg_str


    def send_command(self, command, args=None):
        '''
        Send a command with the given arguments
        '''
        request = cosmos_http_request.COSMOSHTTPRequest(self._url, "cmd", [self._create_command_string(command, args)])
        reply = request.send()

        try:
            if ("result" in reply.keys()):
                return 0
            else:
                return -1
        except KeyError:
            return -1

    def get_opcode_dict(self):
        '''
        Get the opcode for a given command name for this target
        '''
        return self._command_loader.get_opcode_dict()

    def get_name_dict(self):
        '''
        Get the name of a command with the given opcode for this target
        '''
        return self._command_loader.get_name_dict()


def main():
    cmd = COSMOSCommandSender("REF", "http://localhost:7777")

    print "CMD_NO_OP has opcode %d" % cmd.get_opcode_dict()["CMD_NO_OP"]
    print "Sending CMD_NO_OP returned with status %d" % cmd.send_command("CMD_NO_OP")
    print "Sending CMD_NO_OP_STRING with arguments 8, 'TESTING1' returned with status %d" % cmd.send_command("CMD_NO_OP_STRING", [8, "TESTING1"])
    try:
        cmd.send_command("CMD_NO_OP", [1])
    except Exception, ex:
        print "Sending CMD_NO_OP with arguments raises exception '%s'" % ex.args[0]
    try:
        cmd.send_command("CMD_NO_OP_STRING")
    except Exception, ex:
        print "Sending CMD_NO_OP_STRING with no arguments raises exception '%s'" % ex.args[0]
    try:
        cmd.send_command("CMD_NO_OP_STRING", [7, "TESTING", "BADARG"])
    except Exception, ex:
        print "Sending CMD_NO_OP_STRING with wrong number of arguments raises exception '%s'" % ex.args[0]
    try:
        cmd.send_command("NOT_A_COMMAND", [])
    except Exception, ex:
        print "Sending invalid command raises exception '%s'" % ex.args[0]

if __name__ == '__main__':
    main()

#!/bin/env python
#===============================================================================
# NAME: cosmos_command_loader.py
#
# DESCRIPTION: Util class to load command dictionaries from COSMOS over HTTP
# AUTHOR: Aaron Doubek-Kraft
# EMAIL: aaron.doubek-kraft@jpl.nasa.gov
# DATE CREATED: 8/16/2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from cosmos import cosmos_http_request

class COSMOSCommandLoader:

    def __init__(self, target, url):
        self._target = target
        self._url = url
        self._name_dict = {}
        self._opcode_dict = {}
        self._arg_dict = {}
        self.load_dictionaries()

    def load_dictionaries(self):
        '''
        Query the COSMOS API to construct command dictionaries
        '''
        request = cosmos_http_request.COSMOSHTTPRequest(self._url, "get_cmd_list", [self._target])
        reply = request.send()

        try:
            # If request was successful, cmd_list will be an array of all command names
            cmd_list = map(lambda cmd_item : str(cmd_item[0]) , reply["result"])
        except KeyError:
            raise Exception("Couldn't load dictionaries, encountered error: " + reply["error"]["message"])

        for cmd_name in cmd_list:
            request = cosmos_http_request.COSMOSHTTPRequest(self._url, "get_cmd_param_list", [self._target, cmd_name])
            reply = request.send()

            try:
                params = reply["result"]
                arg_arr = []
                #params has form [SYNC, LENGTH, OPCODE, DESC, ARGS...]
                args = params[4:]
                opcode = params[3]
                for arg in args:
                    arg_arr.append({
                        "name": str(arg[0]),
                        "description": str(arg[3]),
                        "type": str(arg[7])
                    })
                self._opcode_dict[cmd_name] = opcode[1]
                self._arg_dict[cmd_name] = arg_arr if len(arg_arr) > 0 else None
            except KeyError:
                raise Exception("Couldn't get arguments for " + cmd_name + ", encountered error: " + reply["error"]["message"])

        # invert name -> opcode map to get names indexed by opcode
        self._name_dict = {opcode: name for (name, opcode) in self._opcode_dict.iteritems()}

    def get_name_dict(self):
        '''
        Get the name of a command with the given opcode
        '''
        return self._name_dict

    def get_opcode_dict(self):
        '''
        Get the opcode of a command with the given name
        '''
        return self._opcode_dict

    def get_args(self, command_name):
        '''
        Get an array of arguments for a command in this dictionary. Returns None
        if the command has no arguments.
        '''
        if command_name in self._arg_dict.keys():
            return self._arg_dict[command_name]
        else:
            raise Exception("Target %s has no command %s" % (self._target, command_name))

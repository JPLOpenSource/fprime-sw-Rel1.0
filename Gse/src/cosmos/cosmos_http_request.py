#!/bin/env python
#===============================================================================
# NAME: cosmos_http_request.py
#
# DESCRIPTION: Util class to make a COSMOS HTTP request
# AUTHOR: Aaron Doubek-Kraft
# EMAIL: aaron.doubek-kraft@jpl.nasa.gov
# DATE CREATED: 8/14/2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

import json

import requests

class COSMOSHTTPRequest:
    '''
    Simple abstraction class for making HTTP requests to the COSMOS API. Instantiated
    with the COSMOS API method and associated parameters, sets up the request
    in the proper format.
    '''
    def __init__(self, url, method, params):
        '''
        Constructor.
        @param url: The URL of the COSMOS HTTP server.
        @param method: The method name from the COSMOS API.
        @param params: The list of parameters for this method.
        '''
        self._url = url
        self._data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 0
        }

    def send(self):
        '''
        Send the HTTP request in this configuration as configured during instantiation.
        @return: the JSON reply from the request as a Python dictionary
        '''
        request = requests.post(self._url, json=self._data)
        return json.loads(request.text)

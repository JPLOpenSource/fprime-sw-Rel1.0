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
    def __init__(self, url, method, params):
        self._url = url
        self._data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 0
        }

    def send(self):
        '''
        Send the HTTP request in this configuration, and returns the JSON reply
        as a Python dictionary
        '''
        request = requests.post(self._url, json=self._data)
        return json.loads(request.text)

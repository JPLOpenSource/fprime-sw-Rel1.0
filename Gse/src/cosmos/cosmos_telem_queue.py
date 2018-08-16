#!/bin/env python
#===============================================================================
# NAME: cosmos_telem_queue.py
#
# DESCRIPTION: Util class to interact with a COSMOS subscription queue using the
#              http api. Provides methods to subscribe to a telemetry channel and
#              request the next method in the telemetry queue. COSMOS does not
#              distinguish between events and telemetry, so this interface works for both.
# AUTHOR: Aaron Doubek-Kraft
# EMAIL: aaron.doubek-kraft@jpl.nasa.gov
# DATE CREATED: 8/14/2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from cosmos import cosmos_http_request

class COSMOSTelemQueue:

    def __init__(self, target, channels, host, port):
        self.__target = target
        self.__channels = channels
        self.__host_url = 'http://' + str(host) + ':' + str(port)
        self.__queue_id = None # The ID of this queue on the COSMOS server
        self.setup_subscription()

    def setup_subscription(self):
        '''
        Register this queue's subscription with the COSMOS HTTP API for the given channels. This sets
        up a queue on the COSMOS server, which can then be queried for the next
        telemetry item with get_next_value()
        '''

        if (self.__queue_id is not None):
            raise Exception('Queue already registered: call destroy_subscription() to reset')

        req_params = [map(lambda channel : [self.__target, channel], self.__channels)]
        request = cosmos_http_request.COSMOSHTTPRequest(self.__host_url, "subscribe_packet_data", req_params)
        reply = request.send()

        try:
            self.__queue_id = reply["result"]
        except KeyError:
            raise Exception("Couldn't setup subscription, encountered error: " + reply["error"]["message"])

    def destroy_subscription(self):
        '''
        Unregister this queue's subscription with the COSMOS HTTP API.
        '''

        if (self.__queue_id is None):
            raise Exception('No queue registered, call setup_subscription()')

        request = cosmos_http_request.COSMOSHTTPRequest(self.__host_url, "unsubscribe_packet_data", [self.__queue_id])
        reply = request.send()

        try:
            status = reply["result"]
            self.__queue_id = None
        except KeyError:
            raise Exception("Couldn't setup subscription, encountered error: " + reply["error"]["message"])

    def get_next_value(self, blocking=False):
        '''
        Query the COSMOS api for the next data point in the queue. Default is 'blocking = False',
        which will return None if there are no additional items in the queue. Setting
        'blocking' to True will make this function block the process until
        data is available.
        '''
        if (self.__queue_id is None):
            raise Exception('No queue registered, call setup_subscription()')

        request = cosmos_http_request.COSMOSHTTPRequest(self.__host_url, "get_packet_data", [self.__queue_id, not blocking])
        reply = request.send()

        try:
            return self.format_telem(reply["result"])
        except KeyError:
            message = reply["error"]["message"]
            if (message == 'queue empty'):
                return None
            raise Exception("Couldn't get next value, encountered error: " + reply["error"]["message"])

    def format_telem(self, telem_arr):
        return (str(telem_arr[2]), telem_arr[5])

#!/bin/env python
#===============================================================================
# NAME: cosmos_telem_queue.py
#
# DESCRIPTION: Util class to interact with a COSMOS subscription queue using the
#              http api.
# AUTHOR: Aaron Doubek-Kraft
# EMAIL: aaron.doubek-kraft@jpl.nasa.gov
# DATE CREATED: 8/14/2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from cosmos import cosmos_http_request

class COSMOSTelemQueue:
    '''
    Class to interact with realtime telemetry via a COSMOS telemetry queue, while
    abstracting out the HTTP queries required.
    Provides methods to subscribe to a telemetry channel and
    request the next item in the telemetry queue. COSMOS does not
    distinguish between events and telemetry, so this interface works for both.
    '''

    def __init__(self, target, channels, host, port):
        '''
        Constructor.
        @param target: Name of this target on the COSMOS telemetry server
        @param channels: A list of the channels to include in the telemetry queue.
        @param host: Hostname for COSMOS telemetry server
        @param port: Port where COSMOS listens for HTTP requests
        '''
        self.__target = target
        self.__channels = channels
        self.__host_url = 'http://' + str(host) + ':' + str(port)
        self.__queue_id = None # The ID of this queue on the COSMOS server
        self.setup_subscription()

    def setup_subscription(self):
        '''
        Register a subscription with the COSMOS HTTP API for the channels
        with wich this queue was instantiated. This sets up a queue on the COSMOS server,
        which can then be queried for the next telemetry item with get_next_value().
        If the HTTP request returns with an error status, this will raise an exception.
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
        Unregister this queue's subscription with the COSMOS HTTP API. If HTTP request
        returns with an error status, this will raise an exception.
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
        data is available. If HTTP request returns with an error status other
        than 'queue empty', this will raise an exception.
        '''
        if (self.__queue_id is None):
            raise Exception('No queue registered, call setup_subscription()')

        request = cosmos_http_request.COSMOSHTTPRequest(self.__host_url, "get_packet_data", [self.__queue_id, not blocking])
        reply = request.send()

        try:
            telem = reply["result"]
        except KeyError:
            message = reply["error"]["message"]
            if (message == 'queue empty'):
                return None
            else:
                raise Exception("Couldn't get next value, encountered error: " + message)


        telem_name = str(telem[2])
        request = cosmos_http_request.COSMOSHTTPRequest(self.__host_url, "get_tlm_packet", [self.__target, telem_name])
        reply = request.send()
        value_item = filter(lambda item : item[0] == 'VALUE' or item[0] == 'MESSAGE', reply["result"])[0]

        return (telem_name, str(value_item[1]))

    def _format_telem(self, telem_arr):
        '''
        Format an array representing a telemetry item returned from the COSMOS API as a
        tuple consisting of (name, value).
        @param telem_arr: Telemetry item returned in the COSMOS format of
                         [RAW_PACKET, DEPLOYMENT, TELEMTRY_NAME, SECONDS, USECONDS, RECEIVED_COUNT]
        @return A tuple with (TELEMETRY_NAME, VALUE)
        '''
        print telem_arr
        return (str(telem_arr[2]), telem_arr[5])

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

import struct

from cosmos import cosmos_http_request
from cosmos import cosmos_telem_loader

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
        self.__loader_instance = cosmos_telem_loader.COSMOSTelemLoader.get_instance()
        self.__format_strings = {
            'UINT8': ">B",
            'UINT16': ">H",
            'UINT32': ">I",
            'UINT64': ">Q",
            'INT8': ">b",
            'INT16': ">h",
            'INT32': ">i",
            'INT64': ">q",
            'FLOAT32': ">f",
            'FLOAT64': ">d"
        }
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

        telem_buffer = telem[0]["raw"]
        telem_name = str(telem[2])
        if self.__loader_instance.is_event(telem_name):
            args = self._read_buffer(telem_buffer, telem_name)
            format_string = self.__loader_instance.get_format_string(telem_name)
            telem_value = args
        else:
            telem_value = self._read_buffer(telem_buffer, telem_name)[0]
        return (telem_name, telem_value)

    def _read_buffer(self, telem_buffer, telem_name):
        '''
        Read the values from a binary buffer
        @param telem_buffer: Buffer to read
        @param telem_name: Name of telemetry item that this packet came from
        @return A list of the values extracted from this buffer
        '''
        buffer_descriptions = self.__loader_instance.get_buffer_description(telem_name)
        formatted_values = []
        for value_buffer_desc in buffer_descriptions:
            type = str(value_buffer_desc["type"])
            if (type == "STRING"):
                # "size" field will be description of string length in binary packet
                value_buffer_desc_copy = dict(value_buffer_desc)
                str_length_bytes = self._read_buffer_item(telem_buffer, value_buffer_desc["size"])
                value_buffer_desc_copy["size"] = str_length_bytes * 8
                buffer_description = value_buffer_desc_copy
            else:
                buffer_description = value_buffer_desc

            formatted_values.append(self._read_buffer_item(telem_buffer, buffer_description))

        return formatted_values

    def _read_buffer_item(self, telem_buffer, buffer_description):
        '''
        Read a single item out of the buffer.
        @param telem_buffer: The buffer to read from
        @param buffer_description: The description of this buffer.
        @return The value of this buffer
        '''
        offset = buffer_description["offset"]
        states = buffer_description["states"]
        type = str(buffer_description["type"])
        size = buffer_description["size"]
        offset_bytes = offset/8
        size_bytes = size/8
        telem_value_buffer = telem_buffer[offset_bytes:offset_bytes+size_bytes]
        telem_value_bytes = bytearray(telem_value_buffer)
        telem_value = struct.unpack(self._get_format_string(type, size), telem_value_bytes)[0]
        if states is not None:
            formatted_value = states[telem_value]
        else:
            formatted_value = telem_value
        return formatted_value

    def _get_format_string(self, type, size):
        '''
        Get the type format string for Python's struct.unpack()
        @param type: Type name. One of INT, UINT, FLOAT, or STRING.
        @param size: The length of the type in bits
        '''
        if type == "STRING":
            return ">" + str(size / 8) + "s"
        else:
            type_code = type + str(size)
            return self.__format_strings[type_code]

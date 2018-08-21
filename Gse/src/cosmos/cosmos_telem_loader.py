#!/bin/env python
#===============================================================================
# NAME: cosmos_telem_loader.py
#
# DESCRIPTION: Util class to get telemetry and event metadata from COSMOS using
#              the HTTP API.
# EMAIL: aaron.doubek-kraft@jpl.nasa.gov
# DATE CREATED: 8/15/2018
#
# Copyright 2018, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================

from cosmos import cosmos_http_request

class COSMOSTelemLoader:
    '''
    Class to load event and channel metadata from COSMOS server.
    '''

    def __init__(self, target, host, port):
        '''
        Constructor.
        @param target: Name of this target on COSMOS server.
        @param host: Hostname of COSMOS telemetry server
        @param port: Port where COSMOS telem server listens for HTTP requests
        '''
        self._target = target
        self._host_url = 'http://' + str(host) + ':' + str(port)
        self._event_id_dict = {}
        self._channel_id_dict = {}
        self._descriptors = {
            "channel": 1,
            "event": 2
        }
        self.load_dictionaries()

    def load_dictionaries(self):
        '''
        Query COSMOS API to load channel and event names, and load them into
        dictionaries in the format {mnemonic: code}
        '''

        request = cosmos_http_request.COSMOSHTTPRequest(self._host_url, "get_tlm_list", [self._target])
        reply = request.send()

        try:
            # If request was successful, telem_list will be an array of all telemetry names
            telem_list = map(lambda telem_packet : str(telem_packet[0]) , reply["result"])
        except KeyError:
            raise Exception("Couldn't load dictionaries, encountered error: '%s'" % (reply["error"]["message"]))

        telem_decriptors = self.get_attribute_dict(telem_list, "DESC", "id_value")
        event_list = []
        channel_list = []

        for (telem_name, descriptor) in telem_decriptors.iteritems():
            # Separate telemtry into events and channels based on descriptor
            if descriptor == self._descriptors["event"]:
                event_list.append(telem_name)
            elif descriptor == self._descriptors["channel"]:
                channel_list.append(telem_name)

        #create map of id's indexed by name
        self._event_id_dict = self.get_attribute_dict(event_list, "EVR_ID", "id_value")
        self._channel_id_dict = self.get_attribute_dict(channel_list, "CHANNEL_ID", "id_value")

        #invert map to name indexed by id
        self._event_name_dict = {id: name for (name, id) in self._event_id_dict.iteritems()}
        self._channel_name_dict = {id: name for (name, id) in self._channel_id_dict.iteritems()}

    def get_attribute_dict(self, telem_list, field, attribute):
        '''
        For each telemetry item in telem_list, get the value of an attribute of a given field
        as a dictionary of {item_name: value ...} pairs.
        @param telem_list: List of telemetry names for which to query this attribute
        @param field: Field of this telemerty item to query (i.e. "VALUE", "EVR_ID", etc.)
        @param attribute: Attribute of this field to query.
        @return A dictionary of the form {telem_name: attribute_value ... }
        '''
        params = map(lambda telem_name: [self._target, telem_name, field], telem_list)
        request = cosmos_http_request.COSMOSHTTPRequest(self._host_url, "get_tlm_details", [params])
        reply = request.send()
        resultDict = {}

        try:
            items = reply["result"]
            for (i, attributes) in enumerate(items):
                resultDict[telem_list[i]] = attributes[attribute]
            return resultDict
        except KeyError:
            raise Exception("Failed to get attribute: " + reply["error"]["message"])


    def get_event_id_dict(self):
        '''
        Get dictionary of event ids indexed by name for this target.
        @return A dictionary of {event_name: event_id ...}
        '''
        return self._event_id_dict

    def get_channel_id_dict(self):
        '''
        Get dictionary of channel ids indexed by name for this target.
        @return A dictionary of {channel_name: channel_id ...}
        '''
        return self._channel_id_dict

    def get_event_name_dict(self):
        '''
        Get dictionary of event names indexed by id for this target.
        @return A dictionary of {event_id: event_name ...}
        '''
        return self._event_name_dict

    def get_channel_name_dict(self):
        '''
        Get dictionary of channel names indexed by id for this target
        @return A dictionary of {channel_id: channel_name ...}
        '''
        return self._channel_name_dict

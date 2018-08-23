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
    Singleton class to load event and channel metadata from COSMOS server.
    '''
    __instance = None

    def __init__(self):
        '''
        Constructor.
        '''
        self._target = None
        self._host_url = None
        self._event_id_dict = {}
        self._channel_id_dict = {}
        self._format_strings = {}
        self._buffer_value_desc = {}
        self._descriptors = {
            "channel": 1,
            "event": 2
        }

    def get_instance():
        """
        Return instance of singleton.
        """
        if(COSMOSTelemLoader.__instance is None):
            COSMOSTelemLoader.__instance = COSMOSTelemLoader()
        return COSMOSTelemLoader.__instance

    #define static method
    get_instance = staticmethod(get_instance)

    def set_target(self, target, host, port):
        '''
        Set the target of the singleton telemetry loader instance.
        @param target: Name of this target on COSMOS server.
        @param host: Hostname of COSMOS telemetry server
        @param port: Port where COSMOS telem server listens for HTTP requests
        '''
        if (self._target is None):
            self._target = target
            self._host_url = 'http://' + str(host) + ':' + str(port)
            self._load_dictionaries()
        else:
            raise Exception("Target already set, call unset_target() to release")

    def unset_target(self):
        '''
        Release this loader isntance to be used with a different target.
        '''
        self._target = None
        self._host_url = None

    def _load_dictionaries(self):
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

        #get size and offset of value in buffer for each channel
        channel_bit_offset_dict = self.get_attribute_dict(channel_list, "VALUE", "bit_offset")
        channel_bit_size_dict = self.get_attribute_dict(channel_list, "VALUE", "bit_size")
        channel_data_type_dict = self.get_attribute_dict(channel_list, "VALUE", "data_type")
        channel_state_dict = self.get_attribute_dict(channel_list, "VALUE", "states")
        self._buffer_value_desc = {}
        for channel in channel_list:
            if channel_state_dict[channel] is not None:
                channel_states = channel_state_dict[channel]
                inverted_channel_states = {id: str(name) for (name, id) in channel_states.iteritems()}
                states = inverted_channel_states
            else:
                states = None

            self._buffer_value_desc[channel] = [{
                "offset": channel_bit_offset_dict[channel],
                "size": channel_bit_size_dict[channel],
                "type": channel_data_type_dict[channel],
                "states": states
            }]

        event_metadata_dict = self.get_attribute_dict(event_list, "MESSAGE", "meta")
        for event in event_list:
            self._buffer_value_desc[event] = []
            for arg in event_metadata_dict[event]["ARGS"]:
                arg_name = arg.upper()
                arg_bit_offset = self.get_attribute_dict([event], arg_name, "bit_offset")[event]
                arg_bit_size = self.get_attribute_dict([event], arg_name, "bit_size")[event]
                arg_data_type = self.get_attribute_dict([event], arg_name, "data_type")[event]
                arg_states = self.get_attribute_dict([event], arg_name, "states")[event]

                if arg_states is not None:
                    arg_states = {id: str(name) for (name, id) in arg_states.iteritems()}

                # handle "String" type, which has an additional "Length" item which needed to be decoded
                if arg_data_type == "STRING":
                    arg_length_name = arg_name + "_LENGTH"
                    arg_length_bit_offset = self.get_attribute_dict([event], arg_length_name, "bit_offset")[event]
                    arg_length_bit_size = self.get_attribute_dict([event], arg_length_name, "bit_size")[event]
                    arg_length_data_type = self.get_attribute_dict([event], arg_length_name, "data_type")[event]
                    arg_bit_size = {
                        "name": arg_length_name,
                        "offset": arg_length_bit_offset,
                        "size": arg_length_bit_size,
                        "type": arg_length_data_type,
                        "states": None
                    }

                self._buffer_value_desc[event].append({
                    "name": arg_name,
                    "offset": arg_bit_offset,
                    "size": arg_bit_size,
                    "type": arg_data_type,
                    "states": arg_states
                })
            self._format_strings[event] = str(event_metadata_dict[event]["FORMAT_STRING"][0])

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

    def get_buffer_description(self, telem_name):
        '''
        Get the size, offset, and type of the value field of a binary buffer for channels
        or for an array of arguments for events
        '''
        return self._buffer_value_desc[telem_name]

    def get_format_string(self, telem_name):
        '''
        Get sprintf style format string for event
        @param telem_name
        '''
        return self._format_strings[telem_name]

    def is_event(self, telem_name):
        '''
        Returns True if the provided telemetry is an event, otherwise False
        @param telem_name: name of this telemetry in COSMOS dictionaries
        @return: Boolean
        '''
        return (telem_name in self._event_id_dict)

    def is_channel(self, telem_name):
        '''
        Returns True if the provided telemetry is an event, otherwise False
        @param telem_name: name of this telemetry in COSMOS dictionaries
        @return: Boolean
        '''
        return (telem_name in self._channel_id_dict)

def main():
    loader = COSMOSTelemLoader.get_instance()
    loader.set_target("REF", "localhost", 7777)

if __name__ == "__main__":
    main()

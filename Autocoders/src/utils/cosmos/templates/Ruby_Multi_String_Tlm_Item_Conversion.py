#!/usr/bin/env python




##################################################
## DEPENDENCIES
import sys
import os
import os.path
try:
    import builtins as builtin
except ImportError:
    import __builtin__ as builtin
from os.path import getmtime, exists
import time
import types
from Cheetah.Version import MinCompatibleVersion as RequiredCheetahVersion
from Cheetah.Version import MinCompatibleVersionTuple as RequiredCheetahVersionTuple
from Cheetah.Template import Template
from Cheetah.DummyTransaction import *
from Cheetah.NameMapper import NotFound, valueForName, valueFromSearchList, valueFromFrameOrSearchList
from Cheetah.CacheRegion import CacheRegion
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers

##################################################
## MODULE CONSTANTS
VFFSL=valueFromFrameOrSearchList
VFSL=valueFromSearchList
VFN=valueForName
currentTime=time.time
__CHEETAH_version__ = '2.4.4'
__CHEETAH_versionTuple__ = (2, 4, 4, 'development', 0)
__CHEETAH_genTime__ = 1529530817.17515
__CHEETAH_genTimestamp__ = 'Wed Jun 20 14:40:17 2018'
__CHEETAH_src__ = 'Ruby_Multi_String_Tlm_Item_Conversion.tmpl'
__CHEETAH_srcLastModified__ = 'Wed Jun 20 14:24:51 2018'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class Ruby_Multi_String_Tlm_Item_Conversion(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(Ruby_Multi_String_Tlm_Item_Conversion, self).__init__(*args, **KWs)
        if not self._CHEETAH__instanceInitialized:
            cheetahKWArgs = {}
            allowedKWs = 'searchList namespaces filter filtersLib errorCatcher'.split()
            for k,v in KWs.items():
                if k in allowedKWs: cheetahKWArgs[k] = v
            self._initCheetahInstance(**cheetahKWArgs)
        

    def respond(self, trans=None):



        ## CHEETAH: main method generated for this template
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        write(u'''# AUTO-GENERATED AS-IS TO LIB DIRECTORY BY COSMOSGEN.PY
# Converts BLOCK data type for commands with multiple strings into the proper packet format

# Converts BLOCK data type for commands with multiple strings into the proper packet format

require \'cosmos/conversions/conversion\'
module Cosmos
    # Allows for the usage of multiple variable-length arguments spread throughout
    # the telemetry packet.  Parses the packet\'s BLOCK item field and sets the
    # last argument defined in the constructor\'s template parameter as the value
    # for the current item.
    class MultiStringTlmItemConversion < Conversion
        BITS_IN_BYTE = 8
        
        # @param template [String] Instructions for parsing the raw data (the number
        #   of bits of each item) specified as a string of bit-number / data-type
        #   pairs beginning with the number of bits to pass over followed by the
        #   word START.  Example: "160 START 16 UINT 0 STRING 16 UINT 0 STRING"
        def initialize(template)
            super()
            @template = template.split(" ")
        end
        
        # @param (see Conversion#call)
        # @return [Integer|Float|Boolean|String] The value corresponding to
        #   the current item
        def call(value, packet, buffer)
            # Get hex string representation of all data in the current packet
            # Arguments defined in COSMOS library file packets.rb
            hex = buffer.formatted(1, 16, \' \', 0, false, \': \', false, \' \', \' \', \' \')
            
            return extract_item(hex)
        end
        
        # Converts a hex string to a signed integer
        # @param text [String] Hex string
        # @param bits [Integer] Bits for signed integer returned
        # @return [Integer] The converted signed integer
        def to_signed(text, bits)
            # Convert first from hex to unsigned integer
            temp = hex_convert(text, "UINT", 0)
            length = bits
            
            mid = 2**(length-1)
            max_uint = 2**length
            
            return (temp>=mid) ? temp - max_uint : temp
        end
        
        # Converts hex string to desired data type
        # @param text [String] Hex string
        # @param type [String] Desired data type.  Can be STRING UINT
        #   INT FLOAT or BOOLEAN.
        # @param bits [Integer] Bits for signed integer returned
        # @return [String|Integer|Float|Boolean] The converted value
        def hex_convert(text, type, bits)
            case type
                when "STRING"
                    return [(text).gsub(/\\s+/, "")].pack(\'H*\')
                when "UINT"
                    return (text).gsub(/\\s+/, "").to_i(16)
                when "INT"
                    return to_signed(text, bits)
                when "FLOAT"
                    # Convert hex to integer, then pack for sign, then unpack to float
                    if bits == 32
                        return [hex_convert((text).gsub(/\\s+/, ""), "INT", bits)].pack(\'L\').unpack(\'F\')[0]
                    elsif bits == 64
                        return [hex_convert((text).gsub(/\\s+/, ""), "INT", bits)].pack(\'Q\').unpack(\'D\')[0]
                    end
                when "BOOLEAN"
                    return hex_convert(text, "UINT", 0) == 0 ? true: false
            end
        end
        
        # Parses an argument specified in template from the full hex string
        # of all raw data in the current packet.  Example: 00 41 35 41 35 20 47
        # @param hex [String] Hex string of all packet data
        # @return [Integer|Float|Boolean|String] The value corresponding to
        #   the current item
        def extract_item(hex)
            text = hex.dup
            error_str = 0
            
            templ_arg_index = 2  # @template skips first 2 indexes because they define offset to first block item
            
            # Number of bytes until first non-BLOCK item
            bytes_to_pass = @template[0].to_i / BITS_IN_BYTE
            # Every 3 characters a new byte in hex string is passed
            chars_read = 0
            
            # Skip past all non-BLOCK items
            i = bytes_to_pass * 3
            
            # Iterate through all characters in hex string
            while i < text.length
                # Extract desired item because end of @template reached else pass over next item
                if templ_arg_index + 2 == @template.length or (@template[templ_arg_index + 2].to_i == 0 and templ_arg_index + 4 == @template.length)
                    # If normal data type else if string
                    if templ_arg_index + 2 == @template.length
                        len = @template[templ_arg_index].to_i / BITS_IN_BYTE
                        return hex_convert(text[i..i+len*3-1], @template[templ_arg_index + 1], @template[templ_arg_index].to_i)
                    else
                        len = @template[templ_arg_index].to_i / BITS_IN_BYTE
                        str_len = hex_convert(text[i..i+len*3-1], @template[templ_arg_index + 1], @template[templ_arg_index].to_i)
                        return hex_convert(text[i+len*3..i+len*3+str_len*3-1], @template[templ_arg_index + 3], @template[templ_arg_index + 2])
                    end
                else
                    # Pass over string and its length else pass over other data type
                    if @template[templ_arg_index + 2].to_i == 0
                        len = @template[templ_arg_index].to_i / BITS_IN_BYTE
                        i = i + len * 3 + hex_convert(text[i..i+len*3-1], @template[templ_arg_index + 1], @template[templ_arg_index].to_i) * 3
                        templ_arg_index = templ_arg_index + 4
                    else
                        i = i + @template[templ_arg_index].to_i / BITS_IN_BYTE * 3
                        templ_arg_index = templ_arg_index + 2
                    end
                end 
            end # while
            
            return error_str
        end
        
    end # class MultivariableTlmItemConversion
    
end # module Cosmos''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        
    ##################################################
    ## CHEETAH GENERATED ATTRIBUTES


    _CHEETAH__instanceInitialized = False

    _CHEETAH_version = __CHEETAH_version__

    _CHEETAH_versionTuple = __CHEETAH_versionTuple__

    _CHEETAH_genTime = __CHEETAH_genTime__

    _CHEETAH_genTimestamp = __CHEETAH_genTimestamp__

    _CHEETAH_src = __CHEETAH_src__

    _CHEETAH_srcLastModified = __CHEETAH_srcLastModified__

    _mainCheetahMethod_for_Ruby_Multi_String_Tlm_Item_Conversion= 'respond'

## END CLASS DEFINITION

if not hasattr(Ruby_Multi_String_Tlm_Item_Conversion, '_initCheetahAttributes'):
    templateAPIClass = getattr(Ruby_Multi_String_Tlm_Item_Conversion, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(Ruby_Multi_String_Tlm_Item_Conversion)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=Ruby_Multi_String_Tlm_Item_Conversion()).run()



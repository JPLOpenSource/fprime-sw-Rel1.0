# encoding: ascii-8bit

# Converts BLOCK data type for commands with multiple strings into the proper packet format for FPrime

require 'cosmos/conversions/conversion'
module Cosmos
    class MultivariableTlmItemConversion < Conversion
        BITS_IN_BYTE = 8
        
        # Template: instructions for parsing the raw data (the number of bits of each item)
        # Specified as a string of bit-number / data-type pairs beginning with the number
        # of bits to pass over followed by the word START
        # "160 START 16 UINT 0 STRING 16 UINT 0 STRING"
        def initialize(template)
            super()
            @template = template.split(" ")
        end
        def call(value, packet, buffer)
            # Get hex string representation of all data in the current packet
            # Arguments defined in COSMOS library file packets.rb
            hex = buffer.formatted(1, 16, ' ', 0, false, ': ', false, ' ', ' ', ' ')
            
            return extract_raw_data(hex)
        end
        
        # Removes whitespace and then "packs" Hex into variable of given type (all byte sizes identical)
        def hex_convert(text, type)
            case type
            when "STRING"
                return [(text).gsub(/\s+/, "")].pack('H*')
            when "INTEGER"
                return (text).gsub(/\s+/, "").to_i
            when "FLOAT"
                (text).gsub(/\s+/, "")
            when "BOOLEAN"
                return hex_convert(text, "INTEGER") == 0 ? true: false
            end
        end
        
        # Returns the last defined packet item in @templates from hex string example below
        # 00 41 35 41 35 20 47 55 49 20 00 00 00 1A 00 00 00
        def extract_raw_data(hex)
            text = hex.dup
            error_str = "ERROR" # Only returned if error
            
            templ_arg_index = 2 # @template skips first 2 indexes because they define first-item offset
            
            # Number of bytes until first non-BLOCK item
            bytes_to_pass = @template[0].to_i / BITS_IN_BYTE
             # Every 3 characters a new byte in hex string is passed
            chars_read = 0
            
            i = bytes_to_pass * 3   # Skip past all non-BLOCK items
            dataline_begin = 0 # Position of each line's raw_data to be appended to final string
            dataline_end = 0
            
            # Iterate through all characters in hex string
            while i < text.length
                # Extract desired item because end of @template reached else pass over next item
                if templ_arg_index + 2 == @template.length or (@template[templ_arg_index + 2].to_i == 0 and templ_arg_index + 4 == @template.length)
                    
                    # If normal data type else if string
                    if templ_arg_index + 2 == @template.length
                        len = @template[templ_arg_index].to_i / BITS_IN_BYTE
                        return hex_convert(text[i..i+len*3-1], @template[templ_arg_index + 1])
                    else
                        len = @template[templ_arg_index].to_i / BITS_IN_BYTE
                        str_len = hex_convert(text[i..i+len*3-1], "INTEGER")
                        return hex_convert(text[i+len*3..i+len*3+str_len*3-1], @template[templ_arg_index + 3])
                    end
                else
                    # Pass over string and its length else pass over other data type
                    if @template[templ_arg_index + 2].to_i == 0
                        len = @template[templ_arg_index].to_i / BITS_IN_BYTE
                        i = i + len * 3 + hex_convert(text[i..i+len*3-1], "INTEGER") * 3
                        templ_arg_index = templ_arg_index + 4
                    else
                        i = i + @template[templ_arg_index].to_i / BITS_IN_BYTE * 3
                        templ_arg_index = templ_arg_index + 2
                    end
                end
            end
            
            return error_str
        end
    end
end

# encoding: ascii-8bit

# Converts BLOCK data type for commands with multiple strings into the proper packet format for FPrime

require 'cosmos/conversions/conversion'
module Cosmos
    class ConvertToHexFprime < Conversion
        def initialize()
            super()

        end
        def call(value, packet, buffer)
            return 
        end
    end
end

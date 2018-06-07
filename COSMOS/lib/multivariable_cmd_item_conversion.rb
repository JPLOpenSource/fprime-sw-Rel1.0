# encoding: ascii-8bit

# Converts BLOCK data type for commands with multiple strings into the proper packet format for FPrime

require 'cosmos/conversions/conversion'
module Cosmos
    class MultivariableCmdItemConversion < Conversion
        def initialize(template)
            super()
            @template = template.split(" ")
        end
        def call(value, packet, buffer)
            return 0
        end
    end
end

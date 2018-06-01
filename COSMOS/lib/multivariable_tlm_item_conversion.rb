# encoding: ascii-8bit

# Converts BLOCK data type for commands with multiple strings into the proper packet format for FPrime

require 'cosmos/conversions/conversion'
module Cosmos
    class MultivariableTlmItemConversion < Conversion
        def initialize(template)
            super()
            @template = template.split(" ")
        end
        def call(value, packet, buffer)
            return value << @template.length
        end
    end
end

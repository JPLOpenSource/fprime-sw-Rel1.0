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
            cur_type_bits = -1
            for i in 0..(@template.length - 1) do
                if i % 2 == 0
                    cur_type_bits = @template[i].to_i
                else
                    value << cur_type_bits
                end
            end
            
            return value
        end
    end
end

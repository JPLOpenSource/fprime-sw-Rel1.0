# encoding: ascii-8bit

# Prints out EVR Strings within COSMOS Data Viewer application
# similar to gse.py application within FPrime

require 'cosmos'
require 'cosmos/tools/data_viewer/data_viewer_component'

module Cosmos
  # This class displays packets as raw hex values
  class EvrDumpComponent < DataViewerComponent
      
    # Prints the header strings for EVR's
    def initialize_gui
        super
        @text.appendPlainText("TIME\t\t\tNAME\t\tID\tSEVERITY\tMESSAGE\n" << '-' * 100)
    end
      
        
      #@text.appendPlainText("Test")

    # Processes the given packet. No gui interaction should be done in this
    # method. Override this method for other components.
    def process_packet (packet)
      processed_text = ''
      processed_text << "\n"
      processed_text << "#{packet.received_time.formatted}\t"
      processed_text << "#{packet.packet_name}\t"
      processed_text << "#{tlm_variable(packet.target_name + ' ' + packet.packet_name + ' EVR_ID', :RAW)}\t"
      processed_text << "COMMAND\t" # Hardcoded change later
      processed_text << "#{tlm_variable(packet.target_name + ' ' + packet.packet_name + ' MESSAGE', :RAW)}\t"

      # Ensure that queue does not grow infinitely while paused
      if @processed_queue.length < 1000
        @processed_queue << processed_text
      end
    end
  end
end

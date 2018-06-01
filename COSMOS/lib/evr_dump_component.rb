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
        @text.font = Cosmos.get_default_font
        @text.appendPlainText("TIME\t\t\tNAME\t\t\tID\tSEVERITY\t\tMESSAGE\n" << '-' * 115)
    end
      
        
      #@text.appendPlainText("Test")

    # Processes the given packet. No gui interaction should be done in this
    # method. Override this method for other components.
    def process_packet (packet)
      # Determine tab amount between columns
      sev_tabs = 2
      name_tabs = 2
      if "#{packet.packet_name}".length > (8 * 2)
          name_tabs = name_tabs - 1
      end
      if "#{tlm_variable(packet.target_name + ' ' + packet.packet_name + ' SEVERITY', :RAW)}".length > (8 * 1)
          sev_tabs = sev_tabs - 1
      end
      
      processed_text = ''
      processed_text << "\n"
      processed_text << "#{packet.received_time.formatted}\t"
      processed_text << "#{packet.packet_name}" << "\t" * name_tabs
      processed_text << "#{tlm_variable(packet.target_name + ' ' + packet.packet_name + ' EVR_ID', :RAW)}\t"
      processed_text << "#{tlm_variable(packet.target_name + ' ' + packet.packet_name + ' EVR_SEVERITY', :RAW)}" << "\t" * sev_tabs
      processed_text << "#{tlm_variable(packet.target_name + ' ' + packet.packet_name + ' MESSAGE', :RAW)}\t"

      # Ensure that queue does not grow infinitely while paused
      if @processed_queue.length < 1000
        @processed_queue << processed_text
      end
    end
  end
end

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
__CHEETAH_genTime__ = 1530131620.827514
__CHEETAH_genTimestamp__ = 'Wed Jun 27 13:33:40 2018'
__CHEETAH_src__ = 'Ruby_Evr_Dump_Component.tmpl'
__CHEETAH_srcLastModified__ = 'Wed Jun 20 09:05:13 2018'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class Ruby_Evr_Dump_Component(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(Ruby_Evr_Dump_Component, self).__init__(*args, **KWs)
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
# Prints out EVR Strings within COSMOS Data Viewer application
# similar to gse.py application within FPrime

require \'cosmos\'
require \'cosmos/tools/data_viewer/data_viewer_component\'

module Cosmos
  # This class displays packets as raw hex values
  class EvrDumpComponent < DataViewerComponent
      
    # Prints the header strings for EVR\'s
    def initialize_gui
        super
        @spaces = {
            "TIME" => 25,
            "NAME" => 25,
            "ID" => 10,
            "SEVERITY" => 15
        }
        @text.font = Cosmos.get_default_font
        @text.appendPlainText("TIME" + " " * @spaces["TIME"] + "NAME" + " " * @spaces["NAME"] + "ID" + " " * @spaces["ID"] + "SEVERITY" + " " * @spaces["SEVERITY"] + "MESSAGE\\n" << \'-\' * 130)
    end

    # Processes the given packet. No gui interaction should be done in this
    # method. Override this method for other components.
    def process_packet (packet)
      # Determine space amount between columns
      time_spaces = ("TIME".length + @spaces["TIME"]) - "#{packet.received_time.formatted}".length
      name_spaces = ("NAME".length + @spaces["NAME"]) - "#{packet.packet_name}".length
      id_spaces = ("ID".length + @spaces["ID"]) - "#{tlm_variable(packet.target_name + \' \' + packet.packet_name + \' EVR_ID\', :RAW)}".length
      severity_spaces = ("SEVERITY".length + @spaces["SEVERITY"]) - "#{tlm_variable(packet.target_name + \' \' + packet.packet_name + \' EVR_SEVERITY\', :RAW)}".length
      
      processed_text = \'\'
      processed_text << "\\n"
      processed_text << "#{packet.received_time.formatted}" << " " * time_spaces
      processed_text << "#{packet.packet_name}" << " " * name_spaces
      processed_text << "#{tlm_variable(packet.target_name + \' \' + packet.packet_name + \' EVR_ID\', :RAW)}" << " " * id_spaces
      processed_text << "#{tlm_variable(packet.target_name + \' \' + packet.packet_name + \' EVR_SEVERITY\', :RAW)}" << " " * severity_spaces
      processed_text << "#{tlm_variable(packet.target_name + \' \' + packet.packet_name + \' MESSAGE\', :RAW)}"

      # Ensure that queue does not grow infinitely while paused
      if @processed_queue.length < 1000
        @processed_queue << processed_text
      end
    end
  end
end
''')
        
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

    _mainCheetahMethod_for_Ruby_Evr_Dump_Component= 'respond'

## END CLASS DEFINITION

if not hasattr(Ruby_Evr_Dump_Component, '_initCheetahAttributes'):
    templateAPIClass = getattr(Ruby_Evr_Dump_Component, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(Ruby_Evr_Dump_Component)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=Ruby_Evr_Dump_Component()).run()



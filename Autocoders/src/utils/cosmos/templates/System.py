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
__CHEETAH_genTime__ = 1529447048.792567
__CHEETAH_genTimestamp__ = 'Tue Jun 19 15:24:08 2018'
__CHEETAH_src__ = 'System.tmpl'
__CHEETAH_srcLastModified__ = 'Thu Jun 14 09:58:09 2018'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class System(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(System, self).__init__(*args, **KWs)
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
        
        write(u'''# Created on ''')
        _v = VFFSL(SL,"user",True) # u'${user}' on line 1, col 14
        if _v is not None: write(_filter(_v, rawExpr=u'${user}')) # from line 1, col 14.
        write(u'''
# Author: ''')
        _v = VFFSL(SL,"date",True) # u'${date}' on line 2, col 11
        if _v is not None: write(_filter(_v, rawExpr=u'${date}')) # from line 2, col 11.
        write(u'''
''')
        write(u'''# THIS FILE IS AUTOMATICALLY GENERATED - ONLY ADD NEW TARGET DEFINITIONS
''')
        write(u'''# System Documentation: http://cosmosrb.com/docs/system/
# Declare Targets that make up the system
''')
        _v = '\n'
        if _v is not None: write(_filter(_v))
        write(u'''# DECLARE_TARGET target_name [substitute_name]
''')
        for name in VFFSL(SL,"names",True): # generated from line 10, col 1
            write(u'''DECLARE_TARGET ''')
            _v = VFFSL(SL,"name",True) # u'$name' on line 11, col 16
            if _v is not None: write(_filter(_v, rawExpr=u'$name')) # from line 11, col 16.
            write(u'''
''')
        write(u"""
# Listen Hosts - Ip addresses or hostnames to listen on when running the tools
LISTEN_HOST CTS_API 127.0.0.1
LISTEN_HOST TLMVIEWER_API 127.0.0.1
LISTEN_HOST CTS_PREIDENTIFIED 0.0.0.0 # 127.0.0.1 is more secure if you don't need external connections
LISTEN_HOST CTS_CMD_ROUTER 0.0.0.0 # 127.0.0.1 is more secure if you don't need external connections
# DECLARE_TARGET
# Connect Hosts - Ip addresses or hostnames to connect to when running the tools
CONNECT_HOST CTS_API 127.0.0.1
CONNECT_HOST TLMVIEWER_API 127.0.0.1
CONNECT_HOST CTS_PREIDENTIFIED 127.0.0.1
CONNECT_HOST CTS_CMD_ROUTER 127.0.0.1

# Ethernet Ports
PORT CTS_API 7777
PORT TLMVIEWER_API 7778
PORT CTS_PREIDENTIFIED 7779
PORT CTS_CMD_ROUTER 7780

# Default Packet Log Writer and Reader
DEFAULT_PACKET_LOG_WRITER packet_log_writer.rb
DEFAULT_PACKET_LOG_READER packet_log_reader.rb

# Paths
PATH LOGS ./outputs/logs
PATH TMP ./outputs/tmp
PATH SAVED_CONFIG ./outputs/saved_config
PATH TABLES ./outputs/tables
PATH HANDBOOKS ./outputs/handbooks
PATH PROCEDURES ./procedures

ALLOW_ACCESS ALL

# Initialize the metadata dialog using values from the following file:
META_INIT config/data/meta_init.txt

ADD_MD5_FILE lib/user_version.rb""")
        
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

    _mainCheetahMethod_for_System= 'respond'

## END CLASS DEFINITION

if not hasattr(System, '_initCheetahAttributes'):
    templateAPIClass = getattr(System, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(System)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=System()).run()



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
__CHEETAH_genTime__ = 1529427409.009339
__CHEETAH_genTimestamp__ = 'Tue Jun 19 09:56:49 2018'
__CHEETAH_src__ = 'Target.tmpl'
__CHEETAH_srcLastModified__ = 'Tue Jun 19 09:56:45 2018'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class Target(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(Target, self).__init__(*args, **KWs)
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
        _v = VFFSL(SL,"date",True) # u'${date}' on line 1, col 14
        if _v is not None: write(_filter(_v, rawExpr=u'${date}')) # from line 1, col 14.
        write(u'''
# Author: ''')
        _v = VFFSL(SL,"user",True) # u'${user}' on line 2, col 11
        if _v is not None: write(_filter(_v, rawExpr=u'${user}')) # from line 2, col 11.
        write(u'''
''')
        _v = '#\n'
        if _v is not None: write(_filter(_v))
        write(u'''# THIS FILE IS AUTOMATICALLY GENERATED - DO NOT EDIT!!!
''')
        _v = '#\n'
        if _v is not None: write(_filter(_v))
        write(u'''# Cosmos Documentation: http://cosmosrb.com/docs/

# Classes for handling multiple string items
REQUIRE multi_string_tlm_item_conversion.rb

# Ignored Parameters
# IGNORE_PARAMETER parameter_name
IGNORE_PARAMETER SYNC
IGNORE_PARAMETER DESC
IGNORE_PARAMETER LENGTH

# Automatically substitute the target name in screen definitions
AUTO_SCREEN_SUBSTITUTE
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

    _mainCheetahMethod_for_Target= 'respond'

## END CLASS DEFINITION

if not hasattr(Target, '_initCheetahAttributes'):
    templateAPIClass = getattr(Target, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(Target)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=Target()).run()



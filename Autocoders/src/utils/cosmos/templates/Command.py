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
__CHEETAH_genTime__ = 1530226865.939029
__CHEETAH_genTimestamp__ = 'Thu Jun 28 16:01:05 2018'
__CHEETAH_src__ = 'Command.tmpl'
__CHEETAH_srcLastModified__ = 'Wed Jun 27 10:11:31 2018'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class Command(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(Command, self).__init__(*args, **KWs)
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
        _v = "#\n"
        if _v is not None: write(_filter(_v))
        write(u'''# THIS FILE IS AUTOMATICALLY GENERATED - DO NOT EDIT!!!
''')
        _v = "#\n"
        if _v is not None: write(_filter(_v))
        write(u'''# Component Source: ''')
        _v = VFFSL(SL,"source",True) # u'${source}' on line 6, col 21
        if _v is not None: write(_filter(_v, rawExpr=u'${source}')) # from line 6, col 21.
        write(u'''

# SYNC: "''')
        _v = VFFSL(SL,"sync",True) # u'${sync}' on line 8, col 10
        if _v is not None: write(_filter(_v, rawExpr=u'${sync}')) # from line 8, col 10.
        write(u'''"
# FULL: "''')
        _v = VFFSL(SL,"full",True) # u'${full}' on line 9, col 10
        if _v is not None: write(_filter(_v, rawExpr=u'${full}')) # from line 9, col 10.
        write(u'''"
# PRIORITY: "''')
        _v = VFFSL(SL,"priority",True) # u'${priority}' on line 10, col 14
        if _v is not None: write(_filter(_v, rawExpr=u'${priority}')) # from line 10, col 14.
        write(u'''"
# COMPONENT: "''')
        _v = VFFSL(SL,"component_string",True) # u'${component_string}' on line 11, col 15
        if _v is not None: write(_filter(_v, rawExpr=u'${component_string}')) # from line 11, col 15.
        write(u'''"
COMMAND ''')
        _v = VFFSL(SL,"target_caps",True) # u'${target_caps}' on line 12, col 9
        if _v is not None: write(_filter(_v, rawExpr=u'${target_caps}')) # from line 12, col 9.
        write(u''' ''')
        _v = VFFSL(SL,"cmd_name",True) # u'${cmd_name}' on line 12, col 24
        if _v is not None: write(_filter(_v, rawExpr=u'${cmd_name}')) # from line 12, col 24.
        write(u''' ''')
        _v = VFFSL(SL,"endianness",True) # u'${endianness}' on line 12, col 36
        if _v is not None: write(_filter(_v, rawExpr=u'${endianness}')) # from line 12, col 36.
        write(u''' "''')
        _v = VFFSL(SL,"cmd_desc",True) # u'${cmd_desc}' on line 12, col 51
        if _v is not None: write(_filter(_v, rawExpr=u'${cmd_desc}')) # from line 12, col 51.
        write(u'''"
<%=render "_''')
        _v = VFFSL(SL,"target_lower",True) # u'${target_lower}' on line 13, col 30
        if _v is not None: write(_filter(_v, rawExpr=u'${target_lower}')) # from line 13, col 30.
        write(u'''_cmds_hdr.txt", locals: {id: ''')
        _v = VFFSL(SL,"opcode",True) # u'${opcode}' on line 13, col 74
        if _v is not None: write(_filter(_v, rawExpr=u'${opcode}')) # from line 13, col 74.
        write(u'''} %>
''')
        for name, desc, types, bit_offset, bits, type, min_val, max_val, default in VFFSL(SL,"cmd_items",True): # generated from line 14, col 5
            if VFFSL(SL,"bit_offset",True) < 0: # generated from line 15, col 5
                write(u'''    PARAMETER ''')
                _v = VFFSL(SL,"name",True) # u'$name' on line 16, col 15
                if _v is not None: write(_filter(_v, rawExpr=u'$name')) # from line 16, col 15.
                write(u''' ''')
                _v = VFFSL(SL,"bit_offset",True) # u'$bit_offset' on line 16, col 21
                if _v is not None: write(_filter(_v, rawExpr=u'$bit_offset')) # from line 16, col 21.
                write(u''' ''')
                _v = VFFSL(SL,"bits",True) # u'$bits' on line 16, col 33
                if _v is not None: write(_filter(_v, rawExpr=u'$bits')) # from line 16, col 33.
                write(u''' ''')
                _v = VFFSL(SL,"type",True) # u'$type' on line 16, col 39
                if _v is not None: write(_filter(_v, rawExpr=u'$type')) # from line 16, col 39.
                write(u''' ''')
                _v = VFFSL(SL,"min_val",True) # u'$min_val' on line 16, col 45
                if _v is not None: write(_filter(_v, rawExpr=u'$min_val')) # from line 16, col 45.
                write(u''' ''')
                _v = VFFSL(SL,"max_val",True) # u'$max_val' on line 16, col 54
                if _v is not None: write(_filter(_v, rawExpr=u'$max_val')) # from line 16, col 54.
                write(u''' ''')
                _v = VFFSL(SL,"default",True) # u'$default' on line 16, col 63
                if _v is not None: write(_filter(_v, rawExpr=u'$default')) # from line 16, col 63.
                write(u''' "''')
                _v = VFFSL(SL,"desc",True) # u'$desc' on line 16, col 73
                if _v is not None: write(_filter(_v, rawExpr=u'$desc')) # from line 16, col 73.
                write(u'''"
''')
                for type in VFFSL(SL,"types",True): # generated from line 17, col 7
                    write(u'''        STATE ''')
                    _v = VFFSL(SL,"type",True)[0] # u'$type[0]' on line 18, col 15
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[0]')) # from line 18, col 15.
                    write(u''' ''')
                    _v = VFFSL(SL,"type",True)[1] # u'$type[1]' on line 18, col 24
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[1]')) # from line 18, col 24.
                    write(u'''
''')
            else: # generated from line 20, col 5
                write(u'''    APPEND_PARAMETER ''')
                _v = VFFSL(SL,"name",True) # u'$name' on line 21, col 22
                if _v is not None: write(_filter(_v, rawExpr=u'$name')) # from line 21, col 22.
                write(u''' ''')
                _v = VFFSL(SL,"bits",True) # u'$bits' on line 21, col 28
                if _v is not None: write(_filter(_v, rawExpr=u'$bits')) # from line 21, col 28.
                write(u''' ''')
                _v = VFFSL(SL,"type",True) # u'$type' on line 21, col 34
                if _v is not None: write(_filter(_v, rawExpr=u'$type')) # from line 21, col 34.
                write(u''' ''')
                _v = VFFSL(SL,"min_val",True) # u'$min_val' on line 21, col 40
                if _v is not None: write(_filter(_v, rawExpr=u'$min_val')) # from line 21, col 40.
                write(u''' ''')
                _v = VFFSL(SL,"max_val",True) # u'$max_val' on line 21, col 49
                if _v is not None: write(_filter(_v, rawExpr=u'$max_val')) # from line 21, col 49.
                write(u''' ''')
                _v = VFFSL(SL,"default",True) # u'$default' on line 21, col 58
                if _v is not None: write(_filter(_v, rawExpr=u'$default')) # from line 21, col 58.
                write(u''' "''')
                _v = VFFSL(SL,"desc",True) # u'$desc' on line 21, col 68
                if _v is not None: write(_filter(_v, rawExpr=u'$desc')) # from line 21, col 68.
                write(u'''"
''')
                for type in VFFSL(SL,"types",True): # generated from line 22, col 7
                    write(u'''        STATE ''')
                    _v = VFFSL(SL,"type",True)[0] # u'$type[0]' on line 23, col 15
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[0]')) # from line 23, col 15.
                    write(u''' ''')
                    _v = VFFSL(SL,"type",True)[1] # u'$type[1]' on line 23, col 24
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[1]')) # from line 23, col 24.
                    write(u'''
''')
        write(u'''
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

    _mainCheetahMethod_for_Command= 'respond'

## END CLASS DEFINITION

if not hasattr(Command, '_initCheetahAttributes'):
    templateAPIClass = getattr(Command, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(Command)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=Command()).run()



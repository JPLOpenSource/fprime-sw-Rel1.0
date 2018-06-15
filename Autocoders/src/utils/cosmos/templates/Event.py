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
__CHEETAH_genTime__ = 1529085565.322517
__CHEETAH_genTimestamp__ = 'Fri Jun 15 10:59:25 2018'
__CHEETAH_src__ = 'Event.tmpl'
__CHEETAH_srcLastModified__ = 'Fri Jun 15 10:01:37 2018'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class Event(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(Event, self).__init__(*args, **KWs)
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
        write(u'''# Component Source: ''')
        _v = VFFSL(SL,"source",True) # u'${source}' on line 6, col 21
        if _v is not None: write(_filter(_v, rawExpr=u'${source}')) # from line 6, col 21.
        write(u'''

# COMPONENT: "''')
        _v = VFFSL(SL,"component_string",True) # u'${component_string}' on line 8, col 15
        if _v is not None: write(_filter(_v, rawExpr=u'${component_string}')) # from line 8, col 15.
        write(u'''"
TELEMETRY ''')
        _v = VFFSL(SL,"target_caps",True) # u'${target_caps}' on line 9, col 11
        if _v is not None: write(_filter(_v, rawExpr=u'${target_caps}')) # from line 9, col 11.
        write(u''' ''')
        _v = VFFSL(SL,"evr_name",True) # u'${evr_name}' on line 9, col 26
        if _v is not None: write(_filter(_v, rawExpr=u'${evr_name}')) # from line 9, col 26.
        write(u''' ''')
        _v = VFFSL(SL,"endianness",True) # u'${endianness}' on line 9, col 38
        if _v is not None: write(_filter(_v, rawExpr=u'${endianness}')) # from line 9, col 38.
        write(u''' "''')
        _v = VFFSL(SL,"evr_desc",True) # u'${evr_desc}' on line 9, col 53
        if _v is not None: write(_filter(_v, rawExpr=u'${evr_desc}')) # from line 9, col 53.
        write(u'''"
    <%=render "_''')
        _v = VFFSL(SL,"target_lower",True) # u'${target_lower}' on line 10, col 30
        if _v is not None: write(_filter(_v, rawExpr=u'${target_lower}')) # from line 10, col 30.
        write(u'''_tlm_evr_hdr.txt", locals: {id: ''')
        _v = VFFSL(SL,"id",True) # u'${id}' on line 10, col 77
        if _v is not None: write(_filter(_v, rawExpr=u'${id}')) # from line 10, col 77.
        write(u'''} %>

''')
        for block, derived, name, desc, template_string, types, neg_offset, bit_offset, bits, type in VFFSL(SL,"evr_items",True): # generated from line 12, col 5
            if VFFSL(SL,"block",True): # generated from line 13, col 5
                write(u'''    APPEND_ITEM EVR_ITEMS 0 BLOCK "Contains all other items"
''')
            elif VFFSL(SL,"derived",True): # generated from line 15, col 5
                write(u'''      ITEM ''')
                _v = VFFSL(SL,"name",True) # u'$name' on line 16, col 12
                if _v is not None: write(_filter(_v, rawExpr=u'$name')) # from line 16, col 12.
                write(u''' 0 0 DERIVED "''')
                _v = VFFSL(SL,"desc",True) # u'$desc' on line 16, col 31
                if _v is not None: write(_filter(_v, rawExpr=u'$desc')) # from line 16, col 31.
                write(u'''"
        READ_CONVERSION multivariable_tlm_item_conversion.rb "''')
                _v = VFFSL(SL,"template_string",True) # u'$template_string' on line 17, col 63
                if _v is not None: write(_filter(_v, rawExpr=u'$template_string')) # from line 17, col 63.
                write(u'''"
''')
                for type in VFFSL(SL,"types",True): # generated from line 18, col 9
                    write(u'''        # STATE ''')
                    _v = VFFSL(SL,"type",True)[0] # u'$type[0]' on line 19, col 17
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[0]')) # from line 19, col 17.
                    write(u''' ''')
                    _v = VFFSL(SL,"type",True)[1] # u'$type[1]' on line 19, col 26
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[1]')) # from line 19, col 26.
                    write(u'''
''')
            elif VFFSL(SL,"neg_offset",True): # generated from line 21, col 5
                write(u'''    ITEM ''')
                _v = VFFSL(SL,"name",True) # u'$name' on line 22, col 10
                if _v is not None: write(_filter(_v, rawExpr=u'$name')) # from line 22, col 10.
                write(u''' ''')
                _v = VFFSL(SL,"bit_offset",True) # u'$bit_offset' on line 22, col 16
                if _v is not None: write(_filter(_v, rawExpr=u'$bit_offset')) # from line 22, col 16.
                write(u''' ''')
                _v = VFFSL(SL,"bits",True) # u'$bits' on line 22, col 28
                if _v is not None: write(_filter(_v, rawExpr=u'$bits')) # from line 22, col 28.
                write(u''' ''')
                _v = VFFSL(SL,"type",True) # u'$type' on line 22, col 34
                if _v is not None: write(_filter(_v, rawExpr=u'$type')) # from line 22, col 34.
                write(u''' "''')
                _v = VFFSL(SL,"desc",True) # u'$desc' on line 22, col 41
                if _v is not None: write(_filter(_v, rawExpr=u'$desc')) # from line 22, col 41.
                write(u'''"
''')
                for type in VFFSL(SL,"types",True): # generated from line 23, col 7
                    write(u'''        # STATE ''')
                    _v = VFFSL(SL,"type",True)[0] # u'$type[0]' on line 24, col 17
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[0]')) # from line 24, col 17.
                    write(u''' ''')
                    _v = VFFSL(SL,"type",True)[1] # u'$type[1]' on line 24, col 26
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[1]')) # from line 24, col 26.
                    write(u'''
''')
            else: # generated from line 26, col 5
                write(u'''    APPEND_ITEM ''')
                _v = VFFSL(SL,"name",True) # u'$name' on line 27, col 17
                if _v is not None: write(_filter(_v, rawExpr=u'$name')) # from line 27, col 17.
                write(u''' ''')
                _v = VFFSL(SL,"bits",True) # u'$bits' on line 27, col 23
                if _v is not None: write(_filter(_v, rawExpr=u'$bits')) # from line 27, col 23.
                write(u''' ''')
                _v = VFFSL(SL,"type",True) # u'$type' on line 27, col 29
                if _v is not None: write(_filter(_v, rawExpr=u'$type')) # from line 27, col 29.
                write(u''' "''')
                _v = VFFSL(SL,"desc",True) # u'$desc' on line 27, col 36
                if _v is not None: write(_filter(_v, rawExpr=u'$desc')) # from line 27, col 36.
                write(u'''"
''')
                for type in VFFSL(SL,"types",True): # generated from line 28, col 7
                    write(u'''        # STATE ''')
                    _v = VFFSL(SL,"type",True)[0] # u'$type[0]' on line 29, col 17
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[0]')) # from line 29, col 17.
                    write(u''' ''')
                    _v = VFFSL(SL,"type",True)[1] # u'$type[1]' on line 29, col 26
                    if _v is not None: write(_filter(_v, rawExpr=u'$type[1]')) # from line 29, col 26.
                    write(u'''
''')
        write(u'''
    ITEM MESSAGE 0 0 DERIVED "Formatted String for Argument"
      GENERIC_READ_CONVERSION_START STRING 0
        sprintf("''')
        _v = VFFSL(SL,"format_string",True) # u'${format_string}' on line 36, col 18
        if _v is not None: write(_filter(_v, rawExpr=u'${format_string}')) # from line 36, col 18.
        write(u'''" ''')
        for name in VFFSL(SL,"nonlen_names",True) : # generated from line 37, col 1
            write(u""", packet.read('""")
            _v = VFFSL(SL,"name",True) # u'$name' on line 38, col 16
            if _v is not None: write(_filter(_v, rawExpr=u'$name')) # from line 38, col 16.
            write(u"""') """)
        write(u''')
      GENERIC_READ_CONVERSION_END
    ITEM EVR_SEVERITY 0 0 DERIVED "Severity"
      GENERIC_READ_CONVERSION_START STRING 0
        sprintf(\'''')
        _v = VFFSL(SL,"severity",True) # u'${severity}' on line 44, col 18
        if _v is not None: write(_filter(_v, rawExpr=u'${severity}')) # from line 44, col 18.
        write(u"""')
      GENERIC_READ_CONVERSION_END""")
        
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

    _mainCheetahMethod_for_Event= 'respond'

## END CLASS DEFINITION

if not hasattr(Event, '_initCheetahAttributes'):
    templateAPIClass = getattr(Event, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(Event)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=Event()).run()



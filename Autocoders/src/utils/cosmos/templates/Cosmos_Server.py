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
__CHEETAH_genTime__ = 1529363452.371112
__CHEETAH_genTimestamp__ = 'Mon Jun 18 16:10:52 2018'
__CHEETAH_src__ = 'Cosmos_Server.tmpl'
__CHEETAH_srcLastModified__ = 'Thu Jun 14 11:55:16 2018'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class Cosmos_Server(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(Cosmos_Server, self).__init__(*args, **KWs)
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
        write(u'''# THIS FILE IS AUTOMATICALLY GENERATED - DO NOT EDIT!!!
''')
        write(u'''# Interface Documentation: http://cosmosrb.com/docs/interfaces/

INTERFACE ''')
        _v = VFFSL(SL,"target_name",True) # u'${target_name}' on line 8, col 11
        if _v is not None: write(_filter(_v, rawExpr=u'${target_name}')) # from line 8, col 11.
        write(u'''_INT tcpip_server_interface.rb ''')
        _v = VFFSL(SL,"write_port",True) # u'${write_port}' on line 8, col 56
        if _v is not None: write(_filter(_v, rawExpr=u'${write_port}')) # from line 8, col 56.
        write(u''' ''')
        _v = VFFSL(SL,"read_port",True) # u'${read_port}' on line 8, col 70
        if _v is not None: write(_filter(_v, rawExpr=u'${read_port}')) # from line 8, col 70.
        write(u''' ''')
        _v = VFFSL(SL,"read_timeout",True) # u'${read_timeout}' on line 8, col 83
        if _v is not None: write(_filter(_v, rawExpr=u'${read_timeout}')) # from line 8, col 83.
        write(u''' ''')
        _v = VFFSL(SL,"write_timeout",True) # u'${write_timeout}' on line 8, col 99
        if _v is not None: write(_filter(_v, rawExpr=u'${write_timeout}')) # from line 8, col 99.
        write(u''' nil
  TARGET ''')
        _v = VFFSL(SL,"target_name",True) # u'${target_name}' on line 9, col 10
        if _v is not None: write(_filter(_v, rawExpr=u'${target_name}')) # from line 9, col 10.
        write(u'''
  PROTOCOL WRITE ''')
        _v = VFFSL(SL,"protocol_name_w",True) # u'${protocol_name_w}' on line 10, col 18
        if _v is not None: write(_filter(_v, rawExpr=u'${protocol_name_w}')) # from line 10, col 18.
        write(u''' ''')
        _v = VFFSL(SL,"len_bit_offset_w",True) # u'${len_bit_offset_w}' on line 10, col 37
        if _v is not None: write(_filter(_v, rawExpr=u'${len_bit_offset_w}')) # from line 10, col 37.
        write(u''' ''')
        _v = VFFSL(SL,"len_bit_size_w",True) # u'${len_bit_size_w}' on line 10, col 57
        if _v is not None: write(_filter(_v, rawExpr=u'${len_bit_size_w}')) # from line 10, col 57.
        write(u''' ''')
        _v = VFFSL(SL,"len_val_offset_w",True) # u'${len_val_offset_w}' on line 10, col 75
        if _v is not None: write(_filter(_v, rawExpr=u'${len_val_offset_w}')) # from line 10, col 75.
        write(u''' ''')
        _v = VFFSL(SL,"bytes_per_count_w",True) # u'${bytes_per_count_w}' on line 10, col 95
        if _v is not None: write(_filter(_v, rawExpr=u'${bytes_per_count_w}')) # from line 10, col 95.
        write(u''' ''')
        _v = VFFSL(SL,"endianness_w",True) # u'${endianness_w}' on line 10, col 116
        if _v is not None: write(_filter(_v, rawExpr=u'${endianness_w}')) # from line 10, col 116.
        write(u''' ''')
        _v = VFFSL(SL,"discard_leading_w",True) # u'${discard_leading_w}' on line 10, col 132
        if _v is not None: write(_filter(_v, rawExpr=u'${discard_leading_w}')) # from line 10, col 132.
        write(u''' ''')
        _v = VFFSL(SL,"sync_w",True) # u'${sync_w}' on line 10, col 153
        if _v is not None: write(_filter(_v, rawExpr=u'${sync_w}')) # from line 10, col 153.
        write(u''' ''')
        _v = VFFSL(SL,"has_max_length_w",True) # u'${has_max_length_w}' on line 10, col 163
        if _v is not None: write(_filter(_v, rawExpr=u'${has_max_length_w}')) # from line 10, col 163.
        write(u''' ''')
        _v = VFFSL(SL,"fill_ls_w",True) # u'${fill_ls_w}' on line 10, col 183
        if _v is not None: write(_filter(_v, rawExpr=u'${fill_ls_w}')) # from line 10, col 183.
        write(u'''
  PROTOCOL READ  ''')
        _v = VFFSL(SL,"protocol_name_r",True) # u'${protocol_name_r}' on line 11, col 18
        if _v is not None: write(_filter(_v, rawExpr=u'${protocol_name_r}')) # from line 11, col 18.
        write(u''' ''')
        _v = VFFSL(SL,"len_bit_offset_r",True) # u'${len_bit_offset_r}' on line 11, col 37
        if _v is not None: write(_filter(_v, rawExpr=u'${len_bit_offset_r}')) # from line 11, col 37.
        write(u''' ''')
        _v = VFFSL(SL,"len_bit_size_r",True) # u'${len_bit_size_r}' on line 11, col 57
        if _v is not None: write(_filter(_v, rawExpr=u'${len_bit_size_r}')) # from line 11, col 57.
        write(u''' ''')
        _v = VFFSL(SL,"len_val_offset_r",True) # u'${len_val_offset_r}' on line 11, col 75
        if _v is not None: write(_filter(_v, rawExpr=u'${len_val_offset_r}')) # from line 11, col 75.
        write(u''' ''')
        _v = VFFSL(SL,"bytes_per_count_r",True) # u'${bytes_per_count_r}' on line 11, col 95
        if _v is not None: write(_filter(_v, rawExpr=u'${bytes_per_count_r}')) # from line 11, col 95.
        write(u''' ''')
        _v = VFFSL(SL,"endianness_r",True) # u'${endianness_r}' on line 11, col 116
        if _v is not None: write(_filter(_v, rawExpr=u'${endianness_r}')) # from line 11, col 116.
        write(u''' ''')
        _v = VFFSL(SL,"discard_leading_r",True) # u'${discard_leading_r}' on line 11, col 132
        if _v is not None: write(_filter(_v, rawExpr=u'${discard_leading_r}')) # from line 11, col 132.
        write(u''' ''')
        _v = VFFSL(SL,"sync_r",True) # u'${sync_r}' on line 11, col 153
        if _v is not None: write(_filter(_v, rawExpr=u'${sync_r}')) # from line 11, col 153.
        write(u''' ''')
        _v = VFFSL(SL,"has_max_length_r",True) # u'${has_max_length_r}' on line 11, col 163
        if _v is not None: write(_filter(_v, rawExpr=u'${has_max_length_r}')) # from line 11, col 163.
        write(u''' ''')
        _v = VFFSL(SL,"fill_ls_r",True) # u'${fill_ls_r}' on line 11, col 183
        if _v is not None: write(_filter(_v, rawExpr=u'${fill_ls_r}')) # from line 11, col 183.
        
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

    _mainCheetahMethod_for_Cosmos_Server= 'respond'

## END CLASS DEFINITION

if not hasattr(Cosmos_Server, '_initCheetahAttributes'):
    templateAPIClass = getattr(Cosmos_Server, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(Cosmos_Server)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=Cosmos_Server()).run()


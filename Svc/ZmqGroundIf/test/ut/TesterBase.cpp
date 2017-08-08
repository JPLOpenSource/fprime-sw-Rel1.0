// ======================================================================
// \title  ZmqGroundIf/test/ut/TesterBase.cpp
// \author Auto-generated
// \brief  cpp file for ZmqGroundIf component test harness base class
//
// \copyright
// Copyright 2009-2016, by the California Institute of Technology.
// ALL RIGHTS RESERVED.  United States Government Sponsorship
// acknowledged. Any commercial use must be negotiated with the Office
// of Technology Transfer at the California Institute of Technology.
//
// This software may be subject to U.S. export control laws and
// regulations.  By accepting this document, the user agrees to comply
// with all U.S. export laws and regulations.  User has the
// responsibility to obtain export licenses, or other export authority
// as may be required before exporting such information to foreign
// countries or providing access to foreign persons.
// ======================================================================

#include <stdlib.h>
#include <string.h>
#include "TesterBase.hpp"

namespace Zmq {

  // ----------------------------------------------------------------------
  // Construction, initialization, and destruction
  // ----------------------------------------------------------------------

  ZmqGroundIfTesterBase ::
    ZmqGroundIfTesterBase(
#if FW_OBJECT_NAMES == 1
        const char *const compName,
        const U32 maxHistorySize
#else
        const U32 maxHistorySize
#endif
    ) :
#if FW_OBJECT_NAMES == 1
      Fw::PassiveComponentBase(compName)
#else
      Fw::PassiveComponentBase()
#endif
  {
    // Initialize histories for typed user output ports
    this->fromPortHistory_fileUplinkBufferSendOut =
      new History<FromPortEntry_fileUplinkBufferSendOut>(maxHistorySize);
    this->fromPortHistory_uplinkPort =
      new History<FromPortEntry_uplinkPort>(maxHistorySize);
    this->fromPortHistory_fileDownlinkBufferSendOut =
      new History<FromPortEntry_fileDownlinkBufferSendOut>(maxHistorySize);
    this->fromPortHistory_fileUplinkBufferGet =
      new History<FromPortEntry_fileUplinkBufferGet>(maxHistorySize);
    // Clear history
    this->clearHistory();
  }

  ZmqGroundIfTesterBase ::
    ~ZmqGroundIfTesterBase(void) 
  {
  }

  void ZmqGroundIfTesterBase ::
    init(
        const NATIVE_INT_TYPE instance
    )
  {

    // Initialize base class

		Fw::PassiveComponentBase::init(instance);

    // Attach input port fileUplinkBufferSendOut

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_fileUplinkBufferSendOut();
        ++_port
    ) {

      this->m_from_fileUplinkBufferSendOut[_port].init();
      this->m_from_fileUplinkBufferSendOut[_port].addCallComp(
          this,
          from_fileUplinkBufferSendOut_static
      );
      this->m_from_fileUplinkBufferSendOut[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_fileUplinkBufferSendOut[%d]",
          this->m_objName,
          _port
      );
      this->m_from_fileUplinkBufferSendOut[_port].setObjName(_portName);
#endif

    }

    // Attach input port Log

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_Log();
        ++_port
    ) {

      this->m_from_Log[_port].init();
      this->m_from_Log[_port].addCallComp(
          this,
          from_Log_static
      );
      this->m_from_Log[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_Log[%d]",
          this->m_objName,
          _port
      );
      this->m_from_Log[_port].setObjName(_portName);
#endif

    }

    // Attach input port LogText

#if FW_ENABLE_TEXT_LOGGING == 1
    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_LogText();
        ++_port
    ) {

      this->m_from_LogText[_port].init();
      this->m_from_LogText[_port].addCallComp(
          this,
          from_LogText_static
      );
      this->m_from_LogText[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_LogText[%d]",
          this->m_objName,
          _port
      );
      this->m_from_LogText[_port].setObjName(_portName);
#endif

    }
#endif

    // Attach input port Time

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_Time();
        ++_port
    ) {

      this->m_from_Time[_port].init();
      this->m_from_Time[_port].addCallComp(
          this,
          from_Time_static
      );
      this->m_from_Time[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_Time[%d]",
          this->m_objName,
          _port
      );
      this->m_from_Time[_port].setObjName(_portName);
#endif

    }

    // Attach input port uplinkPort

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_uplinkPort();
        ++_port
    ) {

      this->m_from_uplinkPort[_port].init();
      this->m_from_uplinkPort[_port].addCallComp(
          this,
          from_uplinkPort_static
      );
      this->m_from_uplinkPort[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_uplinkPort[%d]",
          this->m_objName,
          _port
      );
      this->m_from_uplinkPort[_port].setObjName(_portName);
#endif

    }

    // Attach input port fileDownlinkBufferSendOut

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_fileDownlinkBufferSendOut();
        ++_port
    ) {

      this->m_from_fileDownlinkBufferSendOut[_port].init();
      this->m_from_fileDownlinkBufferSendOut[_port].addCallComp(
          this,
          from_fileDownlinkBufferSendOut_static
      );
      this->m_from_fileDownlinkBufferSendOut[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_fileDownlinkBufferSendOut[%d]",
          this->m_objName,
          _port
      );
      this->m_from_fileDownlinkBufferSendOut[_port].setObjName(_portName);
#endif

    }

    // Attach input port fileUplinkBufferGet

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_fileUplinkBufferGet();
        ++_port
    ) {

      this->m_from_fileUplinkBufferGet[_port].init();
      this->m_from_fileUplinkBufferGet[_port].addCallComp(
          this,
          from_fileUplinkBufferGet_static
      );
      this->m_from_fileUplinkBufferGet[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_fileUplinkBufferGet[%d]",
          this->m_objName,
          _port
      );
      this->m_from_fileUplinkBufferGet[_port].setObjName(_portName);
#endif

    }

    // Initialize output port downlinkPort

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_to_downlinkPort();
        ++_port
    ) {
      this->m_to_downlinkPort[_port].init();

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      snprintf(
          _portName,
          sizeof(_portName),
          "%s_to_downlinkPort[%d]",
          this->m_objName,
          _port
      );
      this->m_to_downlinkPort[_port].setObjName(_portName);
#endif

    }

    // Initialize output port fileDownlinkBufferSendIn

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_to_fileDownlinkBufferSendIn();
        ++_port
    ) {
      this->m_to_fileDownlinkBufferSendIn[_port].init();

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      snprintf(
          _portName,
          sizeof(_portName),
          "%s_to_fileDownlinkBufferSendIn[%d]",
          this->m_objName,
          _port
      );
      this->m_to_fileDownlinkBufferSendIn[_port].setObjName(_portName);
#endif

    }

  }

  // ----------------------------------------------------------------------
  // Getters for port counts
  // ----------------------------------------------------------------------

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_from_fileUplinkBufferSendOut(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_fileUplinkBufferSendOut);
  }

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_from_Log(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_Log);
  }

#if FW_ENABLE_TEXT_LOGGING == 1
  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_from_LogText(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_LogText);
  }
#endif

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_to_downlinkPort(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_to_downlinkPort);
  }

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_from_Time(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_Time);
  }

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_from_uplinkPort(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_uplinkPort);
  }

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_from_fileDownlinkBufferSendOut(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_fileDownlinkBufferSendOut);
  }

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_to_fileDownlinkBufferSendIn(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_to_fileDownlinkBufferSendIn);
  }

  NATIVE_INT_TYPE ZmqGroundIfTesterBase ::
    getNum_from_fileUplinkBufferGet(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_fileUplinkBufferGet);
  }

  // ----------------------------------------------------------------------
  // Connectors for to ports 
  // ----------------------------------------------------------------------

  void ZmqGroundIfTesterBase ::
    connect_to_downlinkPort(
        const NATIVE_INT_TYPE portNum,
        Fw::InputComPort *const downlinkPort
    ) 
  {
    FW_ASSERT(portNum < this->getNum_to_downlinkPort(),static_cast<AssertArg>(portNum));
    this->m_to_downlinkPort[portNum].addCallPort(downlinkPort);
  }

  void ZmqGroundIfTesterBase ::
    connect_to_fileDownlinkBufferSendIn(
        const NATIVE_INT_TYPE portNum,
        Fw::InputBufferSendPort *const fileDownlinkBufferSendIn
    ) 
  {
    FW_ASSERT(portNum < this->getNum_to_fileDownlinkBufferSendIn(),static_cast<AssertArg>(portNum));
    this->m_to_fileDownlinkBufferSendIn[portNum].addCallPort(fileDownlinkBufferSendIn);
  }


  // ----------------------------------------------------------------------
  // Invocation functions for to ports
  // ----------------------------------------------------------------------

  void ZmqGroundIfTesterBase ::
    invoke_to_downlinkPort(
        const NATIVE_INT_TYPE portNum,
        Fw::ComBuffer &data,
        U32 context
    )
  {
    FW_ASSERT(portNum < this->getNum_to_downlinkPort(),static_cast<AssertArg>(portNum));
    FW_ASSERT(portNum < this->getNum_to_downlinkPort(),static_cast<AssertArg>(portNum));
    this->m_to_downlinkPort[portNum].invoke(
        data, context
    );
  }

  void ZmqGroundIfTesterBase ::
    invoke_to_fileDownlinkBufferSendIn(
        const NATIVE_INT_TYPE portNum,
        Fw::Buffer fwBuffer
    )
  {
    FW_ASSERT(portNum < this->getNum_to_fileDownlinkBufferSendIn(),static_cast<AssertArg>(portNum));
    FW_ASSERT(portNum < this->getNum_to_fileDownlinkBufferSendIn(),static_cast<AssertArg>(portNum));
    this->m_to_fileDownlinkBufferSendIn[portNum].invoke(
        fwBuffer
    );
  }

  // ----------------------------------------------------------------------
  // Connection status for to ports
  // ----------------------------------------------------------------------

  bool ZmqGroundIfTesterBase ::
    isConnected_to_downlinkPort(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_to_downlinkPort(), static_cast<AssertArg>(portNum));
    return this->m_to_downlinkPort[portNum].isConnected();
  }

  bool ZmqGroundIfTesterBase ::
    isConnected_to_fileDownlinkBufferSendIn(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_to_fileDownlinkBufferSendIn(), static_cast<AssertArg>(portNum));
    return this->m_to_fileDownlinkBufferSendIn[portNum].isConnected();
  }

  // ----------------------------------------------------------------------
  // Getters for from ports
  // ----------------------------------------------------------------------
 
  Fw::InputBufferSendPort *ZmqGroundIfTesterBase ::
    get_from_fileUplinkBufferSendOut(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_fileUplinkBufferSendOut(),static_cast<AssertArg>(portNum));
    return &this->m_from_fileUplinkBufferSendOut[portNum];
  }

  Fw::InputLogPort *ZmqGroundIfTesterBase ::
    get_from_Log(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_Log(),static_cast<AssertArg>(portNum));
    return &this->m_from_Log[portNum];
  }

#if FW_ENABLE_TEXT_LOGGING == 1
  Fw::InputLogTextPort *ZmqGroundIfTesterBase ::
    get_from_LogText(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_LogText(),static_cast<AssertArg>(portNum));
    return &this->m_from_LogText[portNum];
  }
#endif

  Fw::InputTimePort *ZmqGroundIfTesterBase ::
    get_from_Time(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_Time(),static_cast<AssertArg>(portNum));
    return &this->m_from_Time[portNum];
  }

  Fw::InputComPort *ZmqGroundIfTesterBase ::
    get_from_uplinkPort(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_uplinkPort(),static_cast<AssertArg>(portNum));
    return &this->m_from_uplinkPort[portNum];
  }

  Fw::InputBufferSendPort *ZmqGroundIfTesterBase ::
    get_from_fileDownlinkBufferSendOut(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_fileDownlinkBufferSendOut(),static_cast<AssertArg>(portNum));
    return &this->m_from_fileDownlinkBufferSendOut[portNum];
  }

  Fw::InputBufferGetPort *ZmqGroundIfTesterBase ::
    get_from_fileUplinkBufferGet(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_fileUplinkBufferGet(),static_cast<AssertArg>(portNum));
    return &this->m_from_fileUplinkBufferGet[portNum];
  }

  // ----------------------------------------------------------------------
  // Static functions for from ports
  // ----------------------------------------------------------------------

  void ZmqGroundIfTesterBase ::
    from_fileUplinkBufferSendOut_static(
        Fw::PassiveComponentBase *const callComp,
        const NATIVE_INT_TYPE portNum,
        Fw::Buffer fwBuffer
    )
  {
    FW_ASSERT(callComp);
    ZmqGroundIfTesterBase* _testerBase = 
      static_cast<ZmqGroundIfTesterBase*>(callComp);
    _testerBase->from_fileUplinkBufferSendOut_handlerBase(
        portNum,
        fwBuffer
    );
  }

  void ZmqGroundIfTesterBase ::
    from_uplinkPort_static(
        Fw::PassiveComponentBase *const callComp,
        const NATIVE_INT_TYPE portNum,
        Fw::ComBuffer &data,
        U32 context
    )
  {
    FW_ASSERT(callComp);
    ZmqGroundIfTesterBase* _testerBase = 
      static_cast<ZmqGroundIfTesterBase*>(callComp);
    _testerBase->from_uplinkPort_handlerBase(
        portNum,
        data, context
    );
  }

  void ZmqGroundIfTesterBase ::
    from_fileDownlinkBufferSendOut_static(
        Fw::PassiveComponentBase *const callComp,
        const NATIVE_INT_TYPE portNum,
        Fw::Buffer fwBuffer
    )
  {
    FW_ASSERT(callComp);
    ZmqGroundIfTesterBase* _testerBase = 
      static_cast<ZmqGroundIfTesterBase*>(callComp);
    _testerBase->from_fileDownlinkBufferSendOut_handlerBase(
        portNum,
        fwBuffer
    );
  }

  Fw::Buffer ZmqGroundIfTesterBase ::
    from_fileUplinkBufferGet_static(
        Fw::PassiveComponentBase *const callComp,
        const NATIVE_INT_TYPE portNum,
        U32 size
    )
  {
    FW_ASSERT(callComp);
    ZmqGroundIfTesterBase* _testerBase = 
      static_cast<ZmqGroundIfTesterBase*>(callComp);
    return _testerBase->from_fileUplinkBufferGet_handlerBase(
        portNum,
        size
    );
  }

  // ----------------------------------------------------------------------
  // Histories for typed from ports
  // ----------------------------------------------------------------------

  void ZmqGroundIfTesterBase ::
    clearFromPortHistory(void)
  {
    this->fromPortHistorySize = 0;
    this->fromPortHistory_fileUplinkBufferSendOut->clear();
    this->fromPortHistory_uplinkPort->clear();
    this->fromPortHistory_fileDownlinkBufferSendOut->clear();
    this->fromPortHistory_fileUplinkBufferGet->clear();
  }

  // ---------------------------------------------------------------------- 
  // From port: fileUplinkBufferSendOut
  // ---------------------------------------------------------------------- 

  void ZmqGroundIfTesterBase ::
    pushFromPortEntry_fileUplinkBufferSendOut(
        Fw::Buffer fwBuffer
    )
  {
    FromPortEntry_fileUplinkBufferSendOut _e = {
      fwBuffer
    };
    this->fromPortHistory_fileUplinkBufferSendOut->push_back(_e);
    ++this->fromPortHistorySize;
  }

  // ---------------------------------------------------------------------- 
  // From port: uplinkPort
  // ---------------------------------------------------------------------- 

  void ZmqGroundIfTesterBase ::
    pushFromPortEntry_uplinkPort(
        Fw::ComBuffer &data,
        U32 context
    )
  {
    FromPortEntry_uplinkPort _e = {
      data, context
    };
    this->fromPortHistory_uplinkPort->push_back(_e);
    ++this->fromPortHistorySize;
  }

  // ---------------------------------------------------------------------- 
  // From port: fileDownlinkBufferSendOut
  // ---------------------------------------------------------------------- 

  void ZmqGroundIfTesterBase ::
    pushFromPortEntry_fileDownlinkBufferSendOut(
        Fw::Buffer fwBuffer
    )
  {
    FromPortEntry_fileDownlinkBufferSendOut _e = {
      fwBuffer
    };
    this->fromPortHistory_fileDownlinkBufferSendOut->push_back(_e);
    ++this->fromPortHistorySize;
  }

  // ---------------------------------------------------------------------- 
  // From port: fileUplinkBufferGet
  // ---------------------------------------------------------------------- 

  void ZmqGroundIfTesterBase ::
    pushFromPortEntry_fileUplinkBufferGet(
        U32 size
    )
  {
    FromPortEntry_fileUplinkBufferGet _e = {
      size
    };
    this->fromPortHistory_fileUplinkBufferGet->push_back(_e);
    ++this->fromPortHistorySize;
  }

  // ----------------------------------------------------------------------
  // Handler base functions for from ports
  // ----------------------------------------------------------------------

  void ZmqGroundIfTesterBase ::
    from_fileUplinkBufferSendOut_handlerBase(
        const NATIVE_INT_TYPE portNum,
        Fw::Buffer fwBuffer
    )
  {
    FW_ASSERT(portNum < this->getNum_from_fileUplinkBufferSendOut(),static_cast<AssertArg>(portNum));
    this->from_fileUplinkBufferSendOut_handler(
        portNum,
        fwBuffer
    );
  }

  void ZmqGroundIfTesterBase ::
    from_uplinkPort_handlerBase(
        const NATIVE_INT_TYPE portNum,
        Fw::ComBuffer &data,
        U32 context
    )
  {
    FW_ASSERT(portNum < this->getNum_from_uplinkPort(),static_cast<AssertArg>(portNum));
    this->from_uplinkPort_handler(
        portNum,
        data, context
    );
  }

  void ZmqGroundIfTesterBase ::
    from_fileDownlinkBufferSendOut_handlerBase(
        const NATIVE_INT_TYPE portNum,
        Fw::Buffer fwBuffer
    )
  {
    FW_ASSERT(portNum < this->getNum_from_fileDownlinkBufferSendOut(),static_cast<AssertArg>(portNum));
    this->from_fileDownlinkBufferSendOut_handler(
        portNum,
        fwBuffer
    );
  }

  Fw::Buffer ZmqGroundIfTesterBase ::
    from_fileUplinkBufferGet_handlerBase(
        const NATIVE_INT_TYPE portNum,
        U32 size
    )
  {
    FW_ASSERT(portNum < this->getNum_from_fileUplinkBufferGet(),static_cast<AssertArg>(portNum));
    return this->from_fileUplinkBufferGet_handler(
        portNum,
        size
    );
  }

  // ----------------------------------------------------------------------
  // History 
  // ----------------------------------------------------------------------

  void ZmqGroundIfTesterBase ::
    clearHistory()
  {
    this->clearFromPortHistory();
  }

} // end namespace Zmq

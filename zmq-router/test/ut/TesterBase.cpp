// ======================================================================
// \title  ZmqRouter/test/ut/TesterBase.cpp
// \author Auto-generated
// \brief  cpp file for ZmqRouter component test harness base class
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

  ZmqRouterTesterBase ::
    ZmqRouterTesterBase(
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
    // Initialize telemetry histories
    this->tlmHistory_ZR_BytesSent = 
      new History<TlmEntry_ZR_BytesSent>(maxHistorySize);
    this->tlmHistory_ZR_BytesReceived = 
      new History<TlmEntry_ZR_BytesReceived>(maxHistorySize);
    // Initialize event histories
#if FW_ENABLE_TEXT_LOGGING
    this->textLogHistory = new History<TextLogEntry>(maxHistorySize);
#endif
    // Clear history
    this->clearHistory();
  }

  ZmqRouterTesterBase ::
    ~ZmqRouterTesterBase(void) 
  {
    // Destroy telemetry histories
    delete this->tlmHistory_ZR_BytesSent;
    delete this->tlmHistory_ZR_BytesReceived;
    // Destroy event histories
#if FW_ENABLE_TEXT_LOGGING
    delete this->textLogHistory;
#endif
  }

  void ZmqRouterTesterBase ::
    init(
        const NATIVE_INT_TYPE instance
    )
  {

    // Initialize base class

		Fw::PassiveComponentBase::init(instance);

    // Attach input port PortsOut

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_PortsOut();
        ++_port
    ) {

      this->m_from_PortsOut[_port].init();
      this->m_from_PortsOut[_port].addCallComp(
          this,
          from_PortsOut_static
      );
      this->m_from_PortsOut[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_PortsOut[%d]",
          this->m_objName,
          _port
      );
      this->m_from_PortsOut[_port].setObjName(_portName);
#endif

    }

    // Attach input port Tlm

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_from_Tlm();
        ++_port
    ) {

      this->m_from_Tlm[_port].init();
      this->m_from_Tlm[_port].addCallComp(
          this,
          from_Tlm_static
      );
      this->m_from_Tlm[_port].setPortNum(_port);

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      (void) snprintf(
          _portName,
          sizeof(_portName),
          "%s_from_Tlm[%d]",
          this->m_objName,
          _port
      );
      this->m_from_Tlm[_port].setObjName(_portName);
#endif

    }

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

    // Initialize output port Sched

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_to_Sched();
        ++_port
    ) {
      this->m_to_Sched[_port].init();

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      snprintf(
          _portName,
          sizeof(_portName),
          "%s_to_Sched[%d]",
          this->m_objName,
          _port
      );
      this->m_to_Sched[_port].setObjName(_portName);
#endif

    }

    // Initialize output port PortsIn

    for (
        NATIVE_INT_TYPE _port = 0;
        _port < this->getNum_to_PortsIn();
        ++_port
    ) {
      this->m_to_PortsIn[_port].init();

#if FW_OBJECT_NAMES == 1
      char _portName[80];
      snprintf(
          _portName,
          sizeof(_portName),
          "%s_to_PortsIn[%d]",
          this->m_objName,
          _port
      );
      this->m_to_PortsIn[_port].setObjName(_portName);
#endif

    }

  }

  // ----------------------------------------------------------------------
  // Getters for port counts
  // ----------------------------------------------------------------------

  NATIVE_INT_TYPE ZmqRouterTesterBase ::
    getNum_to_Sched(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_to_Sched);
  }

  NATIVE_INT_TYPE ZmqRouterTesterBase ::
    getNum_to_PortsIn(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_to_PortsIn);
  }

  NATIVE_INT_TYPE ZmqRouterTesterBase ::
    getNum_from_PortsOut(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_PortsOut);
  }

  NATIVE_INT_TYPE ZmqRouterTesterBase ::
    getNum_from_Tlm(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_Tlm);
  }

  NATIVE_INT_TYPE ZmqRouterTesterBase ::
    getNum_from_Time(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_Time);
  }

  NATIVE_INT_TYPE ZmqRouterTesterBase ::
    getNum_from_Log(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_Log);
  }

#if FW_ENABLE_TEXT_LOGGING == 1
  NATIVE_INT_TYPE ZmqRouterTesterBase ::
    getNum_from_LogText(void) const
  {
    return (NATIVE_INT_TYPE) FW_NUM_ARRAY_ELEMENTS(this->m_from_LogText);
  }
#endif

  // ----------------------------------------------------------------------
  // Connectors for to ports 
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    connect_to_Sched(
        const NATIVE_INT_TYPE portNum,
        Svc::InputSchedPort *const Sched
    ) 
  {
    FW_ASSERT(portNum < this->getNum_to_Sched(),static_cast<AssertArg>(portNum));
    this->m_to_Sched[portNum].addCallPort(Sched);
  }

  void ZmqRouterTesterBase ::
    connect_to_PortsIn(
        const NATIVE_INT_TYPE portNum,
        Fw::InputSerializePort *const PortsIn
    ) 
  {
    FW_ASSERT(portNum < this->getNum_to_PortsIn(),static_cast<AssertArg>(portNum));
    this->m_to_PortsIn[portNum].registerSerialPort(PortsIn);
  }


  // ----------------------------------------------------------------------
  // Invocation functions for to ports
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    invoke_to_Sched(
        const NATIVE_INT_TYPE portNum,
        NATIVE_UINT_TYPE context
    )
  {
    FW_ASSERT(portNum < this->getNum_to_Sched(),static_cast<AssertArg>(portNum));
    FW_ASSERT(portNum < this->getNum_to_Sched(),static_cast<AssertArg>(portNum));
    this->m_to_Sched[portNum].invoke(
        context
    );
  }

  void ZmqRouterTesterBase ::
    invoke_to_PortsIn(
      NATIVE_INT_TYPE portNum, //!< The port number
      Fw::SerializeBufferBase& Buffer
    )
  {
    FW_ASSERT(portNum < this->getNum_to_PortsIn(),static_cast<AssertArg>(portNum));
    this->m_to_PortsIn[portNum].invokeSerial(Buffer);
  }

  // ----------------------------------------------------------------------
  // Connection status for to ports
  // ----------------------------------------------------------------------

  bool ZmqRouterTesterBase ::
    isConnected_to_Sched(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_to_Sched(), static_cast<AssertArg>(portNum));
    return this->m_to_Sched[portNum].isConnected();
  }

  bool ZmqRouterTesterBase ::
    isConnected_to_PortsIn(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_to_PortsIn(), static_cast<AssertArg>(portNum));
    return this->m_to_PortsIn[portNum].isConnected();
  }

  // ----------------------------------------------------------------------
  // Getters for from ports
  // ----------------------------------------------------------------------
 
  Fw::InputSerializePort *ZmqRouterTesterBase ::
    get_from_PortsOut(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_PortsOut(),static_cast<AssertArg>(portNum));
    return &this->m_from_PortsOut[portNum];
  }

  Fw::InputTlmPort *ZmqRouterTesterBase ::
    get_from_Tlm(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_Tlm(),static_cast<AssertArg>(portNum));
    return &this->m_from_Tlm[portNum];
  }

  Fw::InputTimePort *ZmqRouterTesterBase ::
    get_from_Time(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_Time(),static_cast<AssertArg>(portNum));
    return &this->m_from_Time[portNum];
  }

  Fw::InputLogPort *ZmqRouterTesterBase ::
    get_from_Log(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_Log(),static_cast<AssertArg>(portNum));
    return &this->m_from_Log[portNum];
  }

#if FW_ENABLE_TEXT_LOGGING == 1
  Fw::InputLogTextPort *ZmqRouterTesterBase ::
    get_from_LogText(const NATIVE_INT_TYPE portNum)
  {
    FW_ASSERT(portNum < this->getNum_from_LogText(),static_cast<AssertArg>(portNum));
    return &this->m_from_LogText[portNum];
  }
#endif

  // ----------------------------------------------------------------------
  // Static functions for from ports
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    from_PortsOut_static(
      Fw::PassiveComponentBase *const callComp, //!< The component instance
      const NATIVE_INT_TYPE portNum, //!< The port number
      Fw::SerializeBufferBase& Buffer //!< serialized data buffer
    )
  {
    FW_ASSERT(callComp);
    ZmqRouterTesterBase* _testerBase = 
      static_cast<ZmqRouterTesterBase*>(callComp);

    _testerBase->from_PortsOut_handlerBase(
        portNum,
        Buffer
    );
  }  

  void ZmqRouterTesterBase ::
    from_PortsOut_handlerBase(
        NATIVE_INT_TYPE portNum, /*!< The port number*/
        Fw::SerializeBufferBase &Buffer /*!< The serialization buffer*/
    )
  {
    FW_ASSERT(portNum < this->getNum_from_PortsOut(),static_cast<AssertArg>(portNum));
    this->from_PortsOut_handler(
        portNum,
        Buffer
    );
  } 
   
  void ZmqRouterTesterBase ::
    from_Tlm_static(
        Fw::PassiveComponentBase *const component,
        NATIVE_INT_TYPE portNum,
        FwChanIdType id,
        Fw::Time &timeTag,
        Fw::TlmBuffer &val
    )
  {
    ZmqRouterTesterBase* _testerBase =
      static_cast<ZmqRouterTesterBase*>(component);
    _testerBase->dispatchTlm(id, timeTag, val);
  }

  void ZmqRouterTesterBase ::
    from_Log_static(
        Fw::PassiveComponentBase *const component,
        const NATIVE_INT_TYPE portNum,
        FwEventIdType id,
        Fw::Time &timeTag,
        Fw::LogSeverity severity,
        Fw::LogBuffer &args
    )
  {
    ZmqRouterTesterBase* _testerBase =
      static_cast<ZmqRouterTesterBase*>(component);
    _testerBase->dispatchEvents(id, timeTag, severity, args);
  }

#if FW_ENABLE_TEXT_LOGGING == 1
  void ZmqRouterTesterBase ::
    from_LogText_static(
        Fw::PassiveComponentBase *const component,
        const NATIVE_INT_TYPE portNum,
        FwEventIdType id,
        Fw::Time &timeTag,
        Fw::TextLogSeverity severity,
        Fw::TextLogString &text
    )
  {
    ZmqRouterTesterBase* _testerBase =
      static_cast<ZmqRouterTesterBase*>(component);
    _testerBase->textLogIn(id,timeTag,severity,text);
  }
#endif

  void ZmqRouterTesterBase ::
    from_Time_static(
        Fw::PassiveComponentBase *const component,
        const NATIVE_INT_TYPE portNum,
        Fw::Time& time
    )
  {
    ZmqRouterTesterBase* _testerBase =
      static_cast<ZmqRouterTesterBase*>(component);
    time = _testerBase->m_testTime;
  }

  // ----------------------------------------------------------------------
  // History 
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    clearHistory()
  {
    this->clearTlm();
    this->textLogHistory->clear();
    this->clearEvents();
  }

  // ----------------------------------------------------------------------
  // Time
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    setTestTime(const Fw::Time& time)
  {
    this->m_testTime = time;
  }

  // ----------------------------------------------------------------------
  // Telemetry dispatch
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    dispatchTlm(
        const FwChanIdType id,
        const Fw::Time &timeTag,
        Fw::TlmBuffer &val
    )
  {

    val.resetDeser();

    const U32 idBase = this->getIdBase();
    FW_ASSERT(id >= idBase, id, idBase);

    switch (id - idBase) {

      case ZmqRouterComponentBase::CHANNELID_ZR_BYTESSENT:
      {
        U32 arg;
        const Fw::SerializeStatus _status = val.deserialize(arg);
        if (_status != Fw::FW_SERIALIZE_OK) {
          printf("Error deserializing ZR_BytesSent: %d\n", _status);
          return;
        }
        this->tlmInput_ZR_BytesSent(timeTag, arg);
        break;
      }

      case ZmqRouterComponentBase::CHANNELID_ZR_BYTESRECEIVED:
      {
        U32 arg;
        const Fw::SerializeStatus _status = val.deserialize(arg);
        if (_status != Fw::FW_SERIALIZE_OK) {
          printf("Error deserializing ZR_BytesReceived: %d\n", _status);
          return;
        }
        this->tlmInput_ZR_BytesReceived(timeTag, arg);
        break;
      }

      default: {
        FW_ASSERT(0, id);
        break;
      }

    }

  }

  void ZmqRouterTesterBase ::
    clearTlm(void)
  {
    this->tlmSize = 0;
    this->tlmHistory_ZR_BytesSent->clear();
    this->tlmHistory_ZR_BytesReceived->clear();
  }

  // ---------------------------------------------------------------------- 
  // Channel: ZR_BytesSent
  // ---------------------------------------------------------------------- 

  void ZmqRouterTesterBase ::
    tlmInput_ZR_BytesSent(
        const Fw::Time& timeTag,
        const U32& val
    )
  {
    TlmEntry_ZR_BytesSent e = { timeTag, val };
    this->tlmHistory_ZR_BytesSent->push_back(e);
    ++this->tlmSize;
  }

  // ---------------------------------------------------------------------- 
  // Channel: ZR_BytesReceived
  // ---------------------------------------------------------------------- 

  void ZmqRouterTesterBase ::
    tlmInput_ZR_BytesReceived(
        const Fw::Time& timeTag,
        const U32& val
    )
  {
    TlmEntry_ZR_BytesReceived e = { timeTag, val };
    this->tlmHistory_ZR_BytesReceived->push_back(e);
    ++this->tlmSize;
  }

  // ----------------------------------------------------------------------
  // Event dispatch
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    dispatchEvents(
        const FwEventIdType id,
        Fw::Time &timeTag,
        const Fw::LogSeverity severity,
        Fw::LogBuffer &args
    )
  {

    args.resetDeser();

    const U32 idBase = this->getIdBase();
    FW_ASSERT(id >= idBase, id, idBase);
    switch (id - idBase) {

      case ZmqRouterComponentBase::EVENTID_ZR_SERVERCONNECTIONOPENED: 
      {

#if FW_AMPCS_COMPATIBLE
        // For AMPCS, decode zero arguments
        Fw::SerializeStatus _zero_status = Fw::FW_SERIALIZE_OK;
        U8 _noArgs;
        _zero_status = args.deserialize(_noArgs);
        FW_ASSERT(
            _zero_status == Fw::FW_SERIALIZE_OK,
            static_cast<AssertArg>(_zero_status)
        );
#endif    
        this->logIn_ACTIVITY_HI_ZR_ServerConnectionOpened();

        break;

      }

      default: {
        FW_ASSERT(0, id);
        break;
      }

    }

  }

  void ZmqRouterTesterBase ::
    clearEvents(void)
  {
    this->eventsSize = 0;
    this->eventsSize_ZR_ServerConnectionOpened = 0;
  }

#if FW_ENABLE_TEXT_LOGGING

  // ----------------------------------------------------------------------
  // Text events 
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    textLogIn(
        const U32 id,
        Fw::Time &timeTag,
        const Fw::TextLogSeverity severity,
        const Fw::TextLogString &text
    )
  {
    TextLogEntry e = { id, timeTag, severity, text };
    textLogHistory->push_back(e);
  }

  void ZmqRouterTesterBase ::
    printTextLogHistoryEntry(
        const TextLogEntry& e,
        FILE* file
    )
  {
    const char *severityString = "UNKNOWN";
    switch (e.severity) {
      case Fw::LOG_FATAL:
        severityString = "FATAL";
        break;
      case Fw::LOG_WARNING_HI:
        severityString = "WARNING_HI";
        break;
      case Fw::LOG_WARNING_LO:
        severityString = "WARNING_LO";
        break;
      case Fw::LOG_COMMAND:
        severityString = "COMMAND";
        break;
      case Fw::LOG_ACTIVITY_HI:
        severityString = "ACTIVITY_HI";
        break;
      case Fw::LOG_ACTIVITY_LO:
        severityString = "ACTIVITY_LO";
        break;
      case Fw::LOG_DIAGNOSTIC:
       severityString = "DIAGNOSTIC";
        break;
      default:
        severityString = "SEVERITY ERROR";
        break;
    }

    fprintf(
        file,
        "EVENT: (%d) (%d:%d,%d) %s: %s\n",
        e.id,
        const_cast<TextLogEntry&>(e).timeTag.getTimeBase(),
        const_cast<TextLogEntry&>(e).timeTag.getSeconds(),
        const_cast<TextLogEntry&>(e).timeTag.getUSeconds(),
        severityString,
        e.text.toChar()
    );

  }

  void ZmqRouterTesterBase ::
    printTextLogHistory(FILE *file) 
  {
    for (U32 i = 0; i < this->textLogHistory->size(); ++i) {
      this->printTextLogHistoryEntry(
          this->textLogHistory->at(i), 
          file
      );
    }
  }

#endif

  // ----------------------------------------------------------------------
  // Event: ZR_ServerConnectionOpened 
  // ----------------------------------------------------------------------

  void ZmqRouterTesterBase ::
    logIn_ACTIVITY_HI_ZR_ServerConnectionOpened(
        void
    )
  {
    ++this->eventsSize_ZR_ServerConnectionOpened;
    ++this->eventsSize;
  }

} // end namespace Zmq

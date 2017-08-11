// ====================================================================== 
// \title  ZmqGroundIf.hpp
// \author dkooi
// \brief  cpp file for ZmqGroundIf test harness implementation class
//
// \copyright
// Copyright 2009-2015, by the California Institute of Technology.
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

#include "Tester.hpp"

#define INSTANCE 0
#define MAX_HISTORY_SIZE 10
#define QUEUE_DEPTH 10

namespace Zmq {

  // ----------------------------------------------------------------------
  // Construction and destruction 
  // ----------------------------------------------------------------------

  Tester ::
    Tester(void) : 
#if FW_OBJECT_NAMES == 1
      ZmqGroundIfGTestBase("Tester", MAX_HISTORY_SIZE),
      component("ZmqGroundIf")
#else
      ZmqGroundIfGTestBase(MAX_HISTORY_SIZE),
      component()
#endif
  {
    this->initComponents();
    this->connectPorts();
  }

  Tester ::
    ~Tester(void) 
  {
    
  }

  // ----------------------------------------------------------------------
  // Tests 
  // ----------------------------------------------------------------------

  void Tester ::
    toDo(void) 
  {
    // TODO
  }

  // ----------------------------------------------------------------------
  // Handlers for typed from ports
  // ----------------------------------------------------------------------

  void Tester ::
    from_fileUplinkBufferSendOut_handler(
        const NATIVE_INT_TYPE portNum,
        Fw::Buffer fwBuffer
    )
  {
    this->pushFromPortEntry_fileUplinkBufferSendOut(fwBuffer);
  }

  void Tester ::
    from_uplinkPort_handler(
        const NATIVE_INT_TYPE portNum,
        Fw::ComBuffer &data,
        U32 context
    )
  {
    this->pushFromPortEntry_uplinkPort(data, context);
  }

  void Tester ::
    from_fileDownlinkBufferSendOut_handler(
        const NATIVE_INT_TYPE portNum,
        Fw::Buffer fwBuffer
    )
  {
    this->pushFromPortEntry_fileDownlinkBufferSendOut(fwBuffer);
  }

  Fw::Buffer Tester ::
    from_fileUplinkBufferGet_handler(
        const NATIVE_INT_TYPE portNum,
        U32 size
    )
  {
    this->pushFromPortEntry_fileUplinkBufferGet(size);
    // TODO: Return a value
  }

  // ----------------------------------------------------------------------
  // Helper methods 
  // ----------------------------------------------------------------------

  void Tester ::
    connectPorts(void) 
  {

    // downlinkPort
    this->connect_to_downlinkPort(
        0,
        this->component.get_downlinkPort_InputPort(0)
    );

    // fileDownlinkBufferSendIn
    this->connect_to_fileDownlinkBufferSendIn(
        0,
        this->component.get_fileDownlinkBufferSendIn_InputPort(0)
    );

    // fileUplinkBufferSendOut
    this->component.set_fileUplinkBufferSendOut_OutputPort(
        0, 
        this->get_from_fileUplinkBufferSendOut(0)
    );

    // Log
    this->component.set_Log_OutputPort(
        0, 
        this->get_from_Log(0)
    );

    // LogText
    this->component.set_LogText_OutputPort(
        0, 
        this->get_from_LogText(0)
    );

    // Time
    this->component.set_Time_OutputPort(
        0, 
        this->get_from_Time(0)
    );

    // uplinkPort
    this->component.set_uplinkPort_OutputPort(
        0, 
        this->get_from_uplinkPort(0)
    );

    // fileDownlinkBufferSendOut
    this->component.set_fileDownlinkBufferSendOut_OutputPort(
        0, 
        this->get_from_fileDownlinkBufferSendOut(0)
    );

    // fileUplinkBufferGet
    this->component.set_fileUplinkBufferGet_OutputPort(
        0, 
        this->get_from_fileUplinkBufferGet(0)
    );

  }

  void Tester ::
    initComponents(void) 
  {
    this->init();
    this->component.init(
        QUEUE_DEPTH, INSTANCE
    );
  }

} // end namespace Zmq

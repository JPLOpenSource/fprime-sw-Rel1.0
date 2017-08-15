// ======================================================================
// \title  ZmqRadio/test/ut/GTestBase.cpp
// \author Auto-generated
// \brief  cpp file for ZmqRadio component Google Test harness base class
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

#include "GTestBase.hpp"

namespace Zmq {

  // ----------------------------------------------------------------------
  // Construction and destruction
  // ----------------------------------------------------------------------

  ZmqRadioGTestBase ::
    ZmqRadioGTestBase(
#if FW_OBJECT_NAMES == 1
        const char *const compName,
        const U32 maxHistorySize
#else
        const U32 maxHistorySize
#endif
    ) : 
        ZmqRadioTesterBase (
#if FW_OBJECT_NAMES == 1
            compName,
#endif
            maxHistorySize
        )
  {

  }

  ZmqRadioGTestBase ::
    ~ZmqRadioGTestBase(void)
  {

  }

  // ----------------------------------------------------------------------
  // Telemetry
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertTlm_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->tlmSize)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Total size of all telemetry histories\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->tlmSize << "\n";
  }

  // ----------------------------------------------------------------------
  // Channel: ZR_PacketsSent
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertTlm_ZR_PacketsSent_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(this->tlmHistory_ZR_PacketsSent->size(), size)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for telemetry channel ZR_PacketsSent\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->tlmHistory_ZR_PacketsSent->size() << "\n";
  }

  void ZmqRadioGTestBase ::
    assertTlm_ZR_PacketsSent(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 index,
        const U32& val
    )
    const
  {
    ASSERT_LT(index, this->tlmHistory_ZR_PacketsSent->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Index into history of telemetry channel ZR_PacketsSent\n"
      << "  Expected: Less than size of history (" 
      << this->tlmHistory_ZR_PacketsSent->size() << ")\n"
      << "  Actual:   " << index << "\n";
    const TlmEntry_ZR_PacketsSent& e =
      this->tlmHistory_ZR_PacketsSent->at(index);
    ASSERT_EQ(val, e.arg)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Value at index "
      << index
      << " on telmetry channel ZR_PacketsSent\n"
      << "  Expected: " << val << "\n"
      << "  Actual:   " << e.arg << "\n";
  }

  // ----------------------------------------------------------------------
  // Events
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertEvents_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventsSize)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Total size of all event histories\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventsSize << "\n";
  }

  // ----------------------------------------------------------------------
  // Event: ZR_PublishConnectionOpened
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertEvents_ZR_PublishConnectionOpened_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventsSize_ZR_PublishConnectionOpened)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for event ZR_PublishConnectionOpened\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventsSize_ZR_PublishConnectionOpened << "\n";
  }

  // ----------------------------------------------------------------------
  // Event: ZR_ContextError
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertEvents_ZR_ContextError_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventHistory_ZR_ContextError->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for event ZR_ContextError\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventHistory_ZR_ContextError->size() << "\n";
  }

  void ZmqRadioGTestBase ::
    assertEvents_ZR_ContextError(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 index,
        const char *const error
    ) const
  {
    ASSERT_GT(this->eventHistory_ZR_ContextError->size(), index)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Index into history of event ZR_ContextError\n"
      << "  Expected: Less than size of history (" 
      << this->eventHistory_ZR_ContextError->size() << ")\n"
      << "  Actual:   " << index << "\n";
    const EventEntry_ZR_ContextError& e =
      this->eventHistory_ZR_ContextError->at(index);
    ASSERT_STREQ(error, e.error.toChar())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Value of argument error at index "
      << index
      << " in history of event ZR_ContextError\n"
      << "  Expected: " << error << "\n"
      << "  Actual:   " << e.error.toChar() << "\n";
  }

  // ----------------------------------------------------------------------
  // Event: ZR_SocketError
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertEvents_ZR_SocketError_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventHistory_ZR_SocketError->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for event ZR_SocketError\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventHistory_ZR_SocketError->size() << "\n";
  }

  void ZmqRadioGTestBase ::
    assertEvents_ZR_SocketError(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 index,
        const char *const error
    ) const
  {
    ASSERT_GT(this->eventHistory_ZR_SocketError->size(), index)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Index into history of event ZR_SocketError\n"
      << "  Expected: Less than size of history (" 
      << this->eventHistory_ZR_SocketError->size() << ")\n"
      << "  Actual:   " << index << "\n";
    const EventEntry_ZR_SocketError& e =
      this->eventHistory_ZR_SocketError->at(index);
    ASSERT_STREQ(error, e.error.toChar())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Value of argument error at index "
      << index
      << " in history of event ZR_SocketError\n"
      << "  Expected: " << error << "\n"
      << "  Actual:   " << e.error.toChar() << "\n";
  }

  // ----------------------------------------------------------------------
  // Event: ZR_BindError
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertEvents_ZR_BindError_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventHistory_ZR_BindError->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for event ZR_BindError\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventHistory_ZR_BindError->size() << "\n";
  }

  void ZmqRadioGTestBase ::
    assertEvents_ZR_BindError(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 index,
        const char *const error
    ) const
  {
    ASSERT_GT(this->eventHistory_ZR_BindError->size(), index)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Index into history of event ZR_BindError\n"
      << "  Expected: Less than size of history (" 
      << this->eventHistory_ZR_BindError->size() << ")\n"
      << "  Actual:   " << index << "\n";
    const EventEntry_ZR_BindError& e =
      this->eventHistory_ZR_BindError->at(index);
    ASSERT_STREQ(error, e.error.toChar())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Value of argument error at index "
      << index
      << " in history of event ZR_BindError\n"
      << "  Expected: " << error << "\n"
      << "  Actual:   " << e.error.toChar() << "\n";
  }

  // ----------------------------------------------------------------------
  // Event: ZR_SendError
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertEvents_ZR_SendError_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventHistory_ZR_SendError->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for event ZR_SendError\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventHistory_ZR_SendError->size() << "\n";
  }

  void ZmqRadioGTestBase ::
    assertEvents_ZR_SendError(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 index,
        const char *const error
    ) const
  {
    ASSERT_GT(this->eventHistory_ZR_SendError->size(), index)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Index into history of event ZR_SendError\n"
      << "  Expected: Less than size of history (" 
      << this->eventHistory_ZR_SendError->size() << ")\n"
      << "  Actual:   " << index << "\n";
    const EventEntry_ZR_SendError& e =
      this->eventHistory_ZR_SendError->at(index);
    ASSERT_STREQ(error, e.error.toChar())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Value of argument error at index "
      << index
      << " in history of event ZR_SendError\n"
      << "  Expected: " << error << "\n"
      << "  Actual:   " << e.error.toChar() << "\n";
  }

  // ----------------------------------------------------------------------
  // From ports
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assertFromPortHistory_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->fromPortHistorySize)
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Total size of all from port histories\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->fromPortHistorySize << "\n";
  }

  // ----------------------------------------------------------------------
  // From port: fileUplinkBufferSendOut
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assert_from_fileUplinkBufferSendOut_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->fromPortHistory_fileUplinkBufferSendOut->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for from_fileUplinkBufferSendOut\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->fromPortHistory_fileUplinkBufferSendOut->size() << "\n";
  }

  // ----------------------------------------------------------------------
  // From port: uplinkPort
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assert_from_uplinkPort_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->fromPortHistory_uplinkPort->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for from_uplinkPort\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->fromPortHistory_uplinkPort->size() << "\n";
  }

  // ----------------------------------------------------------------------
  // From port: fileDownlinkBufferSendOut
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assert_from_fileDownlinkBufferSendOut_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->fromPortHistory_fileDownlinkBufferSendOut->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for from_fileDownlinkBufferSendOut\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->fromPortHistory_fileDownlinkBufferSendOut->size() << "\n";
  }

  // ----------------------------------------------------------------------
  // From port: fileUplinkBufferGet
  // ----------------------------------------------------------------------

  void ZmqRadioGTestBase ::
    assert_from_fileUplinkBufferGet_size(
        const char *const __callSiteFileName,
        const U32 __callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->fromPortHistory_fileUplinkBufferGet->size())
      << "\n"
      << "  File:     " << __callSiteFileName << "\n"
      << "  Line:     " << __callSiteLineNumber << "\n"
      << "  Value:    Size of history for from_fileUplinkBufferGet\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->fromPortHistory_fileUplinkBufferGet->size() << "\n";
  }

} // end namespace Zmq

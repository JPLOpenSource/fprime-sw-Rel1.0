// ======================================================================
// \title  ZmqRouter/test/ut/GTestBase.cpp
// \author Auto-generated
// \brief  cpp file for ZmqRouter component Google Test harness base class
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

  ZmqRouterGTestBase ::
    ZmqRouterGTestBase(
#if FW_OBJECT_NAMES == 1
        const char *const compName,
        const U32 maxHistorySize
#else
        const U32 maxHistorySize
#endif
    ) : 
        ZmqRouterTesterBase (
#if FW_OBJECT_NAMES == 1
            compName,
#endif
            maxHistorySize
        )
  {

  }

  ZmqRouterGTestBase ::
    ~ZmqRouterGTestBase(void)
  {

  }

  // ----------------------------------------------------------------------
  // Telemetry
  // ----------------------------------------------------------------------

  void ZmqRouterGTestBase ::
    assertTlm_size(
        const char *const __ISF_callSiteFileName,
        const U32 __ISF_callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->tlmSize)
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Total size of all telemetry histories\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->tlmSize << "\n";
  }

  // ----------------------------------------------------------------------
  // Channel: ZR_BytesSent
  // ----------------------------------------------------------------------

  void ZmqRouterGTestBase ::
    assertTlm_ZR_BytesSent_size(
        const char *const __ISF_callSiteFileName,
        const U32 __ISF_callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(this->tlmHistory_ZR_BytesSent->size(), size)
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Size of history for telemetry channel ZR_BytesSent\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->tlmHistory_ZR_BytesSent->size() << "\n";
  }

  void ZmqRouterGTestBase ::
    assertTlm_ZR_BytesSent(
        const char *const __ISF_callSiteFileName,
        const U32 __ISF_callSiteLineNumber,
        const U32 index,
        const U32& val
    )
    const
  {
    ASSERT_LT(index, this->tlmHistory_ZR_BytesSent->size())
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Index into history of telemetry channel ZR_BytesSent\n"
      << "  Expected: Less than size of history (" 
      << this->tlmHistory_ZR_BytesSent->size() << ")\n"
      << "  Actual:   " << index << "\n";
    const TlmEntry_ZR_BytesSent& e =
      this->tlmHistory_ZR_BytesSent->at(index);
    ASSERT_EQ(val, e.arg)
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Value at index "
      << index
      << " on telmetry channel ZR_BytesSent\n"
      << "  Expected: " << val << "\n"
      << "  Actual:   " << e.arg << "\n";
  }

  // ----------------------------------------------------------------------
  // Channel: ZR_BytesReceived
  // ----------------------------------------------------------------------

  void ZmqRouterGTestBase ::
    assertTlm_ZR_BytesReceived_size(
        const char *const __ISF_callSiteFileName,
        const U32 __ISF_callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(this->tlmHistory_ZR_BytesReceived->size(), size)
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Size of history for telemetry channel ZR_BytesReceived\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->tlmHistory_ZR_BytesReceived->size() << "\n";
  }

  void ZmqRouterGTestBase ::
    assertTlm_ZR_BytesReceived(
        const char *const __ISF_callSiteFileName,
        const U32 __ISF_callSiteLineNumber,
        const U32 index,
        const U32& val
    )
    const
  {
    ASSERT_LT(index, this->tlmHistory_ZR_BytesReceived->size())
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Index into history of telemetry channel ZR_BytesReceived\n"
      << "  Expected: Less than size of history (" 
      << this->tlmHistory_ZR_BytesReceived->size() << ")\n"
      << "  Actual:   " << index << "\n";
    const TlmEntry_ZR_BytesReceived& e =
      this->tlmHistory_ZR_BytesReceived->at(index);
    ASSERT_EQ(val, e.arg)
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Value at index "
      << index
      << " on telmetry channel ZR_BytesReceived\n"
      << "  Expected: " << val << "\n"
      << "  Actual:   " << e.arg << "\n";
  }

  // ----------------------------------------------------------------------
  // Events
  // ----------------------------------------------------------------------

  void ZmqRouterGTestBase ::
    assertEvents_size(
        const char *const __ISF_callSiteFileName,
        const U32 __ISF_callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventsSize)
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Total size of all event histories\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventsSize << "\n";
  }

  // ----------------------------------------------------------------------
  // Event: ZR_ServerConnectionOpened
  // ----------------------------------------------------------------------

  void ZmqRouterGTestBase ::
    assertEvents_ZR_ServerConnectionOpened_size(
        const char *const __ISF_callSiteFileName,
        const U32 __ISF_callSiteLineNumber,
        const U32 size
    ) const
  {
    ASSERT_EQ(size, this->eventsSize_ZR_ServerConnectionOpened)
      << "\n"
      << "  File:     " << __ISF_callSiteFileName << "\n"
      << "  Line:     " << __ISF_callSiteLineNumber << "\n"
      << "  Value:    Size of history for event ZR_ServerConnectionOpened\n"
      << "  Expected: " << size << "\n"
      << "  Actual:   " << this->eventsSize_ZR_ServerConnectionOpened << "\n";
  }

} // end namespace Zmq

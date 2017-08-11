// ======================================================================
// \title  ZmqGroundIf/test/ut/GTestBase.cpp
// \author Auto-generated
// \brief  cpp file for ZmqGroundIf component Google Test harness base class
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

  ZmqGroundIfGTestBase ::
    ZmqGroundIfGTestBase(
#if FW_OBJECT_NAMES == 1
        const char *const compName,
        const U32 maxHistorySize
#else
        const U32 maxHistorySize
#endif
    ) : 
        ZmqGroundIfTesterBase (
#if FW_OBJECT_NAMES == 1
            compName,
#endif
            maxHistorySize
        )
  {

  }

  ZmqGroundIfGTestBase ::
    ~ZmqGroundIfGTestBase(void)
  {

  }

  // ----------------------------------------------------------------------
  // From ports
  // ----------------------------------------------------------------------

  void ZmqGroundIfGTestBase ::
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

  void ZmqGroundIfGTestBase ::
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

  void ZmqGroundIfGTestBase ::
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

  void ZmqGroundIfGTestBase ::
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

  void ZmqGroundIfGTestBase ::
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

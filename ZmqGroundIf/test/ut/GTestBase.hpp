// ======================================================================
// \title  ZmqGroundIf/test/ut/GTestBase.hpp
// \author Auto-generated
// \brief  hpp file for ZmqGroundIf component Google Test harness base class
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

#ifndef ZmqGroundIf_GTEST_BASE_HPP
#define ZmqGroundIf_GTEST_BASE_HPP

#include "TesterBase.hpp"
#include "gtest/gtest.h"

// ----------------------------------------------------------------------
// Macros for typed user from port history assertions
// ----------------------------------------------------------------------

#define ASSERT_FROM_PORT_HISTORY_SIZE(size) \
  this->assertFromPortHistory_size(__FILE__, __LINE__, size)

#define ASSERT_from_fileUplinkBufferSendOut_SIZE(size) \
  this->assert_from_fileUplinkBufferSendOut_size(__FILE__, __LINE__, size)

#define ASSERT_from_fileUplinkBufferSendOut(index, _fwBuffer) \
  { \
    ASSERT_GT(this->fromPortHistory_fileUplinkBufferSendOut->size(), static_cast<U32>(index)) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Index into history of from_fileUplinkBufferSendOut\n" \
    << "  Expected: Less than size of history (" \
    << this->fromPortHistory_fileUplinkBufferSendOut->size() << ")\n" \
    << "  Actual:   " << index << "\n"; \
    const FromPortEntry_fileUplinkBufferSendOut& _e = \
      this->fromPortHistory_fileUplinkBufferSendOut->at(index); \
    ASSERT_EQ(_fwBuffer, _e.fwBuffer) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Value of argument fwBuffer at index " \
    << index \
    << " in history of from_fileUplinkBufferSendOut\n" \
    << "  Expected: " << _fwBuffer << "\n" \
    << "  Actual:   " << _e.fwBuffer << "\n"; \
  }

#define ASSERT_from_uplinkPort_SIZE(size) \
  this->assert_from_uplinkPort_size(__FILE__, __LINE__, size)

#define ASSERT_from_uplinkPort(index, _data, _context) \
  { \
    ASSERT_GT(this->fromPortHistory_uplinkPort->size(), static_cast<U32>(index)) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Index into history of from_uplinkPort\n" \
    << "  Expected: Less than size of history (" \
    << this->fromPortHistory_uplinkPort->size() << ")\n" \
    << "  Actual:   " << index << "\n"; \
    const FromPortEntry_uplinkPort& _e = \
      this->fromPortHistory_uplinkPort->at(index); \
    ASSERT_EQ(_data, _e.data) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Value of argument data at index " \
    << index \
    << " in history of from_uplinkPort\n" \
    << "  Expected: " << _data << "\n" \
    << "  Actual:   " << _e.data << "\n"; \
    ASSERT_EQ(_context, _e.context) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Value of argument context at index " \
    << index \
    << " in history of from_uplinkPort\n" \
    << "  Expected: " << _context << "\n" \
    << "  Actual:   " << _e.context << "\n"; \
  }

#define ASSERT_from_fileDownlinkBufferSendOut_SIZE(size) \
  this->assert_from_fileDownlinkBufferSendOut_size(__FILE__, __LINE__, size)

#define ASSERT_from_fileDownlinkBufferSendOut(index, _fwBuffer) \
  { \
    ASSERT_GT(this->fromPortHistory_fileDownlinkBufferSendOut->size(), static_cast<U32>(index)) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Index into history of from_fileDownlinkBufferSendOut\n" \
    << "  Expected: Less than size of history (" \
    << this->fromPortHistory_fileDownlinkBufferSendOut->size() << ")\n" \
    << "  Actual:   " << index << "\n"; \
    const FromPortEntry_fileDownlinkBufferSendOut& _e = \
      this->fromPortHistory_fileDownlinkBufferSendOut->at(index); \
    ASSERT_EQ(_fwBuffer, _e.fwBuffer) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Value of argument fwBuffer at index " \
    << index \
    << " in history of from_fileDownlinkBufferSendOut\n" \
    << "  Expected: " << _fwBuffer << "\n" \
    << "  Actual:   " << _e.fwBuffer << "\n"; \
  }

#define ASSERT_from_fileUplinkBufferGet_SIZE(size) \
  this->assert_from_fileUplinkBufferGet_size(__FILE__, __LINE__, size)

#define ASSERT_from_fileUplinkBufferGet(index, _size) \
  { \
    ASSERT_GT(this->fromPortHistory_fileUplinkBufferGet->size(), static_cast<U32>(index)) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Index into history of from_fileUplinkBufferGet\n" \
    << "  Expected: Less than size of history (" \
    << this->fromPortHistory_fileUplinkBufferGet->size() << ")\n" \
    << "  Actual:   " << index << "\n"; \
    const FromPortEntry_fileUplinkBufferGet& _e = \
      this->fromPortHistory_fileUplinkBufferGet->at(index); \
    ASSERT_EQ(_size, _e.size) \
    << "\n" \
    << "  File:     " << __FILE__ << "\n" \
    << "  Line:     " << __LINE__ << "\n" \
    << "  Value:    Value of argument size at index " \
    << index \
    << " in history of from_fileUplinkBufferGet\n" \
    << "  Expected: " << _size << "\n" \
    << "  Actual:   " << _e.size << "\n"; \
  }

namespace Zmq {

  //! \class ZmqGroundIfGTestBase
  //! \brief Auto-generated base class for ZmqGroundIf component Google Test harness
  //!
  class ZmqGroundIfGTestBase :
    public ZmqGroundIfTesterBase
  {

    protected:

      // ----------------------------------------------------------------------
      // Construction and destruction
      // ----------------------------------------------------------------------

      //! Construct object ZmqGroundIfGTestBase
      //!
      ZmqGroundIfGTestBase(
#if FW_OBJECT_NAMES == 1
          const char *const compName, /*!< The component name*/
          const U32 maxHistorySize /*!< The maximum size of each history*/
#else
          const U32 maxHistorySize /*!< The maximum size of each history*/
#endif
      );

      //! Destroy object ZmqGroundIfGTestBase
      //!
      virtual ~ZmqGroundIfGTestBase(void);

    protected:

      // ----------------------------------------------------------------------
      // From ports 
      // ----------------------------------------------------------------------

      void assertFromPortHistory_size(
          const char *const __callSiteFileName, /*!< The name of the file containing the call site*/
          const U32 __callSiteLineNumber, /*!< The line number of the call site*/
          const U32 size /*!< The asserted size*/
      ) const;

    protected:

      // ----------------------------------------------------------------------
      // From port: fileUplinkBufferSendOut 
      // ----------------------------------------------------------------------

      void assert_from_fileUplinkBufferSendOut_size(
          const char *const __callSiteFileName, /*!< The name of the file containing the call site*/
          const U32 __callSiteLineNumber, /*!< The line number of the call site*/
          const U32 size /*!< The asserted size*/
      ) const;

    protected:

      // ----------------------------------------------------------------------
      // From port: uplinkPort 
      // ----------------------------------------------------------------------

      void assert_from_uplinkPort_size(
          const char *const __callSiteFileName, /*!< The name of the file containing the call site*/
          const U32 __callSiteLineNumber, /*!< The line number of the call site*/
          const U32 size /*!< The asserted size*/
      ) const;

    protected:

      // ----------------------------------------------------------------------
      // From port: fileDownlinkBufferSendOut 
      // ----------------------------------------------------------------------

      void assert_from_fileDownlinkBufferSendOut_size(
          const char *const __callSiteFileName, /*!< The name of the file containing the call site*/
          const U32 __callSiteLineNumber, /*!< The line number of the call site*/
          const U32 size /*!< The asserted size*/
      ) const;

    protected:

      // ----------------------------------------------------------------------
      // From port: fileUplinkBufferGet 
      // ----------------------------------------------------------------------

      void assert_from_fileUplinkBufferGet_size(
          const char *const __callSiteFileName, /*!< The name of the file containing the call site*/
          const U32 __callSiteLineNumber, /*!< The line number of the call site*/
          const U32 size /*!< The asserted size*/
      ) const;

  };

} // end namespace Zmq

#endif

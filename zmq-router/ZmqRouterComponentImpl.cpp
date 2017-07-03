// ====================================================================== 
// \title  ZmqRouterImpl.cpp
// \author tcanham
// \brief  cpp file for ZmqRouter component implementation class
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


#include <fprime-zmq/zmq-router/ZmqRouterComponentImpl.hpp>
#include "Fw/Types/BasicTypes.hpp"

namespace Zmq {

  // ----------------------------------------------------------------------
  // Construction, initialization, and destruction 
  // ----------------------------------------------------------------------

  ZmqRouterComponentImpl ::
#if FW_OBJECT_NAMES == 1
    ZmqRouterComponentImpl(
        const char *const compName
    ) :
      ZmqRouterComponentBase(compName)
#else
    ZmqRouterImpl(void)
#endif
  {

  }

  void ZmqRouterComponentImpl ::
    init(
        const NATIVE_INT_TYPE queueDepth,
        const NATIVE_INT_TYPE instance
    ) 
  {
    ZmqRouterComponentBase::init(queueDepth, instance);
  }

  ZmqRouterComponentImpl ::
    ~ZmqRouterComponentImpl(void)
  {

  }

  // ----------------------------------------------------------------------
  // Handler implementations for user-defined typed input ports
  // ----------------------------------------------------------------------

  void ZmqRouterComponentImpl ::
    Sched_handler(
        const NATIVE_INT_TYPE portNum,
        NATIVE_UINT_TYPE context
    )
  {
    // TODO
  }

} // end namespace Zmq

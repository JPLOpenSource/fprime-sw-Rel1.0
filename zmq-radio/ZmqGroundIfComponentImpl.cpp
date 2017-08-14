// ====================================================================== 
// \title  ZmqGroundIfComponentImpl.cpp
// \author dkooi
// \brief  cpp file for ZmqGroundIf implementation class.
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


#include <Fw/Types/BasicTypes.hpp>
#include <fprime-zmq/zmq-groundif/ZmqGroundIfComponentImpl.hpp>

#define DEBUG_PRINT(x,...) printf(x,##__VA_ARGS__)
//#define DEBUG_PRINT(x,...)

namespace Zmq{

	ZmqGroundIfComponentImpl ::
#if FW_OBJECT_NAMES == 1
	ZmqGroundIfComponentImpl(const char* name):
	ZmqGroundIfComponentBase(name)
#else
	ZmqGroundIfComponentImpl(void)
#endif
	,m_packetsSent(0)
	,m_context(0)
	,m_pubSocket(0)
	,m_subSocket(0)
	,m_cmdSocket(0)
	{

	}

	void ZmqGroundIfComponentImpl::init(NATIVE_INT_TYPE queueDepth, NATIVE_INT_TYPE instance){
	    ZmqGroundIfComponentBase::init(queueDepth, instance);
	}

	void ZmqGroundIfComponentImpl::open(const char* port){
	    strncpy(this->server_cmd_port, port, sizeof(port)); // Save command port

	    this->m_context = zmq_ctx_new();

	}

	ZmqGroundIfComponentImpl::~ZmqGroundIfComponentImpl(void){
	    // Object destruction
	    DEBUG_PRINT("Destruct\n");
	}

	void ZmqGroundIfComponentImpl::preamble(void){
	    // Setup Zmq
	    DEBUG_PRINT("Preamble\n");

	}

	void ZmqGroundIfComponentImpl::finalizer(void){
	    // Close Zmq
	    DEBUG_PRINT("Finalizer\n");
	}

	void ZmqGroundIfComponentImpl::downlinkPort_handler(
				    NATIVE_INT_TYPE portNum,
				    Fw::ComBuffer &data,
				    U32 context
				)
	{

	}

	void ZmqGroundIfComponentImpl::fileDownlinkBufferSendIn_handler(
	    NATIVE_INT_TYPE portNum, /*!< The port number*/
	    Fw::Buffer fwBuffer 
	)
	{


	}	


} // namespace Zmq 

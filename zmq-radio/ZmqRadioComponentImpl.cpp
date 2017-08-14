// ====================================================================== 
// \title  ZmqRadioComponentImpl.cpp
// \author dkooi
// \brief  cpp file for ZmqRadio implementation class.
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
#include <fprime-zmq/zmq-radio/ZmqRadioComponentImpl.hpp>

#define DEBUG_PRINT(x,...) printf(x,##__VA_ARGS__)
//#define DEBUG_PRINT(x,...)

namespace Zmq{

	ZmqRadioComponentImpl ::
#if FW_OBJECT_NAMES == 1
	ZmqRadioComponentImpl(const char* name): 
	ZmqRadioComponentBase(name)
#else
	ZmqRadioComponentImpl(void)
#endif
	,m_packetsSent(0)
	,m_context(0)
	,m_pubSocket(0)
	,m_subSocket(0)
	,m_cmdSocket(0)
	{

	}

	void ZmqRadioComponentImpl::init(NATIVE_INT_TYPE queueDepth, NATIVE_INT_TYPE instance){
	    ZmqRadioComponentBase::init(queueDepth, instance);
	}

	void ZmqRadioComponentImpl::open(const char* port, const char* zmqId){
	    strncpy(this->server_cmd_port, port, sizeof(port));// Save command port
	    strncpy(this->m_zmqId, zmqId, sizeof(zmqId));      // Save id for socket identification

	    this->connect();
	}

	void ZmqRadioComponetnImpl::connect(void){

	    // Setup Zmq
	    this->m_context   = zmq_ctx_new();

	    // Create sockets and set options 
	    this->m_cmdSocket = zmq_socket(this->m_context, ZMQ_DEALER);
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_RCVTO
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_IDENTITY, this->m_zmqId, sizeof(this->zmqId));
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_LINGER, ZMQ_RADIO_LINGER, sizeof(ZMQ_RADIO_LINGER));
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_RCVTIMEO, ZMQ_RADIO_RCVTIMEO, sizeof(ZMQ_RADIO_RCVTIMEO));
	    zmq_setsockopt(this->m_cmdSocket, ZMQ
	    
	    this->m_pubSocket = zmq_socket(this->m_context, ZMQ_DEALER);
	    zmq_setsockopt(this->m_pubSocket, ZMQ_IDENTITY, this->m_zmqId, sizeof(this->zmqId));

	    this->m_subSocket = zmq_socket(this->m_context, ZMQ_ROUTER); 
	    zmq_setsockopt(this->m_subSocket, ZMQ_IDENTITY, this->zmqId, sizeof(this->zmqId));


	}

	ZmqRadioComponentImpl::~ZmqRadioComponentImpl(void){
	    // Object destruction
	    DEBUG_PRINT("Destruct\n");
	}

	void ZmqRadioComponentImpl::preamble(void){ 
	    DEBUG_PRINT("Preamble\n");
	    
	}

	void ZmqRadioComponentImpl::finalizer(void){
	    // Close Zmq
	    DEBUG_PRINT("Finalizer\n");
	}

	void ZmqRadioComponentImpl::downlinkPort_handler(
				    NATIVE_INT_TYPE portNum,
				    Fw::ComBuffer &data,
				    U32 context
				)
	{

	}

	void ZmqRadioComponentImpl::fileDownlinkBufferSendIn_handler(
	    NATIVE_INT_TYPE portNum, /*!< The port number*/
	    Fw::Buffer fwBuffer 
	)
	{


	}	


} // namespace Zmq 

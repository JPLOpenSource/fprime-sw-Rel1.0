// ====================================================================== 
// \title  ZmqGroundIfComponentImpl.hpp
// \author dkooi
// \brief  hpp file for ZmqGroundIf implementation class.
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


#ifndef ZMQGROUNDIFIMPL_HPP_
#define ZMQGROUNDIFIMPL_HPP_

#include <fprime-zmq/zmq-groundif/ZmqGroundIfComponentAc.hpp>

namespace Zmq{

    class ZmqGroundIfComponentImpl : public ZmqGroundIfComponentBase{
	public:
#if FW_OBJECT_NAMES == 1
	    ZmqGroundIfComponentImpl(const char* name);
#else
	    ZmqGroundIfComponentImpl(void);
#endif
	    void init(NATIVE_INT_TYPE queueDepth, NATIVE_INT_TYPE instance);

	    virtual ~ZmqGroundIfComponentImpl();
	
	PROTECTED:
	PRIVATE:
	    void preamble(void);
	    void finalizer(void);

	    //! Handler for input port downlinkPort
	    //
	    void downlinkPort_handler(
		NATIVE_INT_TYPE portNum, /*!< The port number*/
		Fw::ComBuffer &data, /*!< Buffer containing packet data*/
		U32 context /*!< Call context value; meaning chosen by user*/
	    ); 


	    //! Handler for input port fileDownlinkBufferSendIn
	    //
	    void fileDownlinkBufferSendIn_handler(
		NATIVE_INT_TYPE portNum, /*!< The port number*/
		Fw::Buffer fwBuffer 
	    );

	    U32   m_packetsSent;
	    void* m_context; //!< zmq context
	    void* m_pubSocket; //!< zmq socket for outbound telemetry,events, and files
	    void* m_subSocket; //!< zmq socket for inbound commands and files
	    void* m_cmdSocket; //!< zmq socket for server registration


    };


} // namespace Zmq 




#endif // ZMQGROUNDIFIMPL_HPP_

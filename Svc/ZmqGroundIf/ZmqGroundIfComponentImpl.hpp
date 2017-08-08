


#ifndef ZMQGROUNDIFIMPL_HPP_
#define ZMQGROUNDIFIMPL_HPP_

#include <Svc/ZmqGroundIf/ZmqGroundIfComponentAc.hpp>

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


} // namespace Svc




#endif // ZMQGROUNDIFIMPL_HPP_

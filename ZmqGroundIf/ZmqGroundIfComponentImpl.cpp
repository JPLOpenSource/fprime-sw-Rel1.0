#include <Fw/Types/BasicTypes.hpp>
#include <fprime-zmq/ZmqGroundIf/ZmqGroundIfComponentImpl.hpp>

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

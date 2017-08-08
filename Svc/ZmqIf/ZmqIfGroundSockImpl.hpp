


#ifndef ZMQGROUNDIFIMPL_HPP_
#define ZMQGROUNDIFIMPL_HPP_

#include <Svc/ZmqIf/ZmqIfComponentAc.hpp>

namespace Svc{

    class ZmqGroundIfImpl : public ZmqIfComponentBase{
	public:
#if FW_OBJECT_NAMES == 1
	    ZmqGroundIfImpl(const char* name);
#else
	    ZmqGroundIfImpl();
#endif
	    void init(NATIVE_INT_TYPE queueDepth, NATIVE_INT_TYPE instance);

	    virtual ~ZmqGroundIfImpl();
	
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


    }


} // namespace Svc




#endif // ZMQGROUNDIFIMPL_HPP_

#ifndef REF_ZMQ_SOCKET_IMPL_HPP 
#define REF_ZMQ_SOCKET_IMPL_HPP 

#include <Svc/GndIf/GndIfComponentAc.hpp>
#include <Ref/zmq/include/zmq.h> 
#include <stdlib.h>

namespace Ref{

    class ZmqSocketIfImpl : public Svc::GndIfComponentBase {
	public:
#if FW_OBJECT_NAMES == 1
	    ZmqSocketIfImpl(const char* name);
#else
	    ZmqSocketIfImpl();
#endif
	    void init(NATIVE_INT_TYPE instance);
	    ~ZmqSocketIfImpl();

	    void startSocketTask(I32 priority, U32 port_number, const char* hostname);
	    void registerToServer(NATIVE_INT_TYPE instance);

	private:

	    void fileDownlinkBufferSendIn_handler( 
			    NATIVE_INT_TYPE portNum, /*!< The port number*/
			    Fw::Buffer fwBuffer
					        );

        static void socketReadTask(void* ptr);
	    void downlinkPort_handler(NATIVE_INT_TYPE portNum, 
			     Fw::ComBuffer &data, U32 context);

	    // ZMQ Components
	    void* m_cmdSocket;
	    void* m_pubSocket;
	    void* m_subSocket;
	    void* m_zmqContext;

	    const char* m_name;
	    const char* m_hostname;
	    U32 m_serverCommandPort;
	    U32 m_serverPublishPort;   // Server's outgoing port
	    U32 m_serverSubscribePort; // Server's ingoing port

	    Os::Task socketTask;

    };

} // Namespace Ref


#endif // REF_ZMQ_SOCKET_IMPL_HPP 


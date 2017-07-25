#include <Fw/Types/EightyCharString.hpp>
#include <Ref/ZmqSockIf/ZmqSocketIfImpl.hpp>



namespace Ref {

    /////////////////////////////////////////////////////////////////////
    // Helper functions
    /////////////////////////////////////////////////////////////////////
    namespace {

        NATIVE_INT_TYPE socketWrite(NATIVE_INT_TYPE fd, U8* buf, U32 size) {
            NATIVE_INT_TYPE total=0;
            while(size > 0) {

            }
            return total;
        }

        NATIVE_INT_TYPE socketRead(NATIVE_INT_TYPE fd, U8* buf, U32 size) {
            NATIVE_INT_TYPE total=0;
            while(size > 0) {

	    }
            return total;
        }
    }

    /////////////////////////////////////////////////////////////////////
    // Class implementation
    /////////////////////////////////////////////////////////////////////

    void ZmqSocketIfImpl::init(NATIVE_INT_TYPE instance) {
        GndIfComponentBase::init(instance);
    }
    
    ZmqSocketIfImpl::~ZmqSocketIfImpl() {
    }

#if FW_OBJECT_NAMES == 1
    ZmqSocketIfImpl::ZmqSocketIfImpl(const char* name):
	    GndIfComponentBase(name), 
	    m_cmdSocket(0),  m_pubSocket(0), m_subSocket(0), m_zmqContext(0),
	    m_name(name), m_hostname(NULL), m_serverCommandPort(0), m_serverPublishPort(0),
	    m_serverSubscribePort(0){
    }
#else
    ZmqSocketIfImpl::ZmqSocketIfImpl():
	    GndIfComponentBase(), 
	    m_cmdSocket(0), m_pubSocket(0), m_subSocket(0), m_zmqContext(0),
	    m_hostname(NULL), m_serverCommandPort(0), m_serverPublishPort(0),
	    m_serverSubscribePort(0){
    }
#endif

    void ZmqSocketIfImpl::startSocketTask(I32 priority, U32 port_number, const char* hostname){
		Fw::EightyCharString name("ScktRead");
		this->m_serverCommandPort = port_number;
		this->m_hostname = hostname;
		this->m_zmqContext = zmq_ctx_new();

        if (this->m_serverCommandPort == 0){
        	printf("Server Command Port is 0\n");
        	return;
        }
        else {
                // Try to open socket before spawning read task:
                log_WARNING_LO_NoConnectionToServer(port_number);
               	registerToServer(port_number);

                // Spawn read task:
        	Os::Task::TaskStatus stat = this->socketTask.start(name,0,
				            priority,10*1024,
				            ZmqSocketIfImpl::socketReadTask, (void*) this);
        	FW_ASSERT(Os::Task::TASK_OK == stat,static_cast<NATIVE_INT_TYPE>(stat));
        }
    }
 

    void ZmqSocketIfImpl::registerToServer(NATIVE_INT_TYPE port){
    	printf("Register to server\n");
		this->m_cmdSocket = zmq_socket(this->m_zmqContext, ZMQ_DEALER);

		// Set cmd socket ID
		U8 id[] = "F1";
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_IDENTITY, (const char*)id, strlen((const char*)id));

		// Connect to server's command port
		char endpoint[256];
		(void)snprintf(endpoint,256,"tcp://%s:%d",this->m_hostname, this->m_serverCommandPort);
		// null terminate
        endpoint[255] = 0;
        printf("Connecting command port: %s\n", endpoint);


		NATIVE_INT_TYPE stat = zmq_connect(this->m_cmdSocket,endpoint);
		if (-1 == stat) {
		  printf("ZMQBind Error\n");
		  return;
		}

		// Send server a registration command
		const U8 regMsgSize = 3;
		const char *reg_msgArr[regMsgSize] = {"REG", "FLIGHT", "ZMQ"};

		U8 i;
		for(i = 0; i < regMsgSize; i++){
			const char *msg = reg_msgArr[i];
			size_t len = strlen(msg);

			zmq_msg_t z_msg;
			int rc = zmq_msg_init_size(&z_msg, len); // Allocate msg_t 
			FW_ASSERT(rc == 0);

			memcpy(zmq_msg_data (&z_msg), msg, len); // Copy part into msg
			rc = zmq_msg_send(&z_msg, this->m_cmdSocket, ((i == regMsgSize-1) ? 0 : ZMQ_SNDMORE) ); // Set SNDMORE flag to zero if last message
		
			if (-1 == rc) {
				printf("ZMQ Message send error\n");
			}

			zmq_msg_close(&z_msg);
		}

		// Receive server response
		const U8 regRespSize = 3;
		U32 regStatus = 0;
		for(i = 0; i < regRespSize; i++){
			zmq_msg_t msg;
			zmq_msg_init(&msg);
			int size = zmq_msg_recv(&msg, this->m_cmdSocket, 0);

			switch(i){
				
				case 0:
					memcpy(&regStatus, zmq_msg_data(&msg), size);
					break;
				case 1:
					memcpy(&this->m_serverPublishPort, zmq_msg_data(&msg), size);
					break;
				case 2:
					memcpy(&this->m_serverSubscribePort, zmq_msg_data(&msg), size);
					break;
				
			}
			zmq_msg_close(&msg);
		}

		printf("S %04x P %04x S %04x\n", regStatus, this->m_serverPublishPort, this->m_serverSubscribePort);
		printf("S %d P %d S %d\n", regStatus, this->m_serverPublishPort, this->m_serverSubscribePort);
		if(regStatus != 0){
			this->log_ACTIVITY_HI_ConnectedToServer(this->m_serverCommandPort);
		}else{
			this->log_WARNING_LO_NoConnectionToServer(this->m_serverCommandPort);
		}
		

		// Create publish socket
		char endpoint[256];
		(void)snprintf(endpoint,256,"tcp://%s:%d",this->m_hostname, this->m_serverSubscribePort);
		// null terminate
        endpoint[255] = 0;
		this->m_pubSocket = zmq_socket(this->m_zmqContext, ZMQ_DEALER);
		zmq_setsockopt(this->m_pubSocket, ZMQ_IDENTITY, (const char*)id, strlen((const char*)id));
		NATIVE_INT_TYPE stat = zmq_connect(this->m_cmdSocket,endpoint);
		if (-1 == stat) {
		  printf("ZMQBind Error\n");
		  return;
		} 

		// Create subscribe socket
		(void)snprintf(endpoint, 256, "tcp://%s:%d", this->m_hostname, this->m_serverPublishPort);
		zmq_setsockopt(this->m_subSocket, ZMQ_IDENTITY, (const char*)id, strlen((const char*)id));
		NATIVE_INT_TYPE stat = zmq_connect(this->m_cmdSocket,endpoint);
		if (-1 == stat) {
		  printf("ZMQBind Error\n");
		  return;
		} 

    }

    void ZmqSocketIfImpl::socketReadTask(void* ptr){

    }

    void ZmqSocketIfImpl::fileDownlinkBufferSendIn_handler(
	    NATIVE_INT_TYPE portNum,
	    Fw::Buffer fwBuffer)
    {
	 
    }

    void ZmqSocketIfImpl::downlinkPort_handler(NATIVE_INT_TYPE portNum, Fw::ComBuffer &data,
					      U32 context) {
    }





} // Namespace Ref

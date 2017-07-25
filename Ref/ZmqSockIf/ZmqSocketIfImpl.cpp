#include <Fw/Com/ComPacket.hpp>
#include <Fw/Types/EightyCharString.hpp>
#include <Ref/ZmqSockIf/ZmqSocketIfImpl.hpp>



namespace Ref {

    /////////////////////////////////////////////////////////////////////
    // Helper functions
    /////////////////////////////////////////////////////////////////////
    namespace {

    	bool zmqError(const char* from) {
			switch (zmq_errno()) {
				case EAGAIN:
				    printf("%s: ZMQ EAGAIN", from);
				    return true;
				case EFSM:
				     printf("%s: ZMQ EFSM", from);
				     return true;
				case ETERM:
					printf("%s: ZMQ terminate\n",from);
					return true;
				case ENOTSOCK:
					printf("%s: ZMQ ENOTSOCK\n",from);
					return true;
				case EINTR:
					printf("%s: ZMQ EINTR\n",from);
					return false;
				case EFAULT:
					printf("%s: ZMQ EFAULT\n",from);
				default:
					printf("%s: ZMQ error: %s\n",from,zmq_strerror(zmq_errno()));
					return true;
			}
		}

        NATIVE_INT_TYPE socketWrite(void* zmqSocket, U8* buf, NATIVE_INT_TYPE size) {
            NATIVE_INT_TYPE total=0;
            while(size > 0) {

            }
            return total;
        }

        NATIVE_INT_TYPE zmqSocketRead(void* zmqSocket, U8* buf, NATIVE_INT_TYPE size) {
            NATIVE_INT_TYPE total=0;

            // Ignore the zmq identifier
			zmq_msg_t zmqID;
	    	zmq_msg_init(&zmqID);
	    	zmq_msg_recv(&zmqID, zmqSocket, 0);
	    	zmq_msg_close(&zmqID);

	    	// Receive FPrime packet
	    	zmq_msg_t fPrimePacket;
	    	zmq_msg_init(&fPrimePacket);
	    	total = zmq_msg_recv(&fPrimePacket, zmqSocket, 0);

	    	if(total == -1){
				zmqError("zmqSocketRead");
	    	}

	    	memcpy(buf, zmq_msg_data(&fPrimePacket), total);
	    	zmq_msg_close(&fPrimePacket);

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
        	Os::Task::TaskStatus stat = this->socketTask.start(name,0, priority,10*1024, ZmqSocketIfImpl::socketReadTask, (void*) this);
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
		(void)snprintf(endpoint,256,"tcp://%s:%d",this->m_hostname, this->m_serverSubscribePort);
		// null terminate
        endpoint[255] = 0;
		this->m_pubSocket = zmq_socket(this->m_zmqContext, ZMQ_DEALER);
		zmq_setsockopt(this->m_pubSocket, ZMQ_IDENTITY, (const char*)id, strlen((const char*)id));
		stat = zmq_connect(this->m_pubSocket,endpoint);
		if (-1 == stat) {
		  printf("ZMQBind Error\n");
		  return;
		} 

		// Create subscribe socket
		(void)snprintf(endpoint, 256, "tcp://%s:%d", this->m_hostname, this->m_serverPublishPort);
		this->m_subSocket = zmq_socket(this->m_zmqContext, ZMQ_ROUTER);
		zmq_setsockopt(this->m_subSocket, ZMQ_IDENTITY, (const char*)id, strlen((const char*)id));
		stat = zmq_connect(this->m_subSocket,endpoint);
		if (-1 == stat) {
		  printf("ZMQBind Error\n");
		  return;
		} 

    }

    void ZmqSocketIfImpl::socketReadTask(void* ptr){
    	printf("socketReadTask\n");
    	fflush(stderr);

    	// cast pointer to component type
    	ZmqSocketIfImpl* comp = (ZmqSocketIfImpl*) ptr;

    	while(1){
	        U32 packetDelimiter;
	        U32 packetSize;
	        U32 packetDesc;
	        U8 buf[FW_COM_BUFFER_MAX_SIZE];
	        U16 buf_ptr = 0;


    		// Read incoming zmq message
    		U32 msgSize = 0;
			msgSize = zmqSocketRead(comp->m_subSocket, buf, (NATIVE_INT_TYPE)FW_COM_BUFFER_MAX_SIZE);

			// Extract packet delimiter
			packetDelimiter = *(U32*)(buf+buf_ptr);
			packetDelimiter = ntohl(packetDelimiter);

            // correct for network order
            packetDelimiter = ntohl(packetDelimiter);
            printf("Packet delimiter: 0x%04x\n",packetDelimiter);

            // if magic number to quit, exit loop
            if (packetDelimiter == 0xA5A5A5A5) {
                (void) printf("packetDelimiter = 0x%x\n", packetDelimiter);
                //break;
            } else if (packetDelimiter != 0x5A5A5A5A) {
                (void) printf("Unexpected delimiter 0x%08X\n",packetDelimiter);
                // just keep reading until a delimiter is found
                continue;
            }

            // Increment buffer pointer
            buf_ptr += sizeof(packetDelimiter);


            // Extract FPrime packet size
            packetSize = *(U32*)(buf + buf_ptr);
            packetSize = ntohl(packetSize);

            printf("Packet Size: 0x%04x\n", packetSize);

            // Increment buffer pointer
            buf_ptr += sizeof(packetSize);


            // Extract FPrime packet description
            packetDesc = *(U32*)(buf + buf_ptr);
            packetDesc = ntohl(packetDesc);

            // Increment buffer pointer
            buf_ptr += sizeof(packetDesc);

            switch(packetDesc) {

                case Fw::ComPacket::FW_PACKET_COMMAND:
                {
                	U8 cmdPacket[FW_COM_BUFFER_MAX_SIZE];

                    // check size of command
                    if (packetSize > FW_COM_BUFFER_MAX_SIZE) {
                        (void) printf("Packet to large! :%d\n",packetSize);
                        // might as well wait for the next packet
                        break;
                    }


                    /*
                    cmdBuffer[3] = packetDesc & 0xff;
                    cmdBuffer[2] = (packetDesc & 0xff00) >> 8;
                    cmdBuffer[1] = (packetDesc & 0xff0000) >> 16;
                    cmdBuffer[0] = (packetDesc & 0xff000000) >> 24;
					*/
		    		
		    		// Add description
                    packetDesc = ntohl(packetDesc); // Is this the same as above?
                    memcpy(cmdPacket, &packetDesc, sizeof(packetDesc));

		    		// Add command data [ Size of cmd data is packet size - packetDesc size ]
                    memcpy(cmdPacket + sizeof(packetDesc), buf + buf_ptr, packetSize - sizeof(packetDesc));


                    if (comp->isConnected_uplinkPort_OutputPort(0)) {
                         Fw::ComBuffer cmdBuffer(cmdPacket, packetSize);
                         comp->uplinkPort_out(0,cmdBuffer,0);
                    }
                    break;
                }
            

                case Fw::ComPacket::FW_PACKET_FILE:
                {
                
                    // Get Buffer
                    Fw::Buffer packet_buffer = comp->fileUplinkBufferGet_out(0, packetSize - sizeof(packetDesc));
                    U8* data_ptr = (U8*)packet_buffer.getdata();

					/*
                    bytesRead = socketRead(comp->m_socketFd, data_ptr, packetSize - sizeof(packetDesc));
                    if (-1 == bytesRead) {
                        (void) printf("Size read error: %s\n",strerror(errno));
                        break;
                    }

                    // for(uint32_t i =0; i < bytesRead; i++){
                    //     (void) printf("IN_DATA:%02x\n", data_ptr[i]);
                    // }
					*/

					// Read file packet minus description. Same as above?
                    memcpy(data_ptr, buf + buf_ptr, packetSize - sizeof(packetDesc));

                    if (comp->isConnected_fileUplinkBufferSendOut_OutputPort(0)) {
                        comp->fileUplinkBufferSendOut_out(0, packet_buffer);
                    }

                    break;
                }

                default:
                    FW_ASSERT(0);
            }



        } // while not done with packets

        // Reconnection scheme here?


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

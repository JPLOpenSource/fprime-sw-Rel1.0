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



	/* Helper Functions */
	namespace { 

		bool zmqError(const char* from) {
			switch (zmq_errno()) {
				case EAGAIN:
				    printf("%s: ZMQ EAGAIN\n", from);
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
					return false;
				case ENOMEM:
					printf("%s: ZMQ ENOMEM\n", from);
					return false;
				default:
					printf("%s: ZMQ error: %s\n",from,zmq_strerror(zmq_errno()));
					return true;
			}
		}



        NATIVE_INT_TYPE zmqSocketWriteComBuffer(void* zmqSocket, Fw::ComBuffer &data) {
        	//printf("Data Size: 0x%04x\n", data.getBuffLength());
        	//printf("Data Desc: 0x%04x\n", *(U32*)data.getBuffAddr());


        	U32 data_net_size = htonl(data.getBuffLength());
        	U8 buf[sizeof(data_net_size) + data.getBuffLength()];
        	memcpy(buf, &data_net_size, sizeof(data_net_size));
        	memcpy(buf + sizeof(data_net_size),  (U8*)data.getBuffAddr(), data.getBuffLength());

        	zmq_msg_t fPrimePacket;
        	zmq_msg_init_size(&fPrimePacket, sizeof(buf));
        	memcpy(zmq_msg_data(&fPrimePacket), buf, sizeof(buf));

        	int rc = zmq_msg_send(&fPrimePacket, zmqSocket, 0);
        	zmq_msg_close(&fPrimePacket);
        	if(rc == -1){
        		zmqError("zmqSocketWriteComBuffer\n");
        	}
        	return 1;

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

	} // namespace



#if FW_OBJECT_NAMES == 1
	ZmqRadioComponentImpl :: ZmqRadioComponentImpl(const char* name): ZmqRadioComponentBase(name)
#else
	ZmqRadioComponentImpl :: ZmqRadioComponentImpl(void)
#endif
	,m_packetsSent(0)
	,m_context(0)
	,m_pubSocket(0)
	,m_subSocket(0)
	,m_cmdSocket(0)
	,m_state(0)
	{
		this->m_state = State(this);
	}

	void ZmqRadioComponentImpl::init(NATIVE_INT_TYPE queueDepth, NATIVE_INT_TYPE instance){
	    ZmqRadioComponentBase::init(queueDepth, instance);
	}

	void ZmqRadioComponentImpl::open(const char* hostname, U32 port, const char* zmqId){
		DEBUG_PRINT("Opening Connection\n");

	    strncpy(this->m_hostname, hostname, strlen(hostname)); // Save hostname
	    this->m_hostname[strlen(hostname)] = 0; // Null terminate

	    strncpy(this->m_zmqId, zmqId, strlen(zmqId));  // Save id for socket identification	
	    this->m_zmqId[strlen(zmqId)] = 0; // Null terminate

	    this->m_serverCmdPort = port; // Save server command port 
	
	    this->connect();
	}

	void ZmqRadioComponentImpl::connect(void){
	    int rc = 0; // Return code

	    // Setup context
	    this->m_context   = zmq_ctx_new();
	    if(not this->m_context){
	    	zmqError("ZmqRadioComponentImpl::connect Error creating context.");
	    	Fw::LogStringArg errArg(zmq_strerror(zmq_errno()));
	    	this->log_WARNING_HI_ZR_ContextError(errArg);
	    	this->m_state.transitionDisconnected();
	    	return;
	    }

	    // Create sockets and set options 
	    this->m_cmdSocket = zmq_socket(this->m_context, ZMQ_DEALER);
	    if(not this->m_cmdSocket){ 
			zmqError("ZmqRadioComponentImpl::connect Error creating cmd socket");
			Fw::LogStringArg errArg(zmq_strerror(zmq_errno()));
			this->log_WARNING_HI_ZR_SocketError(errArg);
			this->m_state.transitionDisconnected();
			return;
	    }	
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_IDENTITY, &this->m_zmqId, strlen(this->m_zmqId));
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_LINGER, &ZMQ_RADIO_LINGER, sizeof(ZMQ_RADIO_LINGER));
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_RCVTIMEO, &ZMQ_RADIO_RCVTIMEO, sizeof(ZMQ_RADIO_RCVTIMEO));
	    zmq_setsockopt(this->m_cmdSocket, ZMQ_SNDTIMEO, &ZMQ_RADIO_SNDTIMEO, sizeof(ZMQ_RADIO_SNDTIMEO));
	    
	    this->m_pubSocket = zmq_socket(this->m_context, ZMQ_DEALER);
	    if(not this->m_pubSocket){ 
			zmqError("ZmqRadioComponentImpl::connect Error creating pub socket");
			Fw::LogStringArg errArg(zmq_strerror(zmq_errno()));
			this->log_WARNING_HI_ZR_SocketError(errArg);
			this->m_state.transitionDisconnected();
			return;
	    }
	    zmq_setsockopt(this->m_pubSocket, ZMQ_IDENTITY, &this->m_zmqId, strlen(this->m_zmqId));
	    zmq_setsockopt(this->m_pubSocket, ZMQ_LINGER, &ZMQ_RADIO_LINGER, sizeof(ZMQ_RADIO_LINGER));
	    zmq_setsockopt(this->m_pubSocket, ZMQ_RCVTIMEO, &ZMQ_RADIO_RCVTIMEO, sizeof(ZMQ_RADIO_RCVTIMEO));
	    zmq_setsockopt(this->m_pubSocket, ZMQ_SNDTIMEO, &ZMQ_RADIO_SNDTIMEO, sizeof(ZMQ_RADIO_SNDTIMEO));


	    this->m_subSocket = zmq_socket(this->m_context, ZMQ_ROUTER); 
	    if(not this->m_subSocket){ 
			zmqError("ZmqRadioComponentImpl::connect Error creating sub socket");
			Fw::LogStringArg errArg(zmq_strerror(zmq_errno()));
			this->log_WARNING_HI_ZR_SocketError(errArg);
			this->m_state.transitionDisconnected();
			return;
	    }
	    zmq_setsockopt(this->m_subSocket, ZMQ_IDENTITY, &this->m_zmqId, strlen(this->m_zmqId));
	    zmq_setsockopt(this->m_subSocket, ZMQ_LINGER, &ZMQ_RADIO_LINGER, sizeof(ZMQ_RADIO_LINGER));
	    zmq_setsockopt(this->m_subSocket, ZMQ_RCVTIMEO, &ZMQ_RADIO_RCVTIMEO, sizeof(ZMQ_RADIO_RCVTIMEO));
	    zmq_setsockopt(this->m_subSocket, ZMQ_SNDTIMEO, &ZMQ_RADIO_SNDTIMEO, sizeof(ZMQ_RADIO_SNDTIMEO));

	    // Attempt registration
	    rc = this->registerToServer();
	    if(rc == -1){
	    	this->m_state.transitionDisconnected();
	    }else{
	    	this->m_state.transitionConnected();
	    }

	    return;
	}

	NATIVE_INT_TYPE ZmqRadioComponentImpl::registerToServer(){
		DEBUG_PRINT("Registering to server\n");

		NATIVE_INT_TYPE rc = 0; //Return code
		char endpoint[ZMQ_RADIO_ENDPOINT_NAME_SIZE];

		// Connect cmd socket to server
		(void)snprintf(endpoint,ZMQ_RADIO_ENDPOINT_NAME_SIZE,"tcp://%s:%d",this->m_hostname, this->m_serverCmdPort);
		zmq_connect(this->m_cmdSocket, endpoint);

		DEBUG_PRINT("SERVER: %s\n", endpoint);

		// Send server a registration command
		const U8 regMsgSize = ZMQ_RADIO_REG_MSG_SIZE;
		const char *reg_msgArr[regMsgSize] = {"REG", "FLIGHT", "ZMQ"};

		U8 i;
		for(i = 0; i < regMsgSize; i++){
			const char *msg = reg_msgArr[i];
			size_t len = strlen(msg);

			zmq_msg_t z_msg; // Declare zmq msg struct
			int rc = zmq_msg_init_size(&z_msg, len); // Allocate msg_t 
			FW_ASSERT(rc == 0);

			memcpy(zmq_msg_data (&z_msg), msg, len); // Copy part into msg
			rc = zmq_msg_send(&z_msg, this->m_cmdSocket, ((i == regMsgSize-1) ? 0 : ZMQ_SNDMORE) ); // Set SNDMORE flag to zero if last message
		
			if (-1 == rc) {
				zmqError("ZmqRadioComponentImpl::registerToServer Error sending registration message."); 
				return -1;
			}

			zmq_msg_close(&z_msg);
		}	     
		DEBUG_PRINT("Sent reg msg\n");


		// Receive server response
		const U8 regRespSize = ZMQ_RADIO_REG_RESP_MSG_SIZE; // How many response messages to expect
		U32 regStatus = 0;
		for(i = 0; i < regRespSize; i++){
			zmq_msg_t msg;
			zmq_msg_init(&msg);
			int size = zmq_msg_recv(&msg, this->m_cmdSocket, 0);
			if(size == -1){
				zmqError("ZmqRadioComponentImpl::registerToServer Error receiving server registration response.");
				return -1;
			}

			// Receive the various msg parts
			switch(i){
				case 0:
					memcpy(&regStatus, zmq_msg_data(&msg), size);
					DEBUG_PRINT("status: %d\n", regStatus);
					break;
				case 1:
					memcpy(&this->m_serverPubPort, zmq_msg_data(&msg), size);
					DEBUG_PRINT("serverPubPort: %d\n", this->m_serverPubPort);
					break;
				case 2:
					memcpy(&this->m_serverSubPort, zmq_msg_data(&msg), size);
					DEBUG_PRINT("serverSubPort: %d\n", this->m_serverSubPort);
					break;
				
			}
			zmq_msg_close(&msg);
		}

		// Check registration status
		if(regStatus != 0){
			
		}else{
			
		}
		

		// Create publish socket
		(void)snprintf(endpoint,ZMQ_RADIO_ENDPOINT_NAME_SIZE,"tcp://%s:%d",this->m_hostname, this->m_serverSubPort);
		// null terminate
        endpoint[ZMQ_RADIO_ENDPOINT_NAME_SIZE-1] = 0;
		rc = zmq_connect(this->m_pubSocket,endpoint);
		if (-1 == rc) {
			zmqError("ZmqRadioComponentImpl::registerToServer Error connecting publish socket.");
			return -1;
		} 

		// Create subscribe socket
		(void)snprintf(endpoint, ZMQ_RADIO_ENDPOINT_NAME_SIZE, "tcp://%s:%d", this->m_hostname, this->m_serverPubPort);
		rc = zmq_connect(this->m_subSocket,endpoint);
		if (-1 == rc) {
		  	zmqError("ZmqRadioComponentImpl::registerToServer Error connecting subscribe socket.");
		  return -1;
		} 

	    return 0;

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

	void ZmqRadioComponentImpl::reconnect_handler(NATIVE_INT_TYPE portNum, NATIVE_UINT_TYPE context ){
		switch(this->m_state.get()){

			case State::ZMQ_RADIO_CONNECTED_STATE:
				// We are connected, do nothing
				break;
			case State::ZMQ_RADIO_DISCONNECTED_STATE:
				// We are disconnected, attempt reconnection
				this->connect();
				break;

		}
	}


	void ZmqRadioComponentImpl::downlinkPort_handler(
				    NATIVE_INT_TYPE portNum,
				    Fw::ComBuffer &data,
				    U32 context
	)
	{
		switch(this->m_state.get()){

			case State::ZMQ_RADIO_CONNECTED_STATE:
				zmqSocketWriteComBuffer(this->m_pubSocket, data);
				break;
			case State::ZMQ_RADIO_DISCONNECTED_STATE:
				// Drop packets
				break;


		}
		

	}

	void ZmqRadioComponentImpl::fileDownlinkBufferSendIn_handler(
	    NATIVE_INT_TYPE portNum, /*!< The port number*/
	    Fw::Buffer fwBuffer 
	)
	{
		switch(this->m_state.get()){

			case State::ZMQ_RADIO_CONNECTED_STATE:
				// Write files down
				break;
			case State::ZMQ_RADIO_DISCONNECTED_STATE:
				// Drop packets

				break;

		}
		


	}

	/* State Class Implementation */	
	ZmqRadioComponentImpl::State::State(ZmqRadioComponentImpl* parent):
		state(ZMQ_RADIO_DISCONNECTED_STATE)
	{
		this->m_parent = parent;
	}

	U8 ZmqRadioComponentImpl::State::get(){
		return this->state;
	}

	void ZmqRadioComponentImpl::State::transitionConnected(){
		switch(this->state){
			case ZMQ_RADIO_CONNECTED_STATE:
				// Already connected
				break;
			case ZMQ_RADIO_DISCONNECTED_STATE:
				this->state = ZMQ_RADIO_CONNECTED_STATE;
				this->m_parent->log_ACTIVITY_HI_ZR_Connection();
				break;


		}

	}

	void ZmqRadioComponentImpl::State::transitionDisconnected(){
		// Release ZMQ resources to prepare for reconnect attempts
		zmq_close(this->m_parent->m_pubSocket);
		zmq_close(this->m_parent->m_subSocket);
		zmq_close(this->m_parent->m_cmdSocket);
		zmq_term(this->m_parent->m_context);


		switch(this->state){
			case ZMQ_RADIO_CONNECTED_STATE:

				this->m_parent->log_WARNING_HI_ZR_Disconnection();
				break;
			case ZMQ_RADIO_DISCONNECTED_STATE:
				break;

		}


	}




} // namespace Zmq 
